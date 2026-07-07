class StockScoreService:

    @staticmethod
    def calculate_score(info: dict):
        score = 50
        reasons = []

        pe = info.get("trailingPE")
        revenue_growth = info.get("revenueGrowth")
        profit_margin = info.get("profitMargins")
        recommendation = info.get("recommendationKey")

        # Valuation
        if pe is not None:
            if pe < 30:
                score += 10
                reasons.append("Reasonable P/E valuation")
            elif pe > 60:
                score -= 10
                reasons.append("High P/E valuation")
            else:
                reasons.append("Moderate P/E valuation")

        # Revenue growth
        if revenue_growth is not None:
            if revenue_growth > 0.10:
                score += 15
                reasons.append("Strong positive revenue growth")
            elif revenue_growth > 0:
                score += 5
                reasons.append("Revenue growth is positive")
            else:
                score -= 10
                reasons.append("Revenue growth is negative")

        # Profitability
        if profit_margin is not None:
            if profit_margin > 0.15:
                score += 15
                reasons.append("Healthy profit margin")
            elif profit_margin > 0:
                score += 5
                reasons.append("Company is profitable")
            else:
                score -= 10
                reasons.append("Company has negative profit margin")

        # Analyst recommendation
        if recommendation in ["buy", "strong_buy"]:
            score += 10
            reasons.append("Positive analyst recommendation")
        elif recommendation in ["sell", "strong_sell"]:
            score -= 10
            reasons.append("Negative analyst recommendation")

        score = max(0, min(score, 100))

        if score >= 80:
            rating = "Strong"
            interpretation = (
                "Strong fundamentals based on the available valuation, "
                "growth, profitability, and analyst indicators."
            )
        elif score >= 60:
            rating = "Good"
            interpretation = (
                "Generally positive fundamentals, but some areas should "
                "be reviewed before making an investment decision."
            )
        elif score >= 40:
            rating = "Neutral"
            interpretation = (
                "Mixed fundamental signals. More research is recommended."
            )
        else:
            rating = "Weak"
            interpretation = (
                "Several fundamental indicators appear weak based on "
                "the currently available data."
            )

        return {
            "score": score,
            "rating": rating,
            "interpretation": interpretation,
            "reasons": reasons,
        }