from types import SimpleNamespace
from unittest.mock import patch

from app.services.portfolio_score_service import PortfolioScoreService


def sample_portfolio():
    return {
        "summary": {
            "total_return_percent": 30,
            "holdings_count": 3,
            "priced_holdings_count": 3,
            "unpriced_holdings_count": 0,
        },
        "allocation": {
            "by_asset_type": [
                {"asset_type": "stock", "allocation_percent": 100}
            ],
            "largest_holding": {
                "symbol": "AAPL",
                "allocation_percent": 38.46,
            },
        },
        "concentration_risk": {
            "risk_level": "high",
            "largest_position_percent": 38.46,
            "top_three_percent": 100,
        },
        "performance_insights": {
            "top_performer": {"symbol": "NVDA", "profit_percent": 50},
            "weakest_performer": {"symbol": "MSFT", "profit_percent": -10},
            "profitable_holdings_count": 2,
            "losing_holdings_count": 1,
        },
        "health_score": {
            "score": 68,
            "rating": "fair",
            "components": {
                "diversification_score": 10,
                "concentration_score": 5,
                "profitability_score": 16.67,
                "pricing_coverage_score": 25,
            },
            "message": "Portfolio health is fair.",
        },
        "holdings": [
            {"symbol": "AAPL", "asset_type": "stock", "price_status": "available"},
            {"symbol": "NVDA", "asset_type": "stock", "price_status": "available"},
            {"symbol": "MSFT", "asset_type": "stock", "price_status": "available"},
        ],
    }


@patch("app.services.portfolio_score_service.PortfolioService.calculate")
def test_generate_portfolio_score(mock_calculate):
    mock_calculate.return_value = sample_portfolio()
    db = SimpleNamespace()

    result = PortfolioScoreService.generate(db, user_id=7)

    assert 0 <= result["overall_score"] <= 100
    assert result["rating"] in {"excellent", "good", "fair", "weak"}
    assert set(result["scores"]) == {
        "diversification",
        "concentration",
        "performance",
        "portfolio_health",
        "market_exposure",
    }
    assert result["scores"]["concentration"]["score"] < 70
    assert result["scores"]["performance"]["score"] >= 70
    assert result["summary"]
    assert result["improvement_suggestions"]
    mock_calculate.assert_called_once_with(db, 7)


@patch("app.services.portfolio_score_service.PortfolioService.calculate")
def test_generate_empty_portfolio_score(mock_calculate):
    mock_calculate.return_value = {
        "summary": {
            "holdings_count": 0,
            "priced_holdings_count": 0,
            "unpriced_holdings_count": 0,
        },
        "allocation": {},
        "concentration_risk": {},
        "performance_insights": {},
        "health_score": {},
        "holdings": [],
    }

    result = PortfolioScoreService.generate(SimpleNamespace(), user_id=7)

    assert result["overall_score"] == 0
    assert result["rating"] == "empty"
    assert result["strengths"] == []
    assert result["weaknesses"]
    assert all(item["score"] == 0 for item in result["scores"].values())


def test_rating_thresholds():
    assert PortfolioScoreService._rating(90) == "excellent"
    assert PortfolioScoreService._rating(75) == "good"
    assert PortfolioScoreService._rating(55) == "fair"
    assert PortfolioScoreService._rating(25) == "weak"


def test_clamp():
    assert PortfolioScoreService._clamp(120) == 100
    assert PortfolioScoreService._clamp(-10) == 0
    assert PortfolioScoreService._clamp(72.345) == 72.34
