from types import SimpleNamespace
from unittest.mock import patch

from app.services.watchtower_service import (
    WatchtowerService,
)


def test_critical_classification():
    severity, event_type, score = (
        WatchtowerService._classify_event(
            (
                "Company cuts guidance after "
                "an SEC investigation"
            ),
            "negative",
            3,
            28,
        )
    )

    assert severity == "critical"
    assert score >= 75
    assert event_type in {
        "sec_investigation",
        "cuts_guidance",
    }


def test_noise_classification():
    severity, _, score = (
        WatchtowerService._classify_event(
            "Routine product color update",
            "neutral",
            1,
            0,
        )
    )

    assert severity == "noise"
    assert score < 20


def test_thesis_contradiction():
    thesis = SimpleNamespace(
        thesis="Growth remains strong"
    )

    result = (
        WatchtowerService._thesis_impact(
            "Revenue decline and guidance cut",
            thesis,
        )
    )

    assert result == "contradicts"


@patch(
    "app.services.watchtower_service."
    "NewsService.search_news"
)
@patch.object(
    WatchtowerService,
    "_thesis_map",
)
@patch.object(
    WatchtowerService,
    "_monitored_symbols",
)
def test_generate_watchtower(
    mock_symbols,
    mock_theses,
    mock_news,
):
    mock_symbols.return_value = (
        {
            "AAPL": {
                "symbol": "AAPL",
                "company_name": "Apple",
                "portfolio_owned": True,
                "portfolio_allocation_percent": 30,
                "source_type": "portfolio",
            }
        },
        {},
    )

    mock_theses.return_value = {
        "AAPL": SimpleNamespace(
            thesis="Services growth",
        )
    }

    mock_news.return_value = {
        "company_name": "Apple",
        "news": [
            {
                "title": (
                    "Apple cuts guidance after "
                    "demand weakness"
                ),
                "summary": (
                    "Sales decline in a key market."
                ),
                "publisher": "Example",
                "link": "https://example.com",
                "published_at": (
                    "2026-08-04T12:00:00Z"
                ),
                "sentiment": "negative",
                "relevance_score": 3,
            }
        ],
    }

    result = WatchtowerService.generate(
        db=object(),
        user_id=1,
    )

    assert result["monitored_symbols"] == 1
    assert result["critical_count"] == 1
    assert (
        result["alerts"][0][
            "thesis_impact"
        ]
        == "contradicts"
    )
    assert (
        result["silence_filter_active"]
        is False
    )
