from unittest.mock import MagicMock, patch

from app.services.portfolio_service import PortfolioService


@patch(
    "app.services.portfolio_service.PortfolioRepository.get_holdings"
)
@patch(
    "app.services.portfolio_service.PriceService.get_live_price"
)
def test_calculate_portfolio(
    mock_price,
    mock_get_holdings,
):
    mock_price.return_value = 200.0

    mock_holding = MagicMock()
    mock_holding.id = 1
    mock_holding.asset_type = "US"
    mock_holding.symbol = "AAPL"
    mock_holding.name = "Apple"
    mock_holding.quantity = 2
    mock_holding.average_price = 100.0

    mock_get_holdings.return_value = [
        mock_holding
    ]

    mock_db = MagicMock()

    result = PortfolioService.calculate(
        mock_db
    )

    assert result["summary"]["total_cost"] == 200.0
    assert result["summary"]["total_value"] == 400.0
    assert result["summary"]["total_profit"] == 200.0
    assert (
        result["summary"]["total_return_percent"]
        == 100.0
    )

    assert result["summary"]["holdings_count"] == 1
    assert (
        result["summary"]["priced_holdings_count"]
        == 1
    )
    assert (
        result["summary"]["unpriced_holdings_count"]
        == 0
    )

    assert len(result["holdings"]) == 1

    holding = result["holdings"][0]

    assert holding["symbol"] == "AAPL"
    assert holding["current_price"] == 200.0
    assert holding["current_value"] == 400.0
    assert holding["profit"] == 200.0
    assert holding["profit_percent"] == 100.0
    assert holding["allocation_percent"] == 100.0
    assert holding["price_status"] == "available"

    mock_get_holdings.assert_called_once_with(
        mock_db
    )
    mock_price.assert_called_once_with("AAPL")