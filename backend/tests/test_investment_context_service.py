from types import SimpleNamespace
from unittest.mock import patch

from app.services.investment_context_service import (
    InvestmentContextService,
)


SAMPLE_PORTFOLIO = {
    "summary": {
        "total_cost": 1000.0,
        "total_value": 1200.0,
        "total_profit": 200.0,
        "total_return_percent": 20.0,
        "holdings_count": 2,
        "priced_holdings_count": 2,
        "unpriced_holdings_count": 0,
    },
    "allocation": {
        "by_asset_type": [],
        "largest_holding": None,
    },
    "concentration_risk": {},
    "performance_insights": {},
    "health_score": {},
    "actionable_insights": {
        "count": 0,
        "items": [],
        "disclaimer": "",
    },
    "holdings": [],
}

SAMPLE_SCORE = {
    "overall_score": 78.0,
    "rating": "good",
    "summary": "Portfolio score summary.",
    "scores": {},
    "strengths": [],
    "weaknesses": [],
    "improvement_suggestions": [],
    "disclaimer": "Informational only.",
}

SAMPLE_INTELLIGENCE = {
    "portfolio_status": "good",
    "executive_summary": "Portfolio intelligence summary.",
    "strengths": [],
    "risks": [],
    "opportunities": [],
    "holdings_to_watch": [],
    "recommended_questions": [],
    "priority_insights": [],
}

SAMPLE_HISTORY = [
    {
        "id": 1,
        "total_value": 1200.0,
    }
]


@patch(
    "app.services.investment_context_service."
    "PortfolioHistoryService.get_history"
)
@patch(
    "app.services.investment_context_service."
    "PortfolioIntelligenceService.generate"
)
@patch(
    "app.services.investment_context_service."
    "PortfolioScoreService.generate"
)
@patch(
    "app.services.investment_context_service."
    "PortfolioService.calculate"
)
def test_build_investment_context(
    mock_calculate,
    mock_score,
    mock_intelligence,
    mock_history,
):
    mock_calculate.return_value = SAMPLE_PORTFOLIO
    mock_score.return_value = SAMPLE_SCORE
    mock_intelligence.return_value = SAMPLE_INTELLIGENCE
    mock_history.return_value = SAMPLE_HISTORY

    db = SimpleNamespace()
    user_id = 7

    context = InvestmentContextService.build(
        db,
        user_id,
    )

    assert context["portfolio"] == SAMPLE_PORTFOLIO
    assert context["portfolio_score"] == SAMPLE_SCORE
    assert context["portfolio_intelligence"] == SAMPLE_INTELLIGENCE
    assert context["portfolio_history"] == SAMPLE_HISTORY

    assert context["goals"] == []
    assert context["watchlists"] == []
    assert context["investment_theses"] == []
    assert context["research_notes"] == []

    assert context["context_version"] == "1.0"

    mock_calculate.assert_called_once_with(
        db,
        user_id,
    )

    mock_score.assert_called_once_with(
        db,
        user_id,
    )

    mock_intelligence.assert_called_once_with(
        db,
        user_id,
    )

    mock_history.assert_called_once_with(
        db,
        user_id,
        limit=30,
    )


@patch(
    "app.services.investment_context_service."
    "PortfolioHistoryService.get_history",
    return_value=[],
)
@patch(
    "app.services.investment_context_service."
    "PortfolioIntelligenceService.generate",
    return_value=SAMPLE_INTELLIGENCE,
)
@patch(
    "app.services.investment_context_service."
    "PortfolioScoreService.generate",
    return_value=SAMPLE_SCORE,
)
@patch(
    "app.services.investment_context_service."
    "PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_context_default_collections_are_empty(
    mock_calculate,
    mock_score,
    mock_intelligence,
    mock_history,
):
    context = InvestmentContextService.build(
        SimpleNamespace(),
        user_id=1,
    )

    assert isinstance(context["goals"], list)
    assert isinstance(context["watchlists"], list)
    assert isinstance(context["investment_theses"], list)
    assert isinstance(context["research_notes"], list)

    assert context["goals"] == []
    assert context["watchlists"] == []
    assert context["investment_theses"] == []
    assert context["research_notes"] == []


@patch(
    "app.services.investment_context_service."
    "PortfolioHistoryService.get_history",
    return_value=[],
)
@patch(
    "app.services.investment_context_service."
    "PortfolioIntelligenceService.generate",
    return_value=SAMPLE_INTELLIGENCE,
)
@patch(
    "app.services.investment_context_service."
    "PortfolioScoreService.generate",
    return_value=SAMPLE_SCORE,
)
@patch(
    "app.services.investment_context_service."
    "PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_context_version_is_one_point_zero(
    mock_calculate,
    mock_score,
    mock_intelligence,
    mock_history,
):
    context = InvestmentContextService.build(
        SimpleNamespace(),
        user_id=1,
    )

    assert context["context_version"] == "1.0"


@patch(
    "app.services.investment_context_service."
    "PortfolioHistoryService.get_history",
    return_value=[],
)
@patch(
    "app.services.investment_context_service."
    "PortfolioIntelligenceService.generate",
    return_value=SAMPLE_INTELLIGENCE,
)
@patch(
    "app.services.investment_context_service."
    "PortfolioScoreService.generate",
    return_value=SAMPLE_SCORE,
)
@patch(
    "app.services.investment_context_service."
    "PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_context_sections_have_expected_types(
    mock_calculate,
    mock_score,
    mock_intelligence,
    mock_history,
):
    context = InvestmentContextService.build(
        SimpleNamespace(),
        user_id=1,
    )

    assert isinstance(context["portfolio"], dict)
    assert isinstance(context["portfolio_score"], dict)
    assert isinstance(context["portfolio_intelligence"], dict)
    assert isinstance(context["portfolio_history"], list)