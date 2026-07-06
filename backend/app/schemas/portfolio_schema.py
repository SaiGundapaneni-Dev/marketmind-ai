from typing import List

from pydantic import BaseModel, Field


class HoldingCreate(BaseModel):
    asset_type: str
    symbol: str
    name: str
    quantity: float = Field(gt=0)
    average_price: float = Field(gt=0)
    currency: str
    portfolio_id: int


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