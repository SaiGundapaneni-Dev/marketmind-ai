from sqlalchemy.orm import Session

from app.services.portfolio_service import PortfolioService


class PortfolioScoreService:
    DISCLAIMER = (
        "Portfolio scores are informational estimates based on available "
        "portfolio data and are not personalized financial advice."
    )

    WEIGHTS = {
        "diversification": 0.20,
        "concentration": 0.20,
        "performance": 0.20,
        "portfolio_health": 0.20,
        "market_exposure": 0.20,
    }

    @staticmethod
    def _clamp(value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)

    @staticmethod
    def _rating(score: float) -> str:
        if score >= 85:
            return "excellent"
        if score >= 70:
            return "good"
        if score >= 50:
            return "fair"
        return "weak"

    @staticmethod
    def _category(score: float, summary: str, factors: list[str], action: str) -> dict:
        score = PortfolioScoreService._clamp(score)
        return {
            "score": score,
            "rating": PortfolioScoreService._rating(score),
            "summary": summary,
            "factors": factors,
            "suggested_action": action,
        }

    @staticmethod
    def _diversification(holdings: list[dict], allocation: dict) -> dict:
        priced = [h for h in holdings if h.get("price_status") == "available"]
        count = len(priced)
        score = 100 if count >= 12 else 90 if count >= 10 else 78 if count >= 7 else 65 if count >= 5 else 45 if count >= 3 else 25 if count else 0
        asset_types = {str(h.get("asset_type") or "unknown").lower() for h in priced}
        score += 10 if len(asset_types) >= 4 else 7 if len(asset_types) == 3 else 4 if len(asset_types) == 2 else 0
        largest = allocation.get("largest_holding") or {}
        largest_pct = float(largest.get("allocation_percent", 0) or 0)
        score -= 25 if largest_pct >= 35 else 15 if largest_pct >= 25 else 8 if largest_pct >= 20 else 0
        factors = [
            f"{count} priced holdings are included in the score.",
            f"{len(asset_types)} asset-type categories are represented.",
        ]
        if largest:
            factors.append(f"The largest holding is {largest.get('symbol', 'unknown')} at {largest_pct:.2f}%.")
        action = (
            "Consider adding more high-quality holdings or broad-market funds."
            if count < 5
            else "Review whether the largest holding should remain above 25%."
            if largest_pct >= 25
            else "Maintain position-size discipline as the portfolio grows."
        )
        return PortfolioScoreService._category(
            score,
            "Diversification reflects holding count, asset-type variety, and largest-position size.",
            factors,
            action,
        )

    @staticmethod
    def _concentration(concentration: dict) -> dict:
        risk = concentration.get("risk_level", "unknown")
        largest = float(concentration.get("largest_position_percent", 0) or 0)
        top_three = float(concentration.get("top_three_percent", 0) or 0)
        score = {"low": 90, "medium": 65, "high": 35}.get(risk, 0)
        score += 8 if largest < 15 else -10 if largest >= 35 else 0
        score += 7 if top_three < 45 else -10 if top_three >= 75 else 0
        return PortfolioScoreService._category(
            score,
            "Concentration measures dependence on the largest holding and top three positions.",
            [
                f"Concentration risk is {str(risk).title()}.",
                f"The largest position represents {largest:.2f}%.",
                f"The top three positions represent {top_three:.2f}%.",
            ],
            "Review whether large positions match your risk tolerance."
            if risk in {"medium", "high"}
            else "Continue monitoring position sizes as values change.",
        )

    @staticmethod
    def _performance(summary: dict, performance: dict) -> dict:
        total_return = float(summary.get("total_return_percent", 0) or 0)
        priced = int(summary.get("priced_holdings_count", 0) or 0)
        profitable = int(performance.get("profitable_holdings_count", 0) or 0)
        losing = int(performance.get("losing_holdings_count", 0) or 0)
        ratio = profitable / priced if priced else 0
        score = 45 + ratio * 35
        score += 20 if total_return >= 25 else 15 if total_return >= 10 else 8 if total_return >= 0 else -20 if total_return <= -20 else -10
        factors = [
            f"Total portfolio return is {total_return:.2f}%.",
            f"{profitable} of {priced} priced holdings are profitable.",
            f"{losing} priced holdings are below average cost.",
        ]
        top = performance.get("top_performer")
        weakest = performance.get("weakest_performer")
        if top:
            factors.append(f"{top.get('symbol')} is the top performer at {float(top.get('profit_percent', 0) or 0):.2f}%.")
        if weakest:
            factors.append(f"{weakest.get('symbol')} is the weakest performer at {float(weakest.get('profit_percent', 0) or 0):.2f}%.")
        return PortfolioScoreService._category(
            score,
            "Performance reflects total return and the share of profitable priced holdings.",
            factors,
            "Review losing holdings against their original thesis."
            if losing
            else "Monitor whether gains are becoming concentrated in a few holdings.",
        )

    @staticmethod
    def _health(health: dict) -> dict:
        score = float(health.get("score", 0) or 0)
        components = health.get("components", {})
        return PortfolioScoreService._category(
            score,
            health.get("message", "Portfolio health combines diversification, concentration, profitability, and pricing coverage."),
            [
                f"Diversification component: {float(components.get('diversification_score', 0) or 0):.2f}/25.",
                f"Concentration component: {float(components.get('concentration_score', 0) or 0):.2f}/25.",
                f"Profitability component: {float(components.get('profitability_score', 0) or 0):.2f}/25.",
                f"Pricing coverage component: {float(components.get('pricing_coverage_score', 0) or 0):.2f}/25.",
            ],
            "Focus first on the lowest health-score component."
            if score < 85
            else "Maintain the habits supporting the current health score.",
        )

    @staticmethod
    def _market_exposure(summary: dict, allocation: dict, holdings: list[dict]) -> dict:
        total = int(summary.get("holdings_count", 0) or 0)
        priced = int(summary.get("priced_holdings_count", 0) or 0)
        unpriced = int(summary.get("unpriced_holdings_count", 0) or 0)
        coverage = priced / total if total else 0
        asset_types = {str(h.get("asset_type") or "unknown").lower() for h in holdings if h.get("price_status") == "available"}
        score = coverage * 70 + (30 if len(asset_types) >= 4 else 24 if len(asset_types) == 3 else 16 if len(asset_types) == 2 else 8 if len(asset_types) == 1 else 0)
        factors = [
            f"Live prices are available for {priced} of {total} holdings.",
            f"{len(asset_types)} priced asset-type categories are represented.",
        ]
        factors.extend(
            f"{item.get('asset_type', 'unknown')}: {float(item.get('allocation_percent', 0) or 0):.2f}%"
            for item in allocation.get("by_asset_type", [])[:5]
        )
        return PortfolioScoreService._category(
            score,
            "Market exposure reflects pricing coverage and recorded asset-type variety.",
            factors,
            "Resolve missing price data before relying on the full score."
            if unpriced
            else "Confirm that the asset-type mix matches your intended strategy.",
        )

    @staticmethod
    def generate(db: Session, user_id: int) -> dict:
        portfolio = PortfolioService.calculate(db, user_id)
        summary = portfolio.get("summary", {})
        allocation = portfolio.get("allocation", {})
        concentration = portfolio.get("concentration_risk", {})
        performance = portfolio.get("performance_insights", {})
        health = portfolio.get("health_score", {})
        holdings = portfolio.get("holdings", [])

        if int(summary.get("holdings_count", 0) or 0) == 0:
            empty = {
                "score": 0.0,
                "rating": "weak",
                "summary": "A score cannot be calculated without holdings.",
                "factors": ["No portfolio holdings are available."],
                "suggested_action": "Add your first holding to begin portfolio scoring.",
            }
            return {
                "overall_score": 0.0,
                "rating": "empty",
                "summary": "Your portfolio is empty. Add at least one holding to generate a score.",
                "scores": {name: dict(empty) for name in PortfolioScoreService.WEIGHTS},
                "strengths": [],
                "weaknesses": ["No holdings are available for analysis."],
                "improvement_suggestions": ["Add at least one holding with quantity and average price."],
                "disclaimer": PortfolioScoreService.DISCLAIMER,
            }

        scores = {
            "diversification": PortfolioScoreService._diversification(holdings, allocation),
            "concentration": PortfolioScoreService._concentration(concentration),
            "performance": PortfolioScoreService._performance(summary, performance),
            "portfolio_health": PortfolioScoreService._health(health),
            "market_exposure": PortfolioScoreService._market_exposure(summary, allocation, holdings),
        }
        overall = PortfolioScoreService._clamp(sum(scores[name]["score"] * weight for name, weight in PortfolioScoreService.WEIGHTS.items()))
        ordered = sorted(scores.items(), key=lambda item: item[1]["score"], reverse=True)
        strengths = [f"{name.replace('_', ' ').title()} is rated {details['rating'].title()} at {details['score']:.2f}/100." for name, details in ordered if details["score"] >= 70][:3]
        weaknesses = [f"{name.replace('_', ' ').title()} is rated {details['rating'].title()} at {details['score']:.2f}/100." for name, details in reversed(ordered) if details["score"] < 70][:3]
        weakest = sorted(scores.items(), key=lambda item: item[1]["score"])[:3]
        suggestions = [details["suggested_action"] for _, details in weakest]
        strongest_name, strongest = ordered[0]
        weakest_name, weakest_details = ordered[-1]
        return {
            "overall_score": overall,
            "rating": PortfolioScoreService._rating(overall),
            "summary": (
                f"Your portfolio score is {overall:.2f}/100. The strongest category is "
                f"{strongest_name.replace('_', ' ')} at {strongest['score']:.2f}, while the main "
                f"area for improvement is {weakest_name.replace('_', ' ')} at {weakest_details['score']:.2f}."
            ),
            "scores": scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": suggestions,
            "disclaimer": PortfolioScoreService.DISCLAIMER,
        }
