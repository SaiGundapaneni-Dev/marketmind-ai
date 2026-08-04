from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from app.services.investment_review_service import (
    InvestmentReviewService,
)


def make_thesis(
    *,
    target_price=250.0,
    review_date=None,
    risk_level="Medium",
):
    return SimpleNamespace(
        id=1,
        holding_id=10,
        thesis="Strong long-term business with durable growth.",
        target_price=target_price,
        investment_horizon="5 Years",
        conviction_score=8,
        risk_level=risk_level,
        buy_reasons="Growth and recurring revenue",
        sell_conditions="Growth permanently weakens",
        notes=None,
        review_date=review_date,
    )


def make_holding():
    return SimpleNamespace(
        id=10,
        symbol="AAPL",
        name="Apple Inc.",
        quantity=2.0,
        average_price=180.0,
    )


def test_on_track_review():
    thesis = make_thesis()
    holding = make_holding()

    with (
        patch.object(
            InvestmentReviewService,
            "_get_thesis_and_holding",
            return_value=(thesis, holding),
        ),
        patch(
            "app.services.investment_review_service."
            "PriceService.get_live_price",
            return_value=220.0,
        ),
        patch(
            "app.services.investment_review_service."
            "NewsService.search_news",
            return_value={
                "news": [
                    {"sentiment": "positive"},
                    {"sentiment": "positive"},
                    {"sentiment": "neutral"},
                ]
            },
        ),
        patch(
            "app.services.investment_review_service."
            "PortfolioService.calculate",
            return_value={
                "holdings": [
                    {
                        "id": 10,
                        "symbol": "AAPL",
                        "allocation_percent": 18.0,
                    }
                ]
            },
        ),
    ):
        result = InvestmentReviewService.review_by_holding(
            db=object(),
            user_id=1,
            holding_id=10,
        )

    assert result["status"] == "On Track"
    assert result["current_price"] == 220.0
    assert result["target_progress_percent"] == 88.0
    assert result["news"]["positive"] == 2


def test_review_due_has_priority():
    thesis = make_thesis(
        review_date=date.today() - timedelta(days=1)
    )
    holding = make_holding()

    with (
        patch.object(
            InvestmentReviewService,
            "_get_thesis_and_holding",
            return_value=(thesis, holding),
        ),
        patch(
            "app.services.investment_review_service."
            "PriceService.get_live_price",
            return_value=220.0,
        ),
        patch(
            "app.services.investment_review_service."
            "NewsService.search_news",
            return_value={"news": []},
        ),
        patch(
            "app.services.investment_review_service."
            "PortfolioService.calculate",
            return_value={"holdings": []},
        ),
    ):
        result = InvestmentReviewService.review_by_holding(
            db=object(),
            user_id=1,
            holding_id=10,
        )

    assert result["status"] == "Review Due"
    assert result["review_overdue"] is True


def test_target_reached():
    thesis = make_thesis(target_price=200.0)
    holding = make_holding()

    with (
        patch.object(
            InvestmentReviewService,
            "_get_thesis_and_holding",
            return_value=(thesis, holding),
        ),
        patch(
            "app.services.investment_review_service."
            "PriceService.get_live_price",
            return_value=220.0,
        ),
        patch(
            "app.services.investment_review_service."
            "NewsService.search_news",
            return_value={"news": []},
        ),
        patch(
            "app.services.investment_review_service."
            "PortfolioService.calculate",
            return_value={"holdings": []},
        ),
    ):
        result = InvestmentReviewService.review_by_holding(
            db=object(),
            user_id=1,
            holding_id=10,
        )

    assert result["status"] == "Target Reached"
    assert result["upside_to_target_percent"] < 0


def test_missing_thesis_raises_value_error():
    with patch.object(
        InvestmentReviewService,
        "_get_thesis_and_holding",
        return_value=None,
    ):
        try:
            InvestmentReviewService.review_by_holding(
                db=object(),
                user_id=1,
                holding_id=999,
            )
        except ValueError as exc:
            assert "No investment thesis" in str(exc)
        else:
            raise AssertionError(
                "Expected ValueError for missing thesis."
            )
