from unittest.mock import patch

from app.services.stock_analysis_service import StockAnalysisService


SAMPLE_STOCK = {
    "symbol": "NVDA",
    "company_name": "NVIDIA Corporation",
    "sector": "Technology",
    "industry": "Semiconductors",
    "market_cap": 4_000_000_000_000,
    "current_price": 200.0,
    "currency": "USD",
    "pe_ratio": 42.0,
    "forward_pe": 28.0,
    "eps": 4.5,
    "profit_margin": 0.55,
    "revenue_growth": 0.35,
    "fifty_two_week_high": 220.0,
    "fifty_two_week_low": 90.0,
    "analyst_target_price": 240.0,
    "recommendation": "buy",
    "marketmind_score": {
        "score": 82,
        "rating": "strong",
        "interpretation": "Strong fundamentals",
        "reasons": [],
        "warnings": [],
    },
}

SAMPLE_NEWS = {
    "symbol": "NVDA",
    "news": [
        {
            "title": "NVIDIA demand remains strong",
            "sentiment": "positive",
        },
        {
            "title": "New AI product launch",
            "sentiment": "positive",
        },
        {
            "title": "Valuation debate continues",
            "sentiment": "neutral",
        },
    ],
}

SAMPLE_PORTFOLIO = {
    "holdings": [
        {
            "symbol": "NVDA",
            "quantity": 2,
            "current_value": 400.0,
            "allocation_percent": 16.5,
            "profit": 110.0,
            "profit_percent": 37.9,
        }
    ]
}


def test_news_summary_counts_sentiment():
    result = StockAnalysisService._build_news_summary(SAMPLE_NEWS)

    assert result["article_count"] == 3
    assert result["positive_count"] == 2
    assert result["neutral_count"] == 1
    assert result["overall_sentiment"] == "positive"


def test_portfolio_exposure_owned():
    result = StockAnalysisService._build_portfolio_exposure(
        "NVDA",
        SAMPLE_PORTFOLIO,
    )

    assert result["owned"] is True
    assert result["quantity"] == 2
    assert result["allocation_percent"] == 16.5


def test_portfolio_exposure_not_owned():
    result = StockAnalysisService._build_portfolio_exposure(
        "AAPL",
        SAMPLE_PORTFOLIO,
    )

    assert result["owned"] is False


def test_bull_case_contains_growth_signal():
    news = StockAnalysisService._build_news_summary(SAMPLE_NEWS)
    result = StockAnalysisService._build_bull_case(
        SAMPLE_STOCK,
        news,
    )

    assert any("Revenue growth" in item for item in result)


def test_bear_case_detects_high_valuation():
    news = StockAnalysisService._build_news_summary(SAMPLE_NEWS)
    result = StockAnalysisService._build_bear_case(
        SAMPLE_STOCK,
        news,
    )

    assert any("valuation" in item.lower() for item in result)


def test_recommendation_has_required_fields():
    news = StockAnalysisService._build_news_summary(SAMPLE_NEWS)
    exposure = StockAnalysisService._build_portfolio_exposure(
        "NVDA",
        SAMPLE_PORTFOLIO,
    )

    result = StockAnalysisService._build_recommendation(
        SAMPLE_STOCK,
        news,
        exposure,
    )

    assert result["label"]
    assert 0 <= result["score"] <= 100
    assert 0 <= result["confidence"] <= 100
    assert result["disclaimer"]


@patch(
    "app.services.stock_analysis_service.StockService.search_stock",
    return_value=SAMPLE_STOCK,
)
@patch(
    "app.services.stock_analysis_service.NewsService.search_news",
    return_value=SAMPLE_NEWS,
)
@patch(
    "app.services.stock_analysis_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_analyze_returns_unified_report(
    mock_portfolio,
    mock_news,
    mock_stock,
):
    result = StockAnalysisService.analyze("nvda", db=None)

    assert result["status"] == "success"
    assert result["symbol"] == "NVDA"
    assert result["stock"]["company_name"] == "NVIDIA Corporation"
    assert result["news_summary"]["article_count"] == 3
    assert result["bull_case"]
    assert result["bear_case"]
    assert result["key_risks"]
    assert result["why_moving"]
    assert result["portfolio_exposure"]["owned"] is True
    assert result["recommendation"]["label"]


@patch(
    "app.services.stock_analysis_service.StockService.search_stock",
    return_value={
        "symbol": "BAD",
        "error": "Unable to fetch stock data",
    },
)
def test_analyze_handles_stock_error(mock_stock):
    result = StockAnalysisService.analyze("BAD", db=None)

    assert result["status"] == "not_found"
    assert result["error"] == "Unable to fetch stock data"


def test_analyze_rejects_blank_symbol():
    result = StockAnalysisService.analyze("   ", db=None)

    assert result["status"] == "needs_more_info"
