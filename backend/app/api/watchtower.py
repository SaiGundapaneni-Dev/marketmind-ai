from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.watchtower_schema import (
    WatchtowerSummary,
)
from app.services.watchtower_service import (
    WatchtowerService,
)


router = APIRouter(
    prefix="/watchtower",
    tags=["AI Watchtower"],
)


@router.get(
    "",
    response_model=WatchtowerSummary,
)
def get_watchtower(
    include_noise: bool = Query(
        default=False,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return WatchtowerService.generate(
        db=db,
        user_id=current_user.id,
        include_noise=include_noise,
    )
