from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PortfolioSnapshotResponse(BaseModel):
    id: int
    total_cost: float
    total_value: float
    total_profit: float
    total_return_percent: float
    health_score: float
    holdings_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PortfolioPerformanceResponse(BaseModel):
    current_value: float
    previous_value: Optional[float] = None
    change: float
    change_percent: float
    highest_value: float
    lowest_value: float
    best_day_change: float
    worst_day_change: float
    snapshot_count: int


class PortfolioContributorResponse(BaseModel):
    symbol: str
    name: str
    profit: float
    profit_percent: float
    contribution_percent: float


class PortfolioContributorsResponse(BaseModel):
    top_contributors: List[PortfolioContributorResponse]
    bottom_contributors: List[PortfolioContributorResponse]


class PortfolioChangesResponse(BaseModel):
    has_previous_snapshot: bool
    value_change: float
    value_change_percent: float
    profit_change: float
    return_change: float
    health_score_change: float
    holdings_count_change: int
    summary: List[str]
