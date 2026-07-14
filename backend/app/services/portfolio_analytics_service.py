class PortfolioAnalyticsService:
    @staticmethod
    def calculate_concentration_risk(
        holdings: list[dict],
    ) -> dict:
        priced = [
            h for h in holdings
            if h["price_status"] == "available"
        ]

        if not priced:
            return {
                "risk_level": "unknown",
                "largest_position_percent": 0.0,
                "top_three_percent": 0.0,
                "concentrated_positions": [],
                "message": (
                    "Concentration risk could not be calculated "
                    "because no holdings have available prices."
                ),
            }

        ordered = sorted(
            priced,
            key=lambda h: h["allocation_percent"],
            reverse=True,
        )

        largest = ordered[0]["allocation_percent"]
        top_three = round(
            sum(h["allocation_percent"] for h in ordered[:3]),
            2,
        )

        concentrated = [
            {
                "symbol": h["symbol"],
                "name": h["name"],
                "allocation_percent": h["allocation_percent"],
            }
            for h in ordered
            if h["allocation_percent"] >= 20
        ]

        if largest >= 35 or top_three >= 75:
            level = "high"
            message = (
                "Your portfolio has high concentration risk. "
                "A large portion of the portfolio is controlled "
                "by one holding or the top three holdings."
            )
        elif largest >= 25 or top_three >= 60:
            level = "medium"
            message = (
                "Your portfolio has moderate concentration risk. "
                "Monitor the largest positions and consider whether "
                "the allocation matches your risk tolerance."
            )
        else:
            level = "low"
            message = (
                "Your portfolio has relatively low concentration "
                "risk based on current holding allocations."
            )

        return {
            "risk_level": level,
            "largest_position_percent": round(largest, 2),
            "top_three_percent": top_three,
            "concentrated_positions": concentrated,
            "message": message,
        }

    @staticmethod
    def calculate_performance_insights(
        holdings: list[dict],
    ) -> dict:
        priced = [
            h for h in holdings
            if h["price_status"] == "available"
        ]

        profitable = [h for h in priced if h["profit"] > 0]
        losing = [h for h in priced if h["profit"] < 0]
        breakeven = [h for h in priced if h["profit"] == 0]

        if not priced:
            return {
                "top_performer": None,
                "weakest_performer": None,
                "largest_profit_contributor": None,
                "largest_loss_contributor": None,
                "profitable_holdings_count": 0,
                "losing_holdings_count": 0,
                "breakeven_holdings_count": 0,
                "message": (
                    "Performance insights could not be calculated "
                    "because no holdings have available prices."
                ),
            }

        def performer(h: dict) -> dict:
            return {
                "symbol": h["symbol"],
                "name": h["name"],
                "profit": h["profit"],
                "profit_percent": h["profit_percent"],
            }

        top = max(priced, key=lambda h: h["profit_percent"])
        weakest = min(priced, key=lambda h: h["profit_percent"])

        return {
            "top_performer": performer(top),
            "weakest_performer": performer(weakest),
            "largest_profit_contributor": (
                performer(max(profitable, key=lambda h: h["profit"]))
                if profitable
                else None
            ),
            "largest_loss_contributor": (
                performer(min(losing, key=lambda h: h["profit"]))
                if losing
                else None
            ),
            "profitable_holdings_count": len(profitable),
            "losing_holdings_count": len(losing),
            "breakeven_holdings_count": len(breakeven),
            "message": (
                f"{len(profitable)} holdings are profitable, "
                f"{len(losing)} are currently at a loss, "
                f"and {len(breakeven)} are near break-even."
            ),
        }

    @staticmethod
    def generate_actionable_insights(
        holdings: list[dict],
        allocation: dict,
        concentration_risk: dict,
        performance_insights: dict,
        health_score: dict,
    ) -> dict:
        insights = []
        level = concentration_risk.get("risk_level", "unknown")
        largest = allocation.get("largest_holding")

        if level == "high":
            insights.append({
                "category": "concentration",
                "severity": "high",
                "title": "High concentration risk",
                "message": (
                    "A large percentage of your portfolio is "
                    "concentrated in one holding or the top three."
                ),
            })
        elif level == "medium":
            insights.append({
                "category": "concentration",
                "severity": "medium",
                "title": "Moderate concentration risk",
                "message": (
                    "Monitor your largest positions because their "
                    "movements may significantly affect total returns."
                ),
            })
        elif level == "low":
            insights.append({
                "category": "concentration",
                "severity": "low",
                "title": "Balanced position sizes",
                "message": (
                    "No single holding currently creates excessive "
                    "concentration based on configured thresholds."
                ),
            })

        if largest:
            insights.append({
                "category": "allocation",
                "severity": (
                    "medium"
                    if largest["allocation_percent"] >= 20
                    else "low"
                ),
                "title": f"{largest['symbol']} is your largest holding",
                "message": (
                    f"{largest['symbol']} represents "
                    f"{largest['allocation_percent']:.2f}% "
                    "of your current portfolio value."
                ),
            })

        top = performance_insights.get("top_performer")
        if top:
            insights.append({
                "category": "performance",
                "severity": "low",
                "title": f"{top['symbol']} is your top performer",
                "message": (
                    f"{top['symbol']} has returned "
                    f"{top['profit_percent']:.2f}% and contributed "
                    f"${top['profit']:.2f} in profit."
                ),
            })

        largest_profit = performance_insights.get(
            "largest_profit_contributor"
        )
        if largest_profit:
            insights.append({
                "category": "performance",
                "severity": "low",
                "title": "Largest profit contributor",
                "message": (
                    f"{largest_profit['symbol']} currently contributes "
                    f"the most dollar profit at "
                    f"${largest_profit['profit']:.2f}."
                ),
            })

        largest_loss = performance_insights.get(
            "largest_loss_contributor"
        )
        if largest_loss:
            insights.append({
                "category": "performance",
                "severity": "medium",
                "title": "Largest loss contributor",
                "message": (
                    f"{largest_loss['symbol']} currently has the "
                    f"largest unrealized loss at "
                    f"-${abs(largest_loss['profit']):.2f}, or "
                    f"{largest_loss['profit_percent']:.2f}%."
                ),
            })

        unpriced = [
            h for h in holdings
            if h["price_status"] == "unavailable"
        ]
        if unpriced:
            symbols = ", ".join(h["symbol"] for h in unpriced)
            insights.append({
                "category": "data_quality",
                "severity": "high",
                "title": "Missing live prices",
                "message": (
                    f"Live prices are unavailable for: {symbols}. "
                    "Portfolio calculations may be incomplete."
                ),
            })

        score = health_score.get("score", 0)
        rating = health_score.get("rating", "unknown")

        insights.append({
            "category": "health",
            "severity": (
                "low"
                if score >= 70
                else "medium"
                if score >= 50
                else "high"
            ),
            "title": f"Portfolio health rating: {rating.title()}",
            "message": (
                f"Your portfolio health score is {score:.2f}/100. "
                "The score reflects diversification, concentration, "
                "profitability, and price-data coverage."
            ),
        })

        order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(
            key=lambda item: order.get(item["severity"], 3)
        )

        return {
            "count": len(insights),
            "items": insights,
            "disclaimer": (
                "These insights are informational and are not "
                "personalized financial advice."
            ),
        }
