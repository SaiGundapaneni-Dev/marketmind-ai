from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/copilot",
    tags=["AI Copilot"],
)


class CopilotRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_copilot(request: CopilotRequest):
    return {
        "question": request.question,
        "answer": "MarketMind Copilot endpoint is working.",
        "status": "success",
    }