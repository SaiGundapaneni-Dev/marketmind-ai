from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

GoalCategory = Literal[
    "retirement", "emergency_fund", "house", "education", "travel",
    "car", "financial_independence", "custom",
]
GoalPriority = Literal["high", "medium", "low"]
GoalStatus = Literal["completed", "on_track", "slightly_behind", "off_track"]


class InvestmentGoalBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: GoalCategory = "custom"
    target_amount: float = Field(gt=0)
    current_amount: float = Field(ge=0, default=0)
    monthly_contribution: float = Field(ge=0, default=0)
    target_date: date
    priority: GoalPriority = "medium"
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def clamp_current_amount(self):
        if self.current_amount > self.target_amount:
            self.current_amount = self.target_amount
        return self


class InvestmentGoalCreate(InvestmentGoalBase):
    pass


class InvestmentGoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: GoalCategory | None = None
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    monthly_contribution: float | None = Field(default=None, ge=0)
    target_date: date | None = None
    priority: GoalPriority | None = None
    notes: str | None = Field(default=None, max_length=2000)


class InvestmentGoalResponse(InvestmentGoalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GoalProgressResponse(InvestmentGoalResponse):
    remaining_amount: float
    progress_percent: float
    months_remaining: int
    projected_completion_date: date | None
    required_monthly_contribution: float
    contribution_gap: float
    health_score: float
    status: GoalStatus
    coach_message: str


class GoalSummaryResponse(BaseModel):
    total_goals: int
    completed_goals: int
    on_track_goals: int
    behind_goals: int
    total_target_amount: float
    total_current_amount: float
    overall_progress_percent: float
    goals: list[GoalProgressResponse]
