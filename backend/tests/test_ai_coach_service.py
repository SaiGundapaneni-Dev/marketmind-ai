from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from app.services.ai_coach_service import (
    AICoachService,
)


def portfolio_data():
    return {
        "summary": {
            "holdings_count": 2,
        },
        "health_score": {
            "score": 82,
            "rating": "good",
        },
        "holdings": [
            {
                "id": 1,
                "symbol": "AAPL",
                "allocation_percent": 30,
                "profit_percent": 20,
            },
            {
                "id": 2,
                "symbol": "MSFT",
                "allocation_percent": 15,
                "profit_percent": -18,
            },
        ],
    }


def intelligence_data():
    return {
        "priority_insights": [],
        "strengths": [
            "The portfolio is profitable."
        ],
    }


@patch.object(
    AICoachService,
    "_get_thesis_map",
)
@patch(
    "app.services.ai_coach_service."
    "PortfolioIntelligenceService.generate"
)
@patch(
    "app.services.ai_coach_service."
    "PortfolioService.calculate"
)
def test_generate_ai_coach(
    mock_portfolio,
    mock_intelligence,
    mock_theses,
):
    mock_portfolio.return_value = (
        portfolio_data()
    )
    mock_intelligence.return_value = (
        intelligence_data()
    )

    mock_theses.return_value = {
        1: SimpleNamespace(
            review_date=(
                date.today()
                - timedelta(days=3)
            ),
            conviction_score=9,
        )
    }

    result = AICoachService.generate(
        db=object(),
        user_id=1,
        now=datetime(
            2026,
            8,
            4,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result["greeting"] == (
        "Good morning"
    )
    assert result["health_score"] == 82
    assert result["estimated_review_minutes"] == 5
    assert any(
        item["title"]
        == "AAPL is overweight"
        for item in result["priorities"]
    )
    assert any(
        item["title"]
        == "MSFT has no saved thesis"
        for item in result["priorities"]
    )


def test_greeting():
    assert (
        AICoachService._greeting(
            datetime(
                2026,
                8,
                4,
                19,
                0,
                tzinfo=timezone.utc,
            )
        )
        == "Good evening"
    )
