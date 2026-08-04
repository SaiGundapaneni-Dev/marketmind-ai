from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services.portfolio_intelligence_service import (
    PortfolioIntelligenceService,
)
from app.services.portfolio_service import PortfolioService


class DailyBriefService:
    DISCLAIMER = (
        "This brief is informational and is not personalized "
        "financial advice or a buy/sell instruction."
    )

    @staticmethod
    def _greeting(now: datetime) -> str:
        hour = now.hour

        if hour < 12:
            return "Good morning"

        if hour < 17:
            return "Good afternoon"

        return "Good evening"

    @staticmethod
    def _action(
        priorities: list[dict],
        health_score: float,
    ) -> tuple[str, str]:
        high_priority = next(
            (
                item
                for item in priorities
                if str(
                    item.get("severity", "")
                ).lower()
                == "high"
            ),
            None,
        )

        if high_priority:
            return (
                "REVIEW",
                (
                    high_priority.get("title")
                    or "A material portfolio issue needs review."
                ),
            )

        if priorities or health_score < 70:
            first = priorities[0] if priorities else {}

            return (
                "MONITOR",
                (
                    first.get("title")
                    or "Portfolio health is below the preferred range."
                ),
            )

        return (
            "HOLD",
            (
                "No material portfolio change currently requires "
                "an immediate decision."
            ),
        )

    @staticmethod
    def generate(
        db: Session,
        user_id: int,
        now: datetime | None = None,
    ) -> dict:
        current_time = now or datetime.now(
            timezone.utc
        )

        portfolio = PortfolioService.calculate(
            db,
            user_id,
        )

        intelligence = (
            PortfolioIntelligenceService.generate(
                db,
                user_id,
            )
        )

        summary = portfolio.get(
            "summary",
            {},
        )

        health = portfolio.get(
            "health_score",
            {},
        )

        concentration = portfolio.get(
            "concentration_risk",
            {},
        )

        priorities = intelligence.get(
            "priority_insights",
            [],
        )

        health_score = float(
            health.get("score", 0) or 0
        )

        action, action_reason = (
            DailyBriefService._action(
                priorities,
                health_score,
            )
        )

        brief_priorities = []

        for item in priorities[:5]:
            severity = str(
                item.get("severity", "info")
            ).lower()

            if severity not in {
                "high",
                "medium",
                "low",
                "info",
            }:
                severity = "info"

            brief_priorities.append({
                "category": item.get(
                    "category",
                    "portfolio",
                ),
                "severity": severity,
                "title": item.get(
                    "title",
                    "Portfolio update",
                ),
                "message": item.get(
                    "message",
                    "",
                ),
                "suggested_action": (
                    item.get(
                        "suggested_action"
                    )
                ),
                "symbols": [
                    symbol
                    for symbol in item.get(
                        "affected_symbols",
                        [],
                    )
                    if symbol
                ],
            })

        holdings_to_watch = []

        for item in intelligence.get(
            "holdings_to_watch",
            [],
        )[:5]:
            symbol = item.get("symbol")

            if not symbol:
                continue

            reason = item.get(
                "reason",
                "Material portfolio position",
            )

            holdings_to_watch.append(
                f"{symbol}: {reason}"
            )

        headline = (
            intelligence.get(
                "executive_summary"
            )
            or (
                "Your daily portfolio intelligence "
                "is ready."
            )
        )

        return {
            "generated_at": current_time,
            "greeting": (
                DailyBriefService._greeting(
                    current_time
                )
            ),
            "headline": headline,
            "action": action,
            "action_reason": action_reason,
            "portfolio_snapshot": {
                "total_value": float(
                    summary.get(
                        "total_value",
                        0,
                    )
                    or 0
                ),
                "total_profit": float(
                    summary.get(
                        "total_profit",
                        0,
                    )
                    or 0
                ),
                "total_return_percent": float(
                    summary.get(
                        "total_return_percent",
                        0,
                    )
                    or 0
                ),
                "holdings_count": int(
                    summary.get(
                        "holdings_count",
                        0,
                    )
                    or 0
                ),
                "health_score": health_score,
                "health_rating": str(
                    health.get(
                        "rating",
                        "unknown",
                    )
                ),
                "concentration_risk": str(
                    concentration.get(
                        "risk_level",
                        "unknown",
                    )
                ),
            },
            "priorities": brief_priorities,
            "positive_signals": (
                intelligence.get(
                    "strengths",
                    [],
                )[:5]
            ),
            "risks": (
                intelligence.get(
                    "risks",
                    [],
                )[:5]
            ),
            "recent_changes": (
                intelligence.get(
                    "recent_changes",
                    [],
                )[:5]
            ),
            "holdings_to_watch": (
                holdings_to_watch
            ),
            "recommended_questions": (
                intelligence.get(
                    "recommended_questions",
                    [],
                )[:6]
            ),
            "disclaimer": (
                DailyBriefService.DISCLAIMER
            ),
        }
