from datetime import datetime, timezone
from unittest.mock import patch

from app.services.daily_brief_service import (
    DailyBriefService,
)


def sample_portfolio():
    return {
        "summary": {
            "total_value": 2500,
            "total_profit": 500,
            "total_return_percent": 25,
            "holdings_count": 4,
        },
        "health_score": {
            "score": 82,
            "rating": "good",
        },
        "concentration_risk": {
            "risk_level": "medium",
        },
    }


def sample_intelligence():
    return {
        "executive_summary": (
            "Portfolio health is good and one "
            "position deserves attention."
        ),
        "priority_insights": [
            {
                "category": "concentration",
                "severity": "medium",
                "title": "Medium concentration risk",
                "message": (
                    "The top three holdings represent "
                    "70% of portfolio value."
                ),
                "suggested_action": (
                    "Review position sizing."
                ),
                "affected_symbols": [
                    "AAPL",
                ],
            }
        ],
        "strengths": [
            "Three holdings are profitable."
        ],
        "risks": [
            "The top three holdings are concentrated."
        ],
        "recent_changes": [
            "Portfolio value increased by $50."
        ],
        "holdings_to_watch": [
            {
                "symbol": "AAPL",
                "reason": "Large portfolio allocation",
            }
        ],
        "recommended_questions": [
            "What should I focus on today?"
        ],
    }


@patch(
    "app.services.daily_brief_service."
    "PortfolioIntelligenceService.generate"
)
@patch(
    "app.services.daily_brief_service."
    "PortfolioService.calculate"
)
def test_generate_daily_brief(
    mock_calculate,
    mock_intelligence,
):
    mock_calculate.return_value = (
        sample_portfolio()
    )

    mock_intelligence.return_value = (
        sample_intelligence()
    )

    result = DailyBriefService.generate(
        db=object(),
        user_id=7,
        now=datetime(
            2026,
            8,
            4,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result["greeting"] == (
        "Good afternoon"
    )

    assert result["action"] == "MONITOR"

    assert (
        result["portfolio_snapshot"][
            "health_score"
        ]
        == 82
    )

    assert (
        result["priorities"][0]["title"]
        == "Medium concentration risk"
    )

    assert result["holdings_to_watch"] == [
        "AAPL: Large portfolio allocation"
    ]


def test_high_priority_requires_review():
    action, reason = (
        DailyBriefService._action(
            [
                {
                    "severity": "high",
                    "title": "High concentration risk",
                }
            ],
            80,
        )
    )

    assert action == "REVIEW"
    assert reason == (
        "High concentration risk"
    )


def test_healthy_portfolio_returns_hold():
    action, _ = (
        DailyBriefService._action(
            [],
            85,
        )
    )

    assert action == "HOLD"
