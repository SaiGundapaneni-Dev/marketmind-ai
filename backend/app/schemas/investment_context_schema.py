from pydantic import BaseModel
from typing import Any

class InvestmentContextResponse(BaseModel):
    portfolio: dict[str, Any]
    portfolio_score: dict[str, Any]
    portfolio_intelligence: dict[str, Any]
    portfolio_history: list[dict[str, Any]]

    goals: list[dict[str, Any]] = []
    watchlists: list[dict[str, Any]] = []
    investment_theses: list[dict[str, Any]] = []
    research_notes: list[dict[str, Any]] = []

    context_version: str