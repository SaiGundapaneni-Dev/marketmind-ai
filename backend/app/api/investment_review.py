import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.investment_review_schema import (
    InvestmentReviewResponse,
)
from app.services.investment_review_service import (
    InvestmentReviewService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/portfolio/thesis/review",
    tags=["Investment Review"],
)


@router.get(
    "/{holding_id}",
    response_model=InvestmentReviewResponse,
)
def review_investment(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> InvestmentReviewResponse:
    try:
        return InvestmentReviewService.review_by_holding(
            db=db,
            user_id=current_user.id,
            holding_id=holding_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error while reviewing investment."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The investment review could not be generated."
            ),
        ) from exc
