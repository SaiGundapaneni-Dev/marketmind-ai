from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class WatchtowerAlert(BaseModel):
    symbol: str
    company_name: str | None = None
    source_type: Literal["portfolio", "watchlist", "both"]
    severity: Literal[
        "critical",
        "important",
        "informational",
        "noise",
    ]
    event_type: str
    title: str
    summary: str | None = None
    publisher: str | None = None
    link: str | None = None
    published_at: str | None = None
    sentiment: str
    relevance_score: float
    materiality_score: float
    portfolio_owned: bool
    portfolio_allocation_percent: float
    thesis_exists: bool
    thesis_impact: Literal[
        "supports",
        "contradicts",
        "neutral",
        "unknown",
    ]
    why_it_matters: str
    suggested_action: str


class WatchtowerSummary(BaseModel):
    generated_at: datetime
    monitored_symbols: int
    critical_count: int
    important_count: int
    informational_count: int
    noise_count: int
    silence_filter_active: bool
    silence_message: str
    alerts: list[WatchtowerAlert] = Field(default_factory=list)
    disclaimer: str
