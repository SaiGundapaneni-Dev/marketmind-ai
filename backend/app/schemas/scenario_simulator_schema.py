from typing import Literal

from pydantic import BaseModel, Field


class ScenarioChange(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    change_percent: float = Field(ge=-100, le=500)


class ScenarioPreset(BaseModel):
    key: str
    name: str
    description: str
    changes: list[ScenarioChange]


class ScenarioSimulationRequest(BaseModel):
    name: str = Field(
        default="Custom Scenario",
        min_length=1,
        max_length=120,
    )
    changes: list[ScenarioChange] = Field(
        min_length=1,
        max_length=50,
    )


class ScenarioHoldingImpact(BaseModel):
    symbol: str
    name: str
    current_value: float
    change_percent: float
    projected_value: float
    impact_value: float
    portfolio_impact_percent: float


class ScenarioSimulationResponse(BaseModel):
    scenario_name: str
    current_portfolio_value: float
    projected_portfolio_value: float
    impact_value: float
    impact_percent: float
    affected_holdings_count: int
    unaffected_holdings_count: int
    resilience_score: float
    risk_level: Literal[
        "low",
        "medium",
        "high",
        "severe",
    ]
    recommendation: str
    explanation: str
    holding_impacts: list[ScenarioHoldingImpact]
    warnings: list[str]
    disclaimer: str


class ScenarioPresetsResponse(BaseModel):
    presets: list[ScenarioPreset]
