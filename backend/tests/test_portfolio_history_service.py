from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.portfolio_history_service import PortfolioHistoryService


def snapshot(
    value: float,
    profit: float,
    return_percent: float,
    health: float,
    holdings: int,
):
    return SimpleNamespace(
        total_value=value,
        total_profit=profit,
        total_return_percent=return_percent,
        health_score=health,
        holdings_count=holdings,
    )


@patch(
    "app.services.portfolio_history_service."
    "PortfolioSnapshotRepository.list_history"
)
def test_get_performance(mock_history):
    mock_history.return_value = [
        snapshot(1000, 100, 10, 70, 4),
        snapshot(1100, 180, 18, 72, 5),
        snapshot(1050, 150, 15, 71, 5),
    ]

    result = PortfolioHistoryService.get_performance(
        MagicMock()
    )

    assert result["current_value"] == 1050
    assert result["previous_value"] == 1100
    assert result["change"] == -50
    assert result["highest_value"] == 1100
    assert result["lowest_value"] == 1000
    assert result["best_day_change"] == 100
    assert result["worst_day_change"] == -50
    assert result["snapshot_count"] == 3


@patch(
    "app.services.portfolio_history_service."
    "PortfolioService.calculate"
)
def test_get_contributors(mock_calculate):
    mock_calculate.return_value = {
        "holdings": [
            {
                "symbol": "AAPL",
                "name": "Apple",
                "profit": 200.0,
                "profit_percent": 50.0,
                "price_status": "available",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft",
                "profit": -50.0,
                "profit_percent": -10.0,
                "price_status": "available",
            },
        ]
    }

    result = PortfolioHistoryService.get_contributors(
        MagicMock()
    )

    assert result["top_contributors"][0]["symbol"] == "AAPL"
    assert result["bottom_contributors"][0]["symbol"] == "MSFT"
    assert result["top_contributors"][0][
        "contribution_percent"
    ] == 80.0


@patch(
    "app.services.portfolio_history_service."
    "PortfolioSnapshotRepository.get_previous"
)
@patch(
    "app.services.portfolio_history_service."
    "PortfolioSnapshotRepository.get_latest"
)
def test_get_changes(mock_latest, mock_previous):
    mock_latest.return_value = snapshot(
        1200,
        250,
        26,
        75,
        6,
    )
    mock_previous.return_value = snapshot(
        1000,
        150,
        16,
        70,
        5,
    )

    result = PortfolioHistoryService.get_changes(
        MagicMock()
    )

    assert result["has_previous_snapshot"] is True
    assert result["value_change"] == 200
    assert result["value_change_percent"] == 20
    assert result["profit_change"] == 100
    assert result["health_score_change"] == 5
    assert result["holdings_count_change"] == 1


@patch(
    "app.services.portfolio_history_service."
    "PortfolioSnapshotRepository.create"
)
@patch(
    "app.services.portfolio_history_service."
    "PortfolioService.calculate"
)
@patch(
    "app.services.portfolio_history_service."
    "PortfolioSnapshotRepository.get_for_day"
)
def test_create_daily_snapshot_prevents_duplicate(
    mock_get_for_day,
    mock_calculate,
    mock_create,
):
    existing = SimpleNamespace(id=1)
    mock_get_for_day.return_value = existing

    result = PortfolioHistoryService.create_daily_snapshot(
        MagicMock()
    )

    assert result is existing
    mock_calculate.assert_not_called()
    mock_create.assert_not_called()
