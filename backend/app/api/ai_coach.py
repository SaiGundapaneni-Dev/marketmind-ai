import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.ai_coach_schema import (
    AICoachResponse,
)
from app.services.ai_coach_service import (
    AICoachService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/portfolio/coach",
    tags=["AI Portfolio Coach"],
)


@router.get(
    "",
    response_model=AICoachResponse,
)
def get_ai_portfolio_coach(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return AICoachService.generate(
            db,
            current_user.id,
        )

    except Exception as exc:
        logger.exception(
            "AI Portfolio Coach generation failed."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The AI Portfolio Coach could not "
                "be generated."
            ),
        ) from exc
