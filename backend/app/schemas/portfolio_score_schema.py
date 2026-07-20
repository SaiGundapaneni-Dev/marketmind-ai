from typing import Dict, List

from pydantic import BaseModel


class PortfolioScoreCategoryResponse(BaseModel):
    score: float
    rating: str
    summary: str
    factors: List[str]
    suggested_action: str


class PortfolioScoreResponse(BaseModel):
    overall_score: float
    rating: str
    summary: str
    scores: Dict[str, PortfolioScoreCategoryResponse]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    disclaimer: str
