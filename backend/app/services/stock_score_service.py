class StockScoreService:

    @staticmethod
    def calculate_score(info: dict):
        score = 50
        reasons = []

        pe = info.get("trailingPE")
        revenue_growth = info.get("revenueGrowth")
        profit_margin = info.get("profitMargins")
        recommendation = info.get("recommendationKey")

        if pe and pe < 30:
            score += 10
            reasons.append("Reasonable P/E ratio")
        elif pe and pe > 60:
            score -= 10
            reasons.append("High P/E valuation")

        if revenue_growth and revenue_growth > 0.1:
            score += 15
            reasons.append("Revenue growth is positive")

        if profit_margin and profit_margin > 0.15:
            score += 15
            reasons.append("Healthy profit margin")

        if recommendation in ["buy", "strong_buy"]:
            score += 10
            reasons.append("Positive analyst recommendation")

        score = max(0, min(score, 100))

        return {
            "score": score,
            "reasons": reasons
        }