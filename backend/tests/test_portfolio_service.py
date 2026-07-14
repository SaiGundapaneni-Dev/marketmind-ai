from unittest.mock import MagicMock, patch

from app.services.portfolio_service import PortfolioService


@patch(
    "app.services.portfolio_calculation_service."
    "PortfolioRepository.get_holdings"
)
@patch(
    "app.services.portfolio_calculation_service."
    "PriceService.get_live_price"
)
def test_calculate_portfolio(
    mock_price,
    mock_get_holdings,
):
    mock_price.return_value = 200.0

    holding = MagicMock()
    holding.id = 1
    holding.asset_type = "US"
    holding.symbol = "AAPL"
    holding.name = "Apple"
    holding.quantity = 2
    holding.average_price = 100.0

    mock_get_holdings.return_value = [holding]

    result = PortfolioService.calculate(MagicMock())

    assert result["summary"]["total_cost"] == 200.0
    assert result["summary"]["total_value"] == 400.0
    assert result["summary"]["total_profit"] == 200.0
    assert result["summary"]["total_return_percent"] == 100.0
    assert result["summary"]["holdings_count"] == 1
    assert result["summary"]["priced_holdings_count"] == 1
    assert result["summary"]["unpriced_holdings_count"] == 0

    item = result["holdings"][0]

    assert item["symbol"] == "AAPL"
    assert item["current_price"] == 200.0
    assert item["current_value"] == 400.0
    assert item["profit"] == 200.0
    assert item["profit_percent"] == 100.0
    assert item["allocation_percent"] == 100.0
    assert item["price_status"] == "available"

    assert result["concentration_risk"]["risk_level"] == "high"
    assert result["performance_insights"][
        "top_performer"
    ]["symbol"] == "AAPL"
    assert result["health_score"]["score"] == 60.0
    assert result["actionable_insights"]["count"] >= 1


@patch(
    "app.services.portfolio_calculation_service."
    "PortfolioRepository.get_holdings"
)
@patch(
    "app.services.portfolio_calculation_service."
    "PriceService.get_live_price"
)
def test_calculate_portfolio_with_missing_price(
    mock_price,
    mock_get_holdings,
):
    mock_price.return_value = None

    holding = MagicMock()
    holding.id = 1
    holding.asset_type = "US"
    holding.symbol = "UNKNOWN"
    holding.name = "Unknown"
    holding.quantity = 1
    holding.average_price = 50.0

    mock_get_holdings.return_value = [holding]

    result = PortfolioService.calculate(MagicMock())

    assert result["summary"]["total_cost"] == 50.0
    assert result["summary"]["total_value"] == 0.0
    assert result["summary"]["unpriced_holdings_count"] == 1
    assert result["holdings"][0]["current_price"] is None
    assert result["concentration_risk"]["risk_level"] == "unknown"
    assert result["health_score"]["components"][
        "pricing_coverage_score"
    ] == 0.0
