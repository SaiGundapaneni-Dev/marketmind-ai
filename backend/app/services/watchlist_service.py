from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.watchlist_repository import WatchlistRepository
from app.services.stock_analysis_service import StockAnalysisService


class WatchlistService:

    @staticmethod
    def list_items(db: Session, user_id: int):
        return WatchlistRepository.list_items(db, user_id)

    @staticmethod
    def create_item(db: Session, user_id: int, data):
        return WatchlistRepository.create(db, user_id, data)

    @staticmethod
    def update_item(
        db: Session,
        user_id: int,
        item_id: int,
        data,
    ):
        return WatchlistRepository.update(
            db,
            user_id,
            item_id,
            data,
        )

    @staticmethod
    def delete_item(
        db: Session,
        user_id: int,
        item_id: int,
    ):
        return WatchlistRepository.delete(
            db,
            user_id,
            item_id,
        )

    @staticmethod
    def _risk_level(report: dict) -> str:
        recommendation = report.get("recommendation") or {}
        label = str(recommendation.get("label", "")).lower()

        if label in {"high risk", "cautious"}:
            return "high"

        stock = report.get("stock") or {}
        score = float(
            (stock.get("marketmind_score") or {}).get("score") or 0
        )

        if score >= 70:
            return "low"

        if score >= 50:
            return "medium"

        return "high"

    @staticmethod
    def build_intelligence_item(item, report: dict) -> dict:
        stock = report.get("stock") or {}
        news = report.get("news_summary") or {}
        exposure = report.get("portfolio_exposure") or {}
        recommendation = report.get("recommendation") or {}
        score_data = stock.get("marketmind_score") or {}

        return {
            "id": item.id,
            "symbol": item.symbol,
            "company_name": (
                stock.get("company_name")
                or item.company_name
                or item.symbol
            ),
            "current_price": stock.get("current_price"),
            "currency": stock.get("currency"),
            "market_cap": stock.get("market_cap"),
            "marketmind_score": score_data.get("score"),
            "marketmind_rating": score_data.get("rating"),
            "research_classification": recommendation.get("label"),
            "confidence": recommendation.get("confidence"),
            "news_sentiment": news.get("overall_sentiment", "neutral"),
            "article_count": news.get("article_count", 0),
            "portfolio_owned": exposure.get("owned", False),
            "portfolio_allocation_percent": exposure.get(
                "allocation_percent",
                0.0,
            ),
            "risk_level": WatchlistService._risk_level(report),
            "bull_case": report.get("bull_case", [])[:3],
            "bear_case": report.get("bear_case", [])[:3],
            "updated_at": datetime.now(timezone.utc),
            "error": report.get("error"),
        }

    @staticmethod
    def analyze_watchlist(
        db: Session,
        user_id: int,
    ):
        items = WatchlistRepository.list_items(db, user_id)
        intelligence_items = []

        for item in items:
            report = StockAnalysisService.analyze(
                item.symbol,
                db,
                user_id=user_id,
            )
            intelligence_items.append(
                WatchlistService.build_intelligence_item(
                    item,
                    report,
                )
            )

        valid_items = [
            item
            for item in intelligence_items
            if not item.get("error")
        ]

        strong_candidates = sum(
            item.get("research_classification")
            == "strong research candidate"
            for item in intelligence_items
        )

        positive = sum(
            item.get("research_classification") == "positive"
            for item in intelligence_items
        )

        neutral = sum(
            item.get("research_classification") == "neutral"
            for item in intelligence_items
        )

        cautious_or_high_risk = sum(
            item.get("research_classification")
            in {"cautious", "high risk"}
            for item in intelligence_items
        )

        top_opportunity = max(
            valid_items,
            key=lambda item: (
                item.get("marketmind_score") or 0,
                item.get("confidence") or 0,
            ),
            default=None,
        )

        risk_order = {"high": 3, "medium": 2, "low": 1}

        highest_risk = max(
            valid_items,
            key=lambda item: risk_order.get(
                item.get("risk_level"),
                0,
            ),
            default=None,
        )

        most_positive_news = max(
            valid_items,
            key=lambda item: (
                item.get("news_sentiment") == "positive",
                item.get("article_count") or 0,
            ),
            default=None,
        )

        most_negative_news = max(
            valid_items,
            key=lambda item: (
                item.get("news_sentiment") == "negative",
                item.get("article_count") or 0,
            ),
            default=None,
        )

        return {
            "count": len(intelligence_items),
            "strong_candidates": strong_candidates,
            "positive": positive,
            "neutral": neutral,
            "cautious_or_high_risk": cautious_or_high_risk,
            "top_opportunity": top_opportunity,
            "highest_risk": highest_risk,
            "most_positive_news": most_positive_news,
            "most_negative_news": most_negative_news,
            "items": intelligence_items,
        }
