from types import SimpleNamespace
from unittest.mock import patch

from app.services.watchlist_service import WatchlistService


SAMPLE_REPORT = {
    "stock": {
        "company_name": "NVIDIA Corporation",
        "current_price": 200.0,
        "currency": "USD",
        "market_cap": 4_000_000_000_000,
        "marketmind_score": {
            "score": 88,
            "rating": "strong",
        },
    },
    "news_summary": {
        "overall_sentiment": "positive",
        "article_count": 3,
    },
    "portfolio_exposure": {
        "owned": True,
        "allocation_percent": 16.5,
    },
    "recommendation": {
        "label": "strong research candidate",
        "confidence": 90,
    },
    "bull_case": ["Strong growth"],
    "bear_case": ["Valuation risk"],
}


def test_risk_level_low_for_high_score():
    assert WatchlistService._risk_level(SAMPLE_REPORT) == "low"


def test_risk_level_high_for_cautious_label():
    report = {
        **SAMPLE_REPORT,
        "recommendation": {
            "label": "cautious",
            "confidence": 70,
        },
    }

    assert WatchlistService._risk_level(report) == "high"


def test_build_intelligence_item():
    item = SimpleNamespace(
        id=1,
        symbol="NVDA",
        company_name="NVIDIA",
    )

    result = WatchlistService.build_intelligence_item(
        item,
        SAMPLE_REPORT,
    )

    assert result["symbol"] == "NVDA"
    assert result["company_name"] == "NVIDIA Corporation"
    assert result["marketmind_score"] == 88
    assert result["news_sentiment"] == "positive"
    assert result["portfolio_owned"] is True
    assert result["risk_level"] == "low"


@patch(
    "app.services.watchlist_service.WatchlistRepository.list_items",
)
@patch(
    "app.services.watchlist_service.StockAnalysisService.analyze",
)
def test_analyze_watchlist(mock_analyze, mock_list_items):
    mock_list_items.return_value = [
        SimpleNamespace(
            id=1,
            symbol="NVDA",
            company_name="NVIDIA",
        ),
        SimpleNamespace(
            id=2,
            symbol="AAPL",
            company_name="Apple",
        ),
    ]

    mock_analyze.side_effect = [
        SAMPLE_REPORT,
        {
            **SAMPLE_REPORT,
            "stock": {
                **SAMPLE_REPORT["stock"],
                "company_name": "Apple Inc.",
                "marketmind_score": {
                    "score": 65,
                    "rating": "moderate",
                },
            },
            "recommendation": {
                "label": "neutral",
                "confidence": 75,
            },
            "news_summary": {
                "overall_sentiment": "neutral",
                "article_count": 1,
            },
        },
    ]

    result = WatchlistService.analyze_watchlist(
        db=None,
        user_id=None,
    )

    assert result["count"] == 2
    assert result["strong_candidates"] == 1
    assert result["neutral"] == 1
    assert result["top_opportunity"]["symbol"] == "NVDA"
    assert len(result["items"]) == 2
