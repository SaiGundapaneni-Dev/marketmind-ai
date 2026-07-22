import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_dependencies import get_current_user
from app.schemas.investment_thesis_schema import (
    InvestmentThesisCreate,
    InvestmentThesisResponse,
    InvestmentThesisUpdate,
)
from app.services.investment_thesis_service import (
    InvestmentThesisService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/portfolio/thesis",
    tags=["Investment Thesis"],
)


@router.post(
    "",
    response_model=InvestmentThesisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_investment_thesis(
    thesis_data: InvestmentThesisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> InvestmentThesisResponse:
    """
    Create an investment thesis for one of the authenticated
    user's portfolio holdings.
    """

    try:
        return InvestmentThesisService.create_thesis(
            db=db,
            thesis_data=thesis_data,
            user_id=current_user.id,
        )

    except ValueError as exc:
        message = str(exc)

        if "already exists" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error while creating investment thesis."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The investment thesis could not be created.",
        ) from exc


@router.get(
    "/{holding_id}",
    response_model=InvestmentThesisResponse,
)
def get_investment_thesis(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> InvestmentThesisResponse:
    """
    Retrieve the investment thesis associated with a holding.
    """

    try:
        return InvestmentThesisService.get_thesis(
            db=db,
            holding_id=holding_id,
            user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error while retrieving investment thesis."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The investment thesis could not be retrieved.",
        ) from exc


@router.put(
    "/{holding_id}",
    response_model=InvestmentThesisResponse,
)
def update_investment_thesis(
    holding_id: int,
    thesis_data: InvestmentThesisUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> InvestmentThesisResponse:
    """
    Update an existing investment thesis.
    """

    try:
        return InvestmentThesisService.update_thesis(
            db=db,
            holding_id=holding_id,
            thesis_data=thesis_data,
            user_id=current_user.id,
        )

    except ValueError as exc:
        message = str(exc)

        if "at least one field" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error while updating investment thesis."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The investment thesis could not be updated.",
        ) from exc


@router.delete(
    "/{holding_id}",
    status_code=status.HTTP_200_OK,
)
def delete_investment_thesis(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict[str, str]:
    """
    Delete an investment thesis associated with a holding.
    """

    try:
        InvestmentThesisService.delete_thesis(
            db=db,
            holding_id=holding_id,
            user_id=current_user.id,
        )

        return {
            "message": "Investment thesis deleted successfully."
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error while deleting investment thesis."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The investment thesis could not be deleted.",
        ) from exc