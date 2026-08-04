from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DailyBriefItem(BaseModel):
    category: str
    severity: Literal[
        "high",
        "medium",
        "low",
        "info",
    ]
    title: str
    message: str
    suggested_action: str | None = None
    symbols: list[str] = []


class DailyBriefPortfolioSnapshot(BaseModel):
    total_value: float
    total_profit: float
    total_return_percent: float
    holdings_count: int
    health_score: float
    health_rating: str
    concentration_risk: str


class DailyBriefResponse(BaseModel):
    generated_at: datetime
    greeting: str
    headline: str
    action: Literal[
        "HOLD",
        "MONITOR",
        "REVIEW",
    ]
    action_reason: str
    portfolio_snapshot: DailyBriefPortfolioSnapshot
    priorities: list[DailyBriefItem]
    positive_signals: list[str]
    risks: list[str]
    recent_changes: list[str]
    holdings_to_watch: list[str]
    recommended_questions: list[str]
    disclaimer: str
