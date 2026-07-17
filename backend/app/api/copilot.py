from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.services.copilot_service import CopilotService

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


class CopilotRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_copilot(
    request: CopilotRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CopilotService.answer(
        question=request.question,
        db=db,
        user_id=current_user.id,
    )
