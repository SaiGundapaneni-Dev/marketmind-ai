from unittest.mock import patch

from app.services.portfolio_service import PortfolioService


@patch(
    "app.services.portfolio_service.PriceService.get_live_price"
)
def test_calculate_portfolio(mock_price):
    mock_price.return_value = 200.0

    result = PortfolioService.calculate()

    assert "summary" in result
    assert "holdings" in result

    assert result["summary"]["total_cost"] >= 0
    assert result["summary"]["total_value"] >= 0

    assert isinstance(result["holdings"], list)