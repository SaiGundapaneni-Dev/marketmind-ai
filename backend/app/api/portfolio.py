import os
import tempfile
import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.investment_context_schema import (
    InvestmentContextResponse,
)
from app.schemas.portfolio_history_schema import (
    PortfolioChangesResponse,
    PortfolioContributorsResponse,
    PortfolioPerformanceResponse,
    PortfolioSnapshotResponse,
)
from app.schemas.portfolio_import_schema import (
    PortfolioImportConfirmRequest,
    PortfolioImportConfirmResponse,
    PortfolioImportPreviewResponse,
)
from app.schemas.portfolio_intelligence_schema import (
    PortfolioIntelligenceResponse,
)
from app.schemas.portfolio_schema import (
    HoldingCreate,
    HoldingUpdate,
    PortfolioResponse,
)
from app.schemas.portfolio_score_schema import (
    PortfolioScoreResponse,
)
from app.services.investment_context_service import (
    InvestmentContextService,
)
from app.services.portfolio_history_service import (
    PortfolioHistoryService,
)
from app.services.portfolio_import_confirm_service import (
    PortfolioImportConfirmService,
)
from app.services.portfolio_import_service import (
    PortfolioImportService,
)
from app.services.portfolio_intelligence_service import (
    PortfolioIntelligenceService,
)
from app.services.portfolio_score_service import (
    PortfolioScoreService,
)
from app.services.portfolio_service import PortfolioService


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get(
    "/context",
    response_model=InvestmentContextResponse,
)
def get_investment_context(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InvestmentContextService.build(
        db,
        current_user.id,
    )


@router.get(
    "/",
    response_model=PortfolioResponse,
)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioService.calculate(
        db,
        current_user.id,
    )


@router.post(
    "/holdings",
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    holding: HoldingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_holding = PortfolioService.create_holding(
        db,
        current_user.id,
        holding,
    )

    return {
        "message": "Holding created successfully",
        "holding_id": new_holding.id,
        "symbol": new_holding.symbol,
    }


@router.post(
    "/import",
    response_model=PortfolioImportPreviewResponse,
)
async def preview_portfolio_import(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Upload, parse, validate, and preview a portfolio CSV.

    No database records are created during this endpoint.
    """

    original_name = (
        file.filename
        or "portfolio.csv"
    )

    extension = os.path.splitext(
        original_name
    )[1].lower()

    if extension != ".csv":
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Only CSV files are currently supported."
            ),
        )

    temporary_path: str | None = None

    try:
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="The uploaded file is empty.",
            )

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            delete=False,
        ) as temporary_file:
            temporary_file.write(file_content)
            temporary_path = temporary_file.name

        result = PortfolioImportService.preview(
            temporary_path,
        )

        result.file_name = original_name

        return result

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    finally:
        await file.close()

        if (
            temporary_path
            and os.path.exists(temporary_path)
        ):
            os.remove(temporary_path)

logger = logging.getLogger(__name__)

@router.post(
    "/import/confirm",
    response_model=PortfolioImportConfirmResponse,
    status_code=status.HTTP_201_CREATED,
)
def confirm_portfolio_import(
    request: PortfolioImportConfirmRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Save reviewed holdings returned by the import-preview endpoint.
    """

    try:
        return PortfolioImportConfirmService.confirm(
            db=db,
            request=request,
            user_id=current_user.id,
        )

    except ValueError as exc:
        logger.exception(
            "Portfolio import validation failed."
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected portfolio import confirmation error."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"{type(exc).__name__}: {str(exc)}"
            ),
        ) from exc


@router.get(
    "/holdings/{holding_id}",
)
def get_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    holding = PortfolioService.get_holding_by_id(
        db,
        current_user.id,
        holding_id,
    )

    if holding is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Holding not found",
        )

    return holding


@router.put(
    "/holdings/{holding_id}",
)
def update_holding(
    holding_id: int,
    holding: HoldingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_holding = (
        PortfolioService.update_holding(
            db,
            current_user.id,
            holding_id,
            holding,
        )
    )

    if updated_holding is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Holding not found",
        )

    return {
        "message": "Holding updated successfully",
        "holding_id": updated_holding.id,
        "symbol": updated_holding.symbol,
    }


@router.delete(
    "/holdings/{holding_id}",
    status_code=status.HTTP_200_OK,
)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted_holding = (
        PortfolioService.delete_holding(
            db,
            current_user.id,
            holding_id,
        )
    )

    if deleted_holding is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Holding not found",
        )

    return {
        "message": "Holding deleted successfully",
        "holding_id": holding_id,
    }


@router.post(
    "/snapshot",
    response_model=PortfolioSnapshotResponse,
)
def create_portfolio_snapshot(
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        PortfolioHistoryService
        .create_daily_snapshot(
            db,
            current_user.id,
            force=force,
        )
    )


@router.get(
    "/history",
    response_model=list[
        PortfolioSnapshotResponse
    ],
)
def get_portfolio_history(
    limit: int = Query(
        default=365,
        ge=1,
        le=2000,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_history(
        db,
        current_user.id,
        limit,
    )


@router.get(
    "/performance",
    response_model=PortfolioPerformanceResponse,
)
def get_portfolio_performance(
    limit: int = Query(
        default=365,
        ge=1,
        le=2000,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_performance(
        db,
        current_user.id,
        limit,
    )


@router.get(
    "/contributors",
    response_model=PortfolioContributorsResponse,
)
def get_portfolio_contributors(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_contributors(
        db,
        current_user.id,
    )


@router.get(
    "/changes",
    response_model=PortfolioChangesResponse,
)
def get_portfolio_changes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_changes(
        db,
        current_user.id,
    )


@router.get(
    "/score",
    response_model=PortfolioScoreResponse,
)
def get_portfolio_score(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioScoreService.generate(
        db,
        current_user.id,
    )


@router.get(
    "/intelligence",
    response_model=PortfolioIntelligenceResponse,
)
def get_portfolio_intelligence(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        PortfolioIntelligenceService.generate(
            db,
            current_user.id,
        )
    )