from datetime import date
from typing import Literal

from pydantic import BaseModel


class InvestmentReviewNews(BaseModel):
    article_count: int
    positive: int
    neutral: int
    negative: int
    overall_sentiment: Literal[
        "positive",
        "neutral",
        "negative",
    ]


class InvestmentReviewPosition(BaseModel):
    quantity: float
    average_price: float
    current_value: float | None
    unrealized_profit: float | None
    unrealized_return_percent: float | None
    allocation_percent: float | None


class InvestmentReviewResponse(BaseModel):
    symbol: str
    company_name: str
    status: Literal[
        "On Track",
        "Needs Attention",
        "Review Due",
        "Target Reached",
        "Insufficient Data",
    ]
    recommendation: str
    summary: str

    current_price: float | None
    target_price: float | None
    target_progress_percent: float | None
    upside_to_target_percent: float | None

    conviction_score: int | None
    risk_level: str | None
    investment_horizon: str | None
    review_date: date | None
    review_overdue: bool

    thesis: str
    buy_reasons: str | None
    sell_conditions: str | None

    news: InvestmentReviewNews
    position: InvestmentReviewPosition
    signals: list[str]
    risks: list[str]

    disclaimer: str
