from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AICoachItem(BaseModel):
    severity: Literal["high", "medium", "low", "positive"]
    category: str
    title: str
    message: str
    suggested_action: str
    symbol: str | None = None


class AICoachResponse(BaseModel):
    generated_at: datetime
    greeting: str
    portfolio_status: str
    health_score: float
    health_rating: str
    headline: str
    priorities: list[AICoachItem] = Field(default_factory=list)
    positive_highlights: list[AICoachItem] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    estimated_review_minutes: int
    no_action_required: bool
    disclaimer: str
