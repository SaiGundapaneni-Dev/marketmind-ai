class PortfolioHealthService:
    @staticmethod
    def calculate_health_score(
        holdings: list[dict],
        concentration_risk: dict,
        performance_insights: dict,
    ) -> dict:
        total_holdings = len(holdings)
        priced_holdings = [
            h for h in holdings
            if h["price_status"] == "available"
        ]
        priced_count = len(priced_holdings)

        if total_holdings >= 10:
            diversification_score = 25
        elif total_holdings >= 7:
            diversification_score = 20
        elif total_holdings >= 5:
            diversification_score = 15
        elif total_holdings >= 3:
            diversification_score = 10
        elif total_holdings >= 1:
            diversification_score = 5
        else:
            diversification_score = 0

        concentration_score = {
            "low": 25,
            "medium": 15,
            "high": 5,
            "unknown": 0,
        }.get(concentration_risk.get("risk_level", "unknown"), 0)

        profitable_count = performance_insights.get(
            "profitable_holdings_count",
            0,
        )
        profitability_score = round(
            (profitable_count / priced_count) * 25,
            2,
        ) if priced_count else 0.0

        pricing_coverage_score = round(
            (priced_count / total_holdings) * 25,
            2,
        ) if total_holdings else 0.0

        total_score = round(
            diversification_score
            + concentration_score
            + profitability_score
            + pricing_coverage_score,
            2,
        )

        if total_score >= 85:
            rating = "excellent"
            message = (
                "Your portfolio has strong overall health based on "
                "diversification, concentration, profitability, and "
                "pricing coverage."
            )
        elif total_score >= 70:
            rating = "good"
            message = (
                "Your portfolio is in good condition, with some room "
                "to improve diversification or concentration risk."
            )
        elif total_score >= 50:
            rating = "fair"
            message = (
                "Your portfolio has fair overall health. Review "
                "concentration, losing positions, and diversification."
            )
        else:
            rating = "weak"
            message = (
                "Your portfolio health score is currently weak. "
                "Several risk or data-quality areas may need attention."
            )

        return {
            "score": total_score,
            "rating": rating,
            "components": {
                "diversification_score": diversification_score,
                "concentration_score": concentration_score,
                "profitability_score": profitability_score,
                "pricing_coverage_score": pricing_coverage_score,
            },
            "message": message,
        }
