from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class InvestmentThesisCreate(BaseModel):
    holding_id: int = Field(..., gt=0)

    thesis: str = Field(
        ...,
        min_length=10,
        max_length=5000,
    )

    target_price: float | None = Field(
        default=None,
        gt=0,
    )

    investment_horizon: str | None = Field(
        default=None,
        max_length=50,
    )

    conviction_score: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )

    risk_level: Literal[
        "Low",
        "Medium",
        "High",
    ] | None = None

    buy_reasons: str | None = None

    sell_conditions: str | None = None

    notes: str | None = None

    review_date: date | None = None


class InvestmentThesisUpdate(BaseModel):
    thesis: str | None = None
    target_price: float | None = Field(
        default=None,
        gt=0,
    )
    investment_horizon: str | None = None
    conviction_score: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )

    risk_level: Literal[
        "Low",
        "Medium",
        "High",
    ] | None = None

    buy_reasons: str | None = None

    sell_conditions: str | None = None

    notes: str | None = None

    review_date: date | None = None


class InvestmentThesisResponse(BaseModel):
    id: int
    holding_id: int

    thesis: str

    target_price: float | None

    investment_horizon: str | None

    conviction_score: int | None

    risk_level: str | None

    buy_reasons: str | None

    sell_conditions: str | None

    notes: str | None

    review_date: date | None

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True