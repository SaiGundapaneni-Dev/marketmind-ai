from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.investment_thesis import InvestmentThesis
from app.models.models import Holding, Portfolio
from app.services.portfolio_intelligence_service import (
    PortfolioIntelligenceService,
)
from app.services.portfolio_service import PortfolioService


class AICoachService:
    DISCLAIMER = (
        "This AI Coach is informational and does not provide "
        "personalized financial advice or buy/sell instructions."
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
    def _get_thesis_map(
        db: Session,
        user_id: int,
    ) -> dict[int, InvestmentThesis]:
        rows = (
            db.query(InvestmentThesis)
            .join(
                Holding,
                Holding.id == InvestmentThesis.holding_id,
            )
            .join(
                Portfolio,
                Portfolio.id == Holding.portfolio_id,
            )
            .filter(Portfolio.user_id == user_id)
            .all()
        )

        return {
            thesis.holding_id: thesis
            for thesis in rows
        }

    @staticmethod
    def _priority_from_intelligence(
        intelligence: dict,
    ) -> list[dict]:
        priorities = []

        for item in intelligence.get(
            "priority_insights",
            [],
        )[:5]:
            severity = str(
                item.get("severity", "medium")
            ).lower()

            if severity not in {
                "high",
                "medium",
                "low",
            }:
                severity = "medium"

            affected = item.get(
                "affected_symbols",
                [],
            )

            priorities.append({
                "severity": severity,
                "category": item.get(
                    "category",
                    "portfolio",
                ),
                "title": item.get(
                    "title",
                    "Portfolio review",
                ),
                "message": item.get(
                    "message",
                    "",
                ),
                "suggested_action": item.get(
                    "suggested_action",
                    "Review this item.",
                ),
                "symbol": (
                    affected[0]
                    if affected
                    else None
                ),
            })

        return priorities

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

        summary = portfolio.get("summary", {})
        health = portfolio.get(
            "health_score",
            {},
        )
        holdings = portfolio.get(
            "holdings",
            [],
        )

        health_score = float(
            health.get("score", 0) or 0
        )
        health_rating = str(
            health.get("rating", "unknown")
        )

        priorities = (
            AICoachService._priority_from_intelligence(
                intelligence
            )
        )

        positives = []
        recommendations = []

        try:
            thesis_map = (
                AICoachService._get_thesis_map(
                    db,
                    user_id,
                )
            )
        except Exception:
            thesis_map = {}

        today = current_time.date()

        for holding in holdings:
            holding_id = holding.get("id")
            symbol = holding.get("symbol")
            allocation = float(
                holding.get(
                    "allocation_percent",
                    0,
                )
                or 0
            )
            profit_percent = float(
                holding.get(
                    "profit_percent",
                    0,
                )
                or 0
            )

            thesis = thesis_map.get(
                holding_id
            )

            if allocation >= 25:
                priorities.append({
                    "severity": "high",
                    "category": "concentration",
                    "title": (
                        f"{symbol} is overweight"
                    ),
                    "message": (
                        f"{symbol} represents "
                        f"{allocation:.2f}% of "
                        "portfolio value."
                    ),
                    "suggested_action": (
                        "Review the position before "
                        "adding more capital."
                    ),
                    "symbol": symbol,
                })

            if profit_percent <= -15:
                priorities.append({
                    "severity": "medium",
                    "category": "performance",
                    "title": (
                        f"{symbol} needs thesis review"
                    ),
                    "message": (
                        f"{symbol} is "
                        f"{profit_percent:.2f}% below "
                        "its recorded average cost."
                    ),
                    "suggested_action": (
                        "Confirm whether the original "
                        "investment thesis still holds."
                    ),
                    "symbol": symbol,
                })

            if thesis is None:
                priorities.append({
                    "severity": "medium",
                    "category": "thesis",
                    "title": (
                        f"{symbol} has no saved thesis"
                    ),
                    "message": (
                        "The position does not have a "
                        "recorded reason for ownership."
                    ),
                    "suggested_action": (
                        "Create a thesis, target, risk "
                        "level, and sell conditions."
                    ),
                    "symbol": symbol,
                })
            else:
                if (
                    thesis.review_date
                    and thesis.review_date < today
                ):
                    days_overdue = (
                        today
                        - thesis.review_date
                    ).days

                    priorities.append({
                        "severity": "medium",
                        "category": "thesis",
                        "title": (
                            f"{symbol} review is overdue"
                        ),
                        "message": (
                            f"The saved thesis review "
                            f"date passed {days_overdue} "
                            "day"
                            + (
                                ""
                                if days_overdue == 1
                                else "s"
                            )
                            + " ago."
                        ),
                        "suggested_action": (
                            "Open the thesis and refresh "
                            "the assumptions."
                        ),
                        "symbol": symbol,
                    })

                if (
                    thesis.conviction_score is not None
                    and thesis.conviction_score >= 8
                    and profit_percent >= 0
                ):
                    positives.append({
                        "severity": "positive",
                        "category": "thesis",
                        "title": (
                            f"{symbol} remains a "
                            "high-conviction winner"
                        ),
                        "message": (
                            f"Conviction is "
                            f"{thesis.conviction_score}/10 "
                            "and the position is currently "
                            f"up {profit_percent:.2f}%."
                        ),
                        "suggested_action": (
                            "Continue monitoring without "
                            "reacting to ordinary noise."
                        ),
                        "symbol": symbol,
                    })

        for strength in intelligence.get(
            "strengths",
            [],
        )[:3]:
            positives.append({
                "severity": "positive",
                "category": "portfolio",
                "title": "Portfolio strength",
                "message": strength,
                "suggested_action": (
                    "Maintain discipline and continue "
                    "monitoring."
                ),
                "symbol": None,
            })

        severity_rank = {
            "high": 0,
            "medium": 1,
            "low": 2,
        }

        unique = []
        seen = set()

        for item in sorted(
            priorities,
            key=lambda value: severity_rank.get(
                value.get("severity"),
                3,
            ),
        ):
            key = (
                item.get("category"),
                item.get("title"),
                item.get("symbol"),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        priorities = unique[:6]

        if priorities:
            for item in priorities[:3]:
                recommendations.append(
                    item["suggested_action"]
                )
        else:
            recommendations.extend([
                (
                    "No material portfolio issue "
                    "requires action today."
                ),
                (
                    "Avoid unnecessary trading and "
                    "ignore ordinary market noise."
                ),
            ])

        if health_score >= 80:
            recommendations.append(
                "Preserve the habits supporting the "
                "current portfolio health score."
            )
        elif health_score < 70:
            recommendations.append(
                "Prioritize diversification and "
                "concentration before adding risk."
            )

        issue_count = len(priorities)

        if issue_count <= 2:
            review_minutes = 2
        elif issue_count <= 4:
            review_minutes = 5
        else:
            review_minutes = 8

        status = (
            "healthy"
            if health_score >= 80
            else "stable"
            if health_score >= 70
            else "needs attention"
        )

        if priorities:
            headline = (
                f"I found {issue_count} item"
                + (
                    ""
                    if issue_count == 1
                    else "s"
                )
                + " worth reviewing today."
            )
        else:
            headline = (
                "Nothing material requires "
                "portfolio action today."
            )

        return {
            "generated_at": current_time,
            "greeting": (
                AICoachService._greeting(
                    current_time
                )
            ),
            "portfolio_status": status,
            "health_score": health_score,
            "health_rating": health_rating,
            "headline": headline,
            "priorities": priorities,
            "positive_highlights": (
                positives[:5]
            ),
            "recommendations": list(
                dict.fromkeys(
                    recommendations
                )
            )[:5],
            "estimated_review_minutes": (
                review_minutes
            ),
            "no_action_required": (
                len(priorities) == 0
            ),
            "disclaimer": (
                AICoachService.DISCLAIMER
            ),
        }
