from types import SimpleNamespace
from unittest.mock import patch

from app.services.portfolio_intelligence_service import (
    PortfolioIntelligenceService,
)


def sample_portfolio():
    return {
        "summary": {
            "total_value": 1300,
            "total_profit": 300,
            "total_return_percent": 30,
            "holdings_count": 3,
        },
        "allocation": {
            "largest_holding": {
                "symbol": "AAPL",
                "allocation_percent": 38.46,
            }
        },
        "concentration_risk": {
            "risk_level": "high",
            "largest_position_percent": 38.46,
            "top_three_percent": 100,
            "concentrated_positions": [
                {"symbol": "AAPL"}
            ],
        },
        "performance_insights": {
            "top_performer": {
                "symbol": "NVDA",
                "profit_percent": 50,
            },
            "weakest_performer": {
                "symbol": "MSFT",
                "profit_percent": -10,
            },
            "largest_profit_contributor": {
                "symbol": "NVDA",
                "profit": 250,
            },
            "largest_loss_contributor": {
                "symbol": "MSFT",
                "profit": -50,
                "profit_percent": -10,
            },
            "profitable_holdings_count": 2,
            "losing_holdings_count": 1,
        },
        "health_score": {
            "score": 68,
            "rating": "fair",
            "components": {
                "diversification_score": 10,
                "concentration_score": 5,
            },
        },
        "holdings": [
            {
                "symbol": "AAPL",
                "name": "Apple",
                "allocation_percent": 38.46,
                "profit": 100,
                "profit_percent": 25,
                "price_status": "available",
            },
            {
                "symbol": "NVDA",
                "name": "NVIDIA",
                "allocation_percent": 30.77,
                "profit": 250,
                "profit_percent": 50,
                "price_status": "available",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft",
                "allocation_percent": 30.77,
                "profit": -50,
                "profit_percent": -10,
                "price_status": "available",
            },
        ],
    }


@patch(
    "app.services.portfolio_intelligence_service."
    "PortfolioHistoryService.get_changes"
)
@patch(
    "app.services.portfolio_intelligence_service."
    "PortfolioService.calculate"
)
def test_generate_portfolio_intelligence(
    mock_calculate,
    mock_changes,
):
    mock_calculate.return_value = sample_portfolio()
    mock_changes.return_value = {
        "summary": ["Portfolio value increased by $50."]
    }

    result = PortfolioIntelligenceService.generate(
        SimpleNamespace(),
        user_id=7,
    )

    assert result["portfolio_status"] == "fair"
    assert "AAPL" in result["executive_summary"]
    assert result["priority_insights"][0][
        "category"
    ] == "concentration"
    assert len(result["holdings_to_watch"]) == 3
    assert len(result["recommended_questions"]) >= 4


@patch(
    "app.services.portfolio_intelligence_service."
    "PortfolioHistoryService.get_changes"
)
@patch(
    "app.services.portfolio_intelligence_service."
    "PortfolioService.calculate"
)
def test_generate_empty_portfolio(
    mock_calculate,
    mock_changes,
):
    mock_calculate.return_value = {
        "summary": {"holdings_count": 0},
        "allocation": {},
        "concentration_risk": {},
        "performance_insights": {},
        "health_score": {},
        "holdings": [],
    }
    mock_changes.return_value = {"summary": []}

    result = PortfolioIntelligenceService.generate(
        SimpleNamespace(),
        user_id=7,
    )

    assert result["portfolio_status"] == "empty"
    assert result["priority_insights"] == []
    assert result["holdings_to_watch"] == []
