from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.investment_thesis import InvestmentThesis
from app.models.models import Holding, Portfolio
from app.repositories.watchlist_repository import (
    WatchlistRepository,
)
from app.services.news_service import NewsService
from app.services.portfolio_service import PortfolioService


class WatchtowerService:
    DISCLAIMER = (
        "Watchtower classifications are deterministic research "
        "signals based on available news, portfolio exposure, and "
        "saved thesis data. They are not personalized financial advice."
    )

    CRITICAL_TERMS = {
        "bankruptcy",
        "chapter 11",
        "fraud",
        "accounting irregularity",
        "sec investigation",
        "criminal investigation",
        "guidance cut",
        "cuts guidance",
        "withdraws guidance",
        "ceo resigns",
        "chief executive resigns",
        "default",
        "restatement",
        "major recall",
        "data breach",
    }

    IMPORTANT_TERMS = {
        "earnings miss",
        "misses estimates",
        "revenue miss",
        "profit warning",
        "downgrade",
        "regulatory",
        "antitrust",
        "lawsuit",
        "product delay",
        "layoffs",
        "restructuring",
        "debt",
        "margin pressure",
        "sales decline",
        "demand weakness",
        "guidance",
        "acquisition",
        "merger",
        "earnings",
    }

    SUPPORT_TERMS = {
        "beats estimates",
        "raises guidance",
        "record revenue",
        "strong demand",
        "revenue growth",
        "margin expansion",
        "new contract",
        "partnership",
        "approval",
        "upgrade",
    }

    CONTRADICTION_TERMS = {
        "miss",
        "cut",
        "decline",
        "weakness",
        "delay",
        "investigation",
        "downgrade",
        "lawsuit",
        "resigns",
        "fraud",
        "recall",
        "breach",
        "warning",
    }

    @staticmethod
    def _thesis_map(
        db: Session,
        user_id: int,
    ) -> dict[str, InvestmentThesis]:
        rows = (
            db.query(InvestmentThesis, Holding)
            .join(
                Holding,
                Holding.id == InvestmentThesis.holding_id,
            )
            .join(
                Portfolio,
                Portfolio.id == Holding.portfolio_id,
            )
            .filter(
                Portfolio.user_id == user_id
            )
            .all()
        )

        return {
            holding.symbol.strip().upper(): thesis
            for thesis, holding in rows
        }

    @staticmethod
    def _monitored_symbols(
        db: Session,
        user_id: int,
    ) -> tuple[dict[str, dict], dict]:
        portfolio = PortfolioService.calculate(
            db,
            user_id,
        )

        portfolio_items = {}

        for item in portfolio.get(
            "holdings",
            [],
        ):
            symbol = str(
                item.get("symbol", "")
            ).strip().upper()

            if not symbol:
                continue

            portfolio_items[symbol] = {
                "symbol": symbol,
                "company_name": item.get(
                    "name"
                ),
                "portfolio_owned": True,
                "portfolio_allocation_percent": float(
                    item.get(
                        "allocation_percent",
                        0,
                    )
                    or 0
                ),
                "source_type": "portfolio",
            }

        watchlist = (
            WatchlistRepository.list_items(
                db,
                user_id,
            )
        )

        monitored = dict(
            portfolio_items
        )

        for item in watchlist:
            symbol = item.symbol.strip().upper()

            if symbol in monitored:
                monitored[symbol][
                    "source_type"
                ] = "both"

                if not monitored[symbol].get(
                    "company_name"
                ):
                    monitored[symbol][
                        "company_name"
                    ] = item.company_name
            else:
                monitored[symbol] = {
                    "symbol": symbol,
                    "company_name": (
                        item.company_name
                    ),
                    "portfolio_owned": False,
                    "portfolio_allocation_percent": 0.0,
                    "source_type": "watchlist",
                }

        return monitored, portfolio

    @staticmethod
    def _classify_event(
        text: str,
        sentiment: str,
        relevance_score: float,
        allocation_percent: float,
    ) -> tuple[str, str, float]:
        normalized = (
            text or ""
        ).lower()

        critical_hits = [
            term
            for term in (
                WatchtowerService.CRITICAL_TERMS
            )
            if term in normalized
        ]

        important_hits = [
            term
            for term in (
                WatchtowerService.IMPORTANT_TERMS
            )
            if term in normalized
        ]

        score = 0.0
        event_type = "routine_update"

        if critical_hits:
            score += 75
            event_type = (
                critical_hits[0].replace(
                    " ",
                    "_",
                )
            )
        elif important_hits:
            score += 45
            event_type = (
                important_hits[0].replace(
                    " ",
                    "_",
                )
            )

        if sentiment == "negative":
            score += 15
        elif sentiment == "positive":
            score += 8

        score += min(
            relevance_score * 5,
            15,
        )

        if allocation_percent >= 25:
            score += 12
        elif allocation_percent >= 15:
            score += 7

        score = round(
            min(score, 100),
            2,
        )

        if score >= 75:
            severity = "critical"
        elif score >= 45:
            severity = "important"
        elif score >= 20:
            severity = "informational"
        else:
            severity = "noise"

        return severity, event_type, score

    @staticmethod
    def _thesis_impact(
        text: str,
        thesis: InvestmentThesis | None,
    ) -> str:
        if thesis is None:
            return "unknown"

        normalized = (
            text or ""
        ).lower()

        if any(
            term in normalized
            for term in (
                WatchtowerService.CONTRADICTION_TERMS
            )
        ):
            return "contradicts"

        if any(
            term in normalized
            for term in (
                WatchtowerService.SUPPORT_TERMS
            )
        ):
            return "supports"

        return "neutral"

    @staticmethod
    def _why_it_matters(
        severity: str,
        symbol: str,
        allocation_percent: float,
        thesis_impact: str,
        portfolio_owned: bool,
    ) -> str:
        parts = []

        if portfolio_owned:
            parts.append(
                f"{symbol} represents "
                f"{allocation_percent:.2f}% "
                "of portfolio value."
            )
        else:
            parts.append(
                f"{symbol} is currently on "
                "your research watchlist."
            )

        if thesis_impact == "contradicts":
            parts.append(
                "The event may weaken assumptions "
                "in the saved investment thesis."
            )
        elif thesis_impact == "supports":
            parts.append(
                "The event appears consistent with "
                "the saved investment thesis."
            )
        elif thesis_impact == "unknown":
            parts.append(
                "No saved thesis is available for "
                "comparison."
            )

        if severity == "critical":
            parts.append(
                "This event has high materiality "
                "and should be reviewed promptly."
            )
        elif severity == "important":
            parts.append(
                "This event may be material enough "
                "to affect monitoring or position sizing."
            )
        elif severity == "informational":
            parts.append(
                "The event is relevant but does not "
                "currently indicate a major thesis change."
            )
        else:
            parts.append(
                "The event appears low materiality "
                "and can usually be ignored."
            )

        return " ".join(parts)

    @staticmethod
    def _suggested_action(
        severity: str,
        thesis_impact: str,
        portfolio_owned: bool,
    ) -> str:
        if severity == "critical":
            return (
                "Review the underlying event and "
                "saved thesis before adding risk."
            )

        if thesis_impact == "contradicts":
            return (
                "Compare the event with your sell "
                "conditions and thesis assumptions."
            )

        if severity == "important":
            return (
                "Monitor follow-up disclosures and "
                "review the holding if evidence strengthens."
            )

        if severity == "informational":
            return (
                "No immediate action is required; "
                "continue normal monitoring."
            )

        if portfolio_owned:
            return (
                "Ignore this item unless stronger "
                "evidence emerges."
            )

        return (
            "Keep this as background research only."
        )

    @staticmethod
    def generate(
        db: Session,
        user_id: int,
        include_noise: bool = False,
    ) -> dict:
        monitored, _ = (
            WatchtowerService._monitored_symbols(
                db,
                user_id,
            )
        )

        try:
            thesis_map = (
                WatchtowerService._thesis_map(
                    db,
                    user_id,
                )
            )
        except Exception:
            thesis_map = {}

        alerts = []

        for symbol, metadata in monitored.items():
            payload = NewsService.search_news(
                symbol
            )

            for item in payload.get(
                "news",
                [],
            ):
                title = item.get("title") or ""
                summary = item.get("summary") or ""
                combined = (
                    f"{title} {summary}"
                ).strip()

                sentiment = str(
                    item.get(
                        "sentiment",
                        "neutral",
                    )
                ).lower()

                relevance_score = float(
                    item.get(
                        "relevance_score",
                        0,
                    )
                    or 0
                )

                (
                    severity,
                    event_type,
                    materiality_score,
                ) = (
                    WatchtowerService._classify_event(
                        combined,
                        sentiment,
                        relevance_score,
                        metadata[
                            "portfolio_allocation_percent"
                        ],
                    )
                )

                thesis = thesis_map.get(
                    symbol
                )

                thesis_impact = (
                    WatchtowerService._thesis_impact(
                        combined,
                        thesis,
                    )
                )

                if (
                    severity == "noise"
                    and not include_noise
                ):
                    continue

                alerts.append({
                    "symbol": symbol,
                    "company_name": (
                        metadata.get(
                            "company_name"
                        )
                        or payload.get(
                            "company_name"
                        )
                    ),
                    "source_type": metadata[
                        "source_type"
                    ],
                    "severity": severity,
                    "event_type": event_type,
                    "title": title or (
                        f"{symbol} news update"
                    ),
                    "summary": (
                        summary or None
                    ),
                    "publisher": item.get(
                        "publisher"
                    ),
                    "link": item.get(
                        "link"
                    ),
                    "published_at": item.get(
                        "published_at"
                    ),
                    "sentiment": sentiment,
                    "relevance_score": (
                        relevance_score
                    ),
                    "materiality_score": (
                        materiality_score
                    ),
                    "portfolio_owned": metadata[
                        "portfolio_owned"
                    ],
                    "portfolio_allocation_percent": (
                        metadata[
                            "portfolio_allocation_percent"
                        ]
                    ),
                    "thesis_exists": (
                        thesis is not None
                    ),
                    "thesis_impact": (
                        thesis_impact
                    ),
                    "why_it_matters": (
                        WatchtowerService._why_it_matters(
                            severity,
                            symbol,
                            metadata[
                                "portfolio_allocation_percent"
                            ],
                            thesis_impact,
                            metadata[
                                "portfolio_owned"
                            ],
                        )
                    ),
                    "suggested_action": (
                        WatchtowerService._suggested_action(
                            severity,
                            thesis_impact,
                            metadata[
                                "portfolio_owned"
                            ],
                        )
                    ),
                })

        rank = {
            "critical": 0,
            "important": 1,
            "informational": 2,
            "noise": 3,
        }

        alerts.sort(
            key=lambda item: (
                rank[item["severity"]],
                -item[
                    "materiality_score"
                ],
            )
        )

        counts = {
            severity: sum(
                item["severity"]
                == severity
                for item in alerts
            )
            for severity in (
                "critical",
                "important",
                "informational",
                "noise",
            )
        }

        material_count = (
            counts["critical"]
            + counts["important"]
        )

        silence_filter_active = (
            material_count == 0
        )

        if not monitored:
            silence_message = (
                "Add portfolio holdings or watchlist "
                "symbols to begin monitoring."
            )
        elif silence_filter_active:
            silence_message = (
                "No material events detected. "
                "Ignore today's market noise; "
                "your monitored theses have no "
                "high-priority news signal."
            )
        else:
            silence_message = (
                f"{material_count} material event"
                + (
                    ""
                    if material_count == 1
                    else "s"
                )
                + " deserve review."
            )

        return {
            "generated_at": datetime.now(
                timezone.utc
            ),
            "monitored_symbols": len(
                monitored
            ),
            "critical_count": counts[
                "critical"
            ],
            "important_count": counts[
                "important"
            ],
            "informational_count": counts[
                "informational"
            ],
            "noise_count": counts[
                "noise"
            ],
            "silence_filter_active": (
                silence_filter_active
            ),
            "silence_message": (
                silence_message
            ),
            "alerts": alerts[:50],
            "disclaimer": (
                WatchtowerService.DISCLAIMER
            ),
        }
