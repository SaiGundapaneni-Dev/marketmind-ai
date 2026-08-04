from types import SimpleNamespace
from unittest.mock import patch

from app.services.scenario_simulator_service import (
    ScenarioSimulatorService,
)


def portfolio():
    return {
        "summary": {
            "total_value": 1000,
        },
        "holdings": [
            {
                "symbol": "AAPL",
                "name": "Apple",
                "current_value": 600,
                "price_status": "available",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft",
                "current_value": 400,
                "price_status": "available",
            },
        ],
    }


@patch(
    "app.services.scenario_simulator_service."
    "PortfolioService.calculate"
)
def test_single_stock_scenario(
    mock_calculate,
):
    mock_calculate.return_value = portfolio()

    result = (
        ScenarioSimulatorService.simulate(
            db=object(),
            user_id=1,
            scenario_name="AAPL -20%",
            changes=[
                SimpleNamespace(
                    symbol="AAPL",
                    change_percent=-20,
                )
            ],
        )
    )

    assert (
        result[
            "projected_portfolio_value"
        ]
        == 880
    )

    assert result["impact_value"] == -120
    assert result["impact_percent"] == -12
    assert result["risk_level"] == "high"
    assert (
        result[
            "affected_holdings_count"
        ]
        == 1
    )


@patch(
    "app.services.scenario_simulator_service."
    "PortfolioService.calculate"
)
def test_multi_stock_positive_scenario(
    mock_calculate,
):
    mock_calculate.return_value = portfolio()

    result = (
        ScenarioSimulatorService.simulate(
            db=object(),
            user_id=1,
            scenario_name="Rally",
            changes=[
                SimpleNamespace(
                    symbol="AAPL",
                    change_percent=10,
                ),
                SimpleNamespace(
                    symbol="MSFT",
                    change_percent=5,
                ),
            ],
        )
    )

    assert (
        result[
            "projected_portfolio_value"
        ]
        == 1080
    )

    assert result["impact_percent"] == 8
    assert result["resilience_score"] == 100


def test_risk_thresholds():
    assert (
        ScenarioSimulatorService._risk_level(
            -3
        )
        == "low"
    )
    assert (
        ScenarioSimulatorService._risk_level(
            -7
        )
        == "medium"
    )
    assert (
        ScenarioSimulatorService._risk_level(
            -15
        )
        == "high"
    )
    assert (
        ScenarioSimulatorService._risk_level(
            -25
        )
        == "severe"
    )
