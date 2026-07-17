from typing import List

from pydantic import BaseModel


class PriorityInsightResponse(BaseModel):
    priority: int
    category: str
    severity: str
    title: str
    message: str
    evidence: List[str]
    suggested_action: str
    affected_symbols: List[str]


class HoldingToWatchResponse(BaseModel):
    symbol: str
    name: str
    allocation_percent: float
    profit: float
    profit_percent: float
    reason: str


class PortfolioIntelligenceResponse(BaseModel):
    portfolio_status: str
    executive_summary: str
    priority_insights: List[PriorityInsightResponse]
    strengths: List[str]
    risks: List[str]
    opportunities: List[str]
    holdings_to_watch: List[HoldingToWatchResponse]
    recent_changes: List[str]
    recommended_questions: List[str]
    disclaimer: str
