from typing import List, Optional

from pydantic import BaseModel, Field


class HoldingCreate(BaseModel):
    asset_type: str
    symbol: str
    name: str
    quantity: float = Field(gt=0)
    average_price: float = Field(gt=0)
    currency: str
    portfolio_id: int


class HoldingUpdate(BaseModel):
    asset_type: str
    symbol: str
    name: str
    quantity: float = Field(gt=0)
    average_price: float = Field(gt=0)
    currency: str


class HoldingResponse(BaseModel):
    id: int
    asset_type: str
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: Optional[float] = None
    cost: float
    current_value: float
    profit: float
    profit_percent: float
    allocation_percent: float
    price_status: str


class PortfolioSummaryResponse(BaseModel):
    total_cost: float
    total_value: float
    total_profit: float
    total_return_percent: float
    holdings_count: int
    priced_holdings_count: int
    unpriced_holdings_count: int


class AssetTypeAllocationResponse(BaseModel):
    asset_type: str
    value: float
    allocation_percent: float


class LargestHoldingResponse(BaseModel):
    symbol: str
    name: str
    current_value: float
    allocation_percent: float


class PortfolioAllocationResponse(BaseModel):
    by_asset_type: List[AssetTypeAllocationResponse]
    largest_holding: Optional[
        LargestHoldingResponse
    ] = None


class ConcentratedPositionResponse(BaseModel):
    symbol: str
    name: str
    allocation_percent: float


class ConcentrationRiskResponse(BaseModel):
    risk_level: str
    largest_position_percent: float
    top_three_percent: float
    concentrated_positions: List[
        ConcentratedPositionResponse
    ]
    message: str


class PerformerResponse(BaseModel):
    symbol: str
    name: str
    profit: float
    profit_percent: float


class PerformanceInsightsResponse(BaseModel):
    top_performer: Optional[PerformerResponse] = None
    weakest_performer: Optional[PerformerResponse] = None
    largest_profit_contributor: Optional[
        PerformerResponse
    ] = None
    largest_loss_contributor: Optional[
        PerformerResponse
    ] = None
    profitable_holdings_count: int
    losing_holdings_count: int
    breakeven_holdings_count: int
    message: str
    
class HealthScoreComponentsResponse(BaseModel):
    diversification_score: float
    concentration_score: float
    profitability_score: float
    pricing_coverage_score: float


class PortfolioHealthScoreResponse(BaseModel):
    score: float
    rating: str
    components: HealthScoreComponentsResponse
    message: str
    
class PortfolioResponse(BaseModel):
    summary: PortfolioSummaryResponse
    allocation: PortfolioAllocationResponse
    concentration_risk: ConcentrationRiskResponse
    performance_insights: PerformanceInsightsResponse
    health_score: PortfolioHealthScoreResponse
    holdings: List[HoldingResponse]
    