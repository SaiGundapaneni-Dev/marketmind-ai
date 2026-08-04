from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.portfolio_service import PortfolioService


class ScenarioSimulatorService:
    DISCLAIMER = (
        "Scenario results are deterministic illustrations based on "
        "the percentage changes entered. They are not forecasts, "
        "probabilities, or personalized financial advice."
    )

    PRESETS = [
        {
            "key": "market_correction",
            "name": "Broad Market Correction",
            "description": (
                "Apply a 15% decline to every priced holding."
            ),
            "mode": "all",
            "change_percent": -15.0,
        },
        {
            "key": "market_crash",
            "name": "Severe Market Crash",
            "description": (
                "Apply a 30% decline to every priced holding."
            ),
            "mode": "all",
            "change_percent": -30.0,
        },
        {
            "key": "tech_rally",
            "name": "Technology Rally",
            "description": (
                "Apply a 20% increase to common large-cap "
                "technology holdings."
            ),
            "mode": "symbols",
            "symbols": [
                "AAPL",
                "MSFT",
                "NVDA",
                "GOOGL",
                "GOOG",
                "META",
                "AMZN",
                "TSLA",
                "AMD",
                "PLTR",
            ],
            "change_percent": 20.0,
        },
        {
            "key": "ai_correction",
            "name": "AI Sector Correction",
            "description": (
                "Apply a 20% decline to common AI-related holdings."
            ),
            "mode": "symbols",
            "symbols": [
                "NVDA",
                "AMD",
                "PLTR",
                "MSFT",
                "GOOGL",
                "GOOG",
                "META",
            ],
            "change_percent": -20.0,
        },
    ]

    @staticmethod
    def list_presets(
        db: Session,
        user_id: int,
    ) -> dict:
        portfolio = PortfolioService.calculate(
            db,
            user_id,
        )

        priced = [
            item
            for item in portfolio.get(
                "holdings",
                [],
            )
            if item.get(
                "price_status"
            )
            == "available"
        ]

        portfolio_symbols = {
            str(item.get("symbol", "")).upper()
            for item in priced
            if item.get("symbol")
        }

        presets = []

        for preset in (
            ScenarioSimulatorService.PRESETS
        ):
            if preset["mode"] == "all":
                symbols = sorted(
                    portfolio_symbols
                )
            else:
                symbols = [
                    symbol
                    for symbol in preset.get(
                        "symbols",
                        [],
                    )
                    if symbol in portfolio_symbols
                ]

            presets.append({
                "key": preset["key"],
                "name": preset["name"],
                "description": preset[
                    "description"
                ],
                "changes": [
                    {
                        "symbol": symbol,
                        "change_percent": preset[
                            "change_percent"
                        ],
                    }
                    for symbol in symbols
                ],
            })

        return {
            "presets": presets,
        }

    @staticmethod
    def _risk_level(
        impact_percent: float,
    ) -> str:
        drawdown = abs(
            min(impact_percent, 0)
        )

        if drawdown >= 20:
            return "severe"

        if drawdown >= 10:
            return "high"

        if drawdown >= 5:
            return "medium"

        return "low"

    @staticmethod
    def _resilience_score(
        impact_percent: float,
    ) -> float:
        if impact_percent >= 0:
            return 100.0

        score = 100 + (
            impact_percent * 3
        )

        return round(
            max(0, min(score, 100)),
            2,
        )

    @staticmethod
    def _recommendation(
        impact_percent: float,
        risk_level: str,
        affected_count: int,
    ) -> tuple[str, str]:
        if risk_level == "severe":
            return (
                "Review portfolio construction",
                (
                    "This scenario produces a severe projected "
                    "drawdown. Review concentration, liquidity, "
                    "and whether the affected positions still "
                    "match their investment theses."
                ),
            )

        if risk_level == "high":
            return (
                "Stress-test concentration",
                (
                    "This scenario creates a material portfolio "
                    "decline. Focus on the holdings contributing "
                    "most of the projected loss."
                ),
            )

        if risk_level == "medium":
            return (
                "Monitor portfolio exposure",
                (
                    "The projected impact is meaningful but not "
                    "severe. Review the largest contributors "
                    "before changing allocation."
                ),
            )

        if impact_percent < 0:
            return (
                "No immediate rebalance indicated",
                (
                    "The scenario creates a limited projected "
                    "decline based on current position sizes."
                ),
            )

        return (
            "Review upside concentration",
            (
                f"{affected_count} holding"
                + (
                    ""
                    if affected_count == 1
                    else "s"
                )
                + " benefit from this scenario. Confirm that "
                "upside does not create excessive concentration."
            ),
        )

    @staticmethod
    def simulate(
        db: Session,
        user_id: int,
        scenario_name: str,
        changes: list,
    ) -> dict:
        portfolio = PortfolioService.calculate(
            db,
            user_id,
        )

        holdings = portfolio.get(
            "holdings",
            [],
        )

        current_total = float(
            portfolio.get(
                "summary",
                {},
            ).get(
                "total_value",
                0,
            )
            or 0
        )

        normalized_changes = {
            str(
                (
                    change.symbol
                    if hasattr(
                        change,
                        "symbol",
                    )
                    else change.get(
                        "symbol",
                        "",
                    )
                )
            )
            .strip()
            .upper(): float(
                (
                    change.change_percent
                    if hasattr(
                        change,
                        "change_percent",
                    )
                    else change.get(
                        "change_percent",
                        0,
                    )
                )
            )
            for change in changes
        }

        projected_total = current_total
        holding_impacts = []
        unaffected_count = 0
        warnings = []

        for holding in holdings:
            symbol = str(
                holding.get(
                    "symbol",
                    "",
                )
            ).upper()

            current_value = float(
                holding.get(
                    "current_value",
                    0,
                )
                or 0
            )

            if (
                holding.get(
                    "price_status"
                )
                != "available"
            ):
                warnings.append(
                    f"{symbol} was excluded because "
                    "live pricing is unavailable."
                )
                unaffected_count += 1
                continue

            if symbol not in (
                normalized_changes
            ):
                unaffected_count += 1
                continue

            change_percent = (
                normalized_changes[symbol]
            )

            projected_value = round(
                current_value
                * (
                    1
                    + change_percent
                    / 100
                ),
                2,
            )

            impact_value = round(
                projected_value
                - current_value,
                2,
            )

            projected_total += (
                impact_value
            )

            portfolio_impact_percent = (
                round(
                    (
                        impact_value
                        / current_total
                        * 100
                    ),
                    2,
                )
                if current_total > 0
                else 0
            )

            holding_impacts.append({
                "symbol": symbol,
                "name": holding.get(
                    "name",
                    symbol,
                ),
                "current_value": round(
                    current_value,
                    2,
                ),
                "change_percent": (
                    change_percent
                ),
                "projected_value": (
                    projected_value
                ),
                "impact_value": (
                    impact_value
                ),
                "portfolio_impact_percent": (
                    portfolio_impact_percent
                ),
            })

        holding_impacts.sort(
            key=lambda item: abs(
                item["impact_value"]
            ),
            reverse=True,
        )

        projected_total = round(
            projected_total,
            2,
        )

        impact_value = round(
            projected_total
            - current_total,
            2,
        )

        impact_percent = (
            round(
                impact_value
                / current_total
                * 100,
                2,
            )
            if current_total > 0
            else 0
        )

        risk_level = (
            ScenarioSimulatorService._risk_level(
                impact_percent
            )
        )

        resilience_score = (
            ScenarioSimulatorService._resilience_score(
                impact_percent
            )
        )

        recommendation, explanation = (
            ScenarioSimulatorService._recommendation(
                impact_percent,
                risk_level,
                len(holding_impacts),
            )
        )

        unknown_symbols = sorted(
            set(normalized_changes)
            - {
                str(
                    holding.get(
                        "symbol",
                        "",
                    )
                ).upper()
                for holding in holdings
            }
        )

        if unknown_symbols:
            warnings.append(
                "These symbols are not in the portfolio "
                "and were ignored: "
                + ", ".join(
                    unknown_symbols
                )
                + "."
            )

        if not holding_impacts:
            warnings.append(
                "No priced portfolio holdings matched "
                "the scenario changes."
            )

        return {
            "scenario_name": scenario_name,
            "current_portfolio_value": round(
                current_total,
                2,
            ),
            "projected_portfolio_value": (
                projected_total
            ),
            "impact_value": impact_value,
            "impact_percent": (
                impact_percent
            ),
            "affected_holdings_count": len(
                holding_impacts
            ),
            "unaffected_holdings_count": (
                unaffected_count
            ),
            "resilience_score": (
                resilience_score
            ),
            "risk_level": risk_level,
            "recommendation": (
                recommendation
            ),
            "explanation": explanation,
            "holding_impacts": (
                holding_impacts
            ),
            "warnings": warnings,
            "disclaimer": (
                ScenarioSimulatorService.DISCLAIMER
            ),
        }
