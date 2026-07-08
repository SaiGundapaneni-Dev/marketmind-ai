class StockScoreService:

    @staticmethod
    def _is_valid_number(value):
        return isinstance(value, (int, float)) and value == value

    @staticmethod
    def _rating(score: int):
        if score >= 80:
            return (
                "Strong",
                "Strong fundamentals based on available valuation, growth, profitability, and analyst indicators."
            )

        if score >= 60:
            return (
                "Good",
                "Generally positive fundamentals, but some areas should be reviewed before making an investment decision."
            )

        if score >= 40:
            return (
                "Neutral",
                "Mixed fundamental signals. More research is recommended."
            )

        return (
            "Weak",
            "Several fundamental indicators appear weak based on the currently available data."
        )

    @staticmethod
    def calculate_score(info: dict):
        score = 50
        reasons = []
        warnings = []

        pe = info.get("trailingPE")
        revenue_growth = info.get("revenueGrowth")
        profit_margin = info.get("profitMargins")
        recommendation = info.get("recommendationKey")

        # P/E valuation
        if StockScoreService._is_valid_number(pe):
            if pe <= 0:
                warnings.append("P/E ratio is unavailable or not meaningful.")
            elif pe < 25:
                score += 10
                reasons.append("Reasonable P/E valuation.")
            elif pe <= 50:
                reasons.append("Moderate P/E valuation.")
            else:
                score -= 10
                reasons.append("High P/E valuation.")
        else:
            warnings.append("P/E ratio is missing.")

        # Revenue growth
        if StockScoreService._is_valid_number(revenue_growth):
            if revenue_growth > 1:
                warnings.append("Revenue growth appears unusually high and may need verification.")
                score += 5
                reasons.append("Revenue growth is positive, but data should be verified.")
            elif revenue_growth > 0.15:
                score += 15
                reasons.append("Strong positive revenue growth.")
            elif revenue_growth > 0:
                score += 5
                reasons.append("Revenue growth is positive.")
            else:
                score -= 10
                reasons.append("Revenue growth is negative.")
        else:
            warnings.append("Revenue growth data is missing.")

        # Profit margin
        if StockScoreService._is_valid_number(profit_margin):
            if profit_margin > 1:
                warnings.append("Profit margin appears unusually high and may need verification.")
                score += 5
                reasons.append("Profit margin is positive, but data should be verified.")
            elif profit_margin > 0.20:
                score += 15
                reasons.append("Healthy profit margin.")
            elif profit_margin > 0:
                score += 5
                reasons.append("Company is profitable.")
            else:
                score -= 10
                reasons.append("Company has negative profit margin.")
        else:
            warnings.append("Profit margin data is missing.")

        # Analyst recommendation
        if recommendation in ["buy", "strong_buy"]:
            score += 10
            reasons.append("Positive analyst recommendation.")
        elif recommendation in ["sell", "strong_sell"]:
            score -= 10
            reasons.append("Negative analyst recommendation.")
        elif recommendation:
            reasons.append("Analyst recommendation is neutral or mixed.")
        else:
            warnings.append("Analyst recommendation is missing.")

        score = max(0, min(score, 100))
        rating, interpretation = StockScoreService._rating(score)

        return {
            "score": score,
            "rating": rating,
            "interpretation": interpretation,
            "reasons": reasons,
            "warnings": warnings,
        }