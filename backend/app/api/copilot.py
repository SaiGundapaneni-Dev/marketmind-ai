from fastapi import APIRouter
from pydantic import BaseModel

from app.services.copilot_service import CopilotService


router = APIRouter(
    prefix="/copilot",
    tags=["AI Copilot"],
)


class CopilotRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_copilot(request: CopilotRequest):
    return CopilotService.answer(request.question)