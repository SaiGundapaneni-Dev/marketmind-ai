from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.investment_thesis import InvestmentThesis
from app.models.models import Holding, Portfolio
from app.services.news_service import NewsService
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService


class InvestmentReviewService:
    """
    Combines a user's saved thesis with live price, recent news,
    and portfolio exposure to produce an explainable review.

    This service is deterministic. It does not place trades and does
    not return personalized buy/sell instructions.
    """

    @staticmethod
    def _get_thesis_and_holding(
        db: Session,
        user_id: int,
        holding_id: int | None = None,
        symbol: str | None = None,
    ) -> tuple[InvestmentThesis, Holding] | None:
        query = (
            db.query(InvestmentThesis, Holding)
            .join(
                Holding,
                Holding.id == InvestmentThesis.holding_id,
            )
            .join(
                Portfolio,
                Portfolio.id == Holding.portfolio_id,
            )
            .filter(Portfolio.user_id == user_id)
        )

        if holding_id is not None:
            query = query.filter(Holding.id == holding_id)

        if symbol is not None:
            query = query.filter(
                Holding.symbol == symbol.strip().upper()
            )

        result = query.first()

        if result is None:
            return None

        thesis, holding = result
        return thesis, holding

    @staticmethod
    def _safe_number(value: Any) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)
        return None

    @staticmethod
    def _news_summary(symbol: str) -> dict:
        try:
            payload = NewsService.search_news(symbol)
        except Exception:
            payload = {
                "news": [],
                "error": "Unable to fetch news",
            }

        articles = payload.get("news", [])
        if not isinstance(articles, list):
            articles = []

        positive = sum(
            item.get("sentiment") == "positive"
            for item in articles
        )
        negative = sum(
            item.get("sentiment") == "negative"
            for item in articles
        )
        neutral = len(articles) - positive - negative

        if positive > negative:
            overall = "positive"
        elif negative > positive:
            overall = "negative"
        else:
            overall = "neutral"

        return {
            "article_count": len(articles),
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "overall_sentiment": overall,
        }

    @staticmethod
    def _portfolio_position(
        db: Session,
        user_id: int,
        holding: Holding,
        current_price: float | None,
    ) -> dict:
        allocation_percent = None

        try:
            portfolio = PortfolioService.calculate(
                db,
                user_id,
            )
            portfolio_holdings = portfolio.get(
                "holdings",
                [],
            )

            matched_holding = next(
                (
                    item
                    for item in portfolio_holdings
                    if item.get("id") == holding.id
                    or (
                        str(
                            item.get("symbol", "")
                        ).upper()
                        == holding.symbol.upper()
                    )
                ),
                None,
            )

            if matched_holding:
                allocation_percent = (
                    InvestmentReviewService._safe_number(
                        matched_holding.get(
                            "allocation_percent"
                        )
                    )
                )
        except Exception:
            allocation_percent = None

        current_value = None
        unrealized_profit = None
        unrealized_return_percent = None

        if current_price is not None:
            current_value = round(
                holding.quantity * current_price,
                2,
            )
            cost = holding.quantity * holding.average_price
            unrealized_profit = round(
                current_value - cost,
                2,
            )

            if cost > 0:
                unrealized_return_percent = round(
                    unrealized_profit / cost * 100,
                    2,
                )

        return {
            "quantity": holding.quantity,
            "average_price": holding.average_price,
            "current_value": current_value,
            "unrealized_profit": unrealized_profit,
            "unrealized_return_percent": (
                unrealized_return_percent
            ),
            "allocation_percent": allocation_percent,
        }

    @staticmethod
    def _build_classification(
        thesis: InvestmentThesis,
        current_price: float | None,
        news: dict,
        position: dict,
    ) -> tuple[str, str, list[str], list[str]]:
        signals: list[str] = []
        risks: list[str] = []

        review_overdue = bool(
            thesis.review_date
            and thesis.review_date < date.today()
        )

        target_reached = bool(
            current_price is not None
            and thesis.target_price is not None
            and current_price >= thesis.target_price
        )

        if current_price is None:
            risks.append(
                "Live price data is currently unavailable."
            )
        else:
            signals.append(
                f"Live price is ${current_price:,.2f}."
            )

        if thesis.target_price is not None:
            signals.append(
                f"Saved target price is "
                f"${thesis.target_price:,.2f}."
            )

        if news["article_count"] == 0:
            signals.append(
                "No highly relevant recent news was found."
            )
        elif news["overall_sentiment"] == "positive":
            signals.append(
                "Recent relevant news sentiment is positive."
            )
        elif news["overall_sentiment"] == "negative":
            risks.append(
                "Recent relevant news sentiment is negative."
            )
        else:
            signals.append(
                "Recent relevant news sentiment is mixed or neutral."
            )

        return_percent = position.get(
            "unrealized_return_percent"
        )

        if return_percent is not None:
            if return_percent <= -15:
                risks.append(
                    "The position is more than 15% below "
                    "its recorded average cost."
                )
            elif return_percent >= 25:
                signals.append(
                    "The position has a meaningful unrealized gain."
                )

        allocation = position.get(
            "allocation_percent"
        )

        if allocation is not None and allocation >= 25:
            risks.append(
                "The holding represents at least 25% of "
                "the portfolio."
            )

        if thesis.risk_level == "High":
            risks.append(
                "The saved thesis classifies this investment "
                "as high risk."
            )

        if review_overdue:
            risks.append(
                "The saved thesis review date has passed."
            )

        if target_reached:
            status = "Target Reached"
            recommendation = (
                "Revisit the original target and sell conditions "
                "before making a portfolio decision."
            )
        elif review_overdue:
            status = "Review Due"
            recommendation = (
                "Review and refresh the thesis, target, risks, "
                "and sell conditions."
            )
        elif current_price is None:
            status = "Insufficient Data"
            recommendation = (
                "Try the review again when live price data "
                "is available."
            )
        elif news["overall_sentiment"] == "negative" or len(risks) >= 2:
            status = "Needs Attention"
            recommendation = (
                "Compare the current risks with your recorded "
                "sell conditions and investment horizon."
            )
        else:
            status = "On Track"
            recommendation = (
                "Continue monitoring the thesis, target progress, "
                "news, and portfolio concentration."
            )

        return status, recommendation, signals, risks

    @staticmethod
    def _build_review(
        db: Session,
        user_id: int,
        thesis: InvestmentThesis,
        holding: Holding,
    ) -> dict:
        symbol = holding.symbol.strip().upper()

        try:
            current_price = PriceService.get_live_price(
                symbol
            )
        except Exception:
            current_price = None

        current_price = (
            round(float(current_price), 2)
            if current_price is not None
            else None
        )

        news = InvestmentReviewService._news_summary(
            symbol
        )

        position = (
            InvestmentReviewService._portfolio_position(
                db=db,
                user_id=user_id,
                holding=holding,
                current_price=current_price,
            )
        )

        target_progress_percent = None
        upside_to_target_percent = None

        if (
            current_price is not None
            and thesis.target_price is not None
            and thesis.target_price > 0
        ):
            target_progress_percent = round(
                current_price
                / thesis.target_price
                * 100,
                2,
            )
            upside_to_target_percent = round(
                (
                    thesis.target_price
                    - current_price
                )
                / current_price
                * 100,
                2,
            )

        (
            status,
            recommendation,
            signals,
            risks,
        ) = InvestmentReviewService._build_classification(
            thesis=thesis,
            current_price=current_price,
            news=news,
            position=position,
        )

        review_overdue = bool(
            thesis.review_date
            and thesis.review_date < date.today()
        )

        summary_parts = [
            f"{symbol} is classified as {status}.",
            recommendation,
        ]

        if target_progress_percent is not None:
            summary_parts.append(
                f"The current price is at "
                f"{target_progress_percent:.2f}% "
                f"of the saved target."
            )

        summary_parts.append(
            f"Recent news includes "
            f"{news['positive']} positive, "
            f"{news['neutral']} neutral, and "
            f"{news['negative']} negative articles."
        )

        return {
            "symbol": symbol,
            "company_name": holding.name,
            "status": status,
            "recommendation": recommendation,
            "summary": " ".join(summary_parts),
            "current_price": current_price,
            "target_price": thesis.target_price,
            "target_progress_percent": (
                target_progress_percent
            ),
            "upside_to_target_percent": (
                upside_to_target_percent
            ),
            "conviction_score": thesis.conviction_score,
            "risk_level": thesis.risk_level,
            "investment_horizon": (
                thesis.investment_horizon
            ),
            "review_date": thesis.review_date,
            "review_overdue": review_overdue,
            "thesis": thesis.thesis,
            "buy_reasons": thesis.buy_reasons,
            "sell_conditions": thesis.sell_conditions,
            "news": news,
            "position": position,
            "signals": signals,
            "risks": risks,
            "disclaimer": (
                "This review is informational research based on "
                "your saved thesis and available market data. "
                "It is not personalized financial advice or a "
                "buy/sell instruction."
            ),
        }

    @staticmethod
    def review_by_holding(
        db: Session,
        user_id: int,
        holding_id: int,
    ) -> dict:
        result = (
            InvestmentReviewService._get_thesis_and_holding(
                db=db,
                user_id=user_id,
                holding_id=holding_id,
            )
        )

        if result is None:
            raise ValueError(
                "No investment thesis was found for this holding."
            )

        thesis, holding = result

        return InvestmentReviewService._build_review(
            db=db,
            user_id=user_id,
            thesis=thesis,
            holding=holding,
        )

    @staticmethod
    def review_by_symbol(
        db: Session,
        user_id: int,
        symbol: str,
    ) -> dict:
        result = (
            InvestmentReviewService._get_thesis_and_holding(
                db=db,
                user_id=user_id,
                symbol=symbol,
            )
        )

        if result is None:
            raise ValueError(
                f"No investment thesis was found for "
                f"{symbol.strip().upper()}."
            )

        thesis, holding = result

        return InvestmentReviewService._build_review(
            db=db,
            user_id=user_id,
            thesis=thesis,
            holding=holding,
        )
