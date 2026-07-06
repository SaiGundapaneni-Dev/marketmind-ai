from pydantic import BaseModel
from typing import List


class HoldingResponse(BaseModel):
    asset_type: str
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: float
    cost: float
    current_value: float
    profit: float
    profit_percent: float


class PortfolioSummaryResponse(BaseModel):
    total_cost: float
    total_value: float
    total_profit: float
    total_return_percent: float


class PortfolioResponse(BaseModel):
    summary: PortfolioSummaryResponse
    holdings: List[HoldingResponse]