from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WatchlistCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    company_name: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=1000)


class WatchlistUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=1000)


class WatchlistItemResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    company_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchlistIntelligenceItem(BaseModel):
    id: int
    symbol: str
    company_name: Optional[str] = None
    current_price: Optional[float] = None
    currency: Optional[str] = None
    market_cap: Optional[float] = None
    marketmind_score: Optional[float] = None
    marketmind_rating: Optional[str] = None
    research_classification: Optional[str] = None
    confidence: Optional[float] = None
    news_sentiment: str
    article_count: int
    portfolio_owned: bool
    portfolio_allocation_percent: float
    risk_level: str
    bull_case: List[str]
    bear_case: List[str]
    updated_at: datetime
    error: Optional[str] = None


class WatchlistSummaryResponse(BaseModel):
    count: int
    strong_candidates: int
    positive: int
    neutral: int
    cautious_or_high_risk: int
    top_opportunity: Optional[WatchlistIntelligenceItem] = None
    highest_risk: Optional[WatchlistIntelligenceItem] = None
    most_positive_news: Optional[WatchlistIntelligenceItem] = None
    most_negative_news: Optional[WatchlistIntelligenceItem] = None
    items: List[WatchlistIntelligenceItem]
