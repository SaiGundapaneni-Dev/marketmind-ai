from sqlalchemy.orm import Session

from app.services.portfolio_history_service import PortfolioHistoryService
from app.services.portfolio_service import PortfolioService


class PortfolioIntelligenceService:
    DISCLAIMER = (
        "These insights are informational and are not personalized "
        "financial advice."
    )

    @staticmethod
    def generate(db: Session, user_id: int) -> dict:
        portfolio = PortfolioService.calculate(db, user_id)
        changes = PortfolioHistoryService.get_changes(db, user_id)

        summary = portfolio.get("summary", {})
        allocation = portfolio.get("allocation", {})
        concentration = portfolio.get("concentration_risk", {})
        performance = portfolio.get("performance_insights", {})
        health = portfolio.get("health_score", {})
        holdings = portfolio.get("holdings", [])

        holdings_count = summary.get("holdings_count", 0)

        if holdings_count == 0:
            return {
                "portfolio_status": "empty",
                "executive_summary": (
                    "Your portfolio is empty. Add at least one holding "
                    "to begin receiving personalized intelligence."
                ),
                "priority_insights": [],
                "strengths": [],
                "risks": [],
                "opportunities": [
                    "Add your first holding to begin portfolio analysis."
                ],
                "holdings_to_watch": [],
                "recent_changes": changes.get("summary", []),
                "recommended_questions": [
                    "How does Vestora calculate portfolio health?",
                    "What information should I track for each stock?",
                ],
                "disclaimer": PortfolioIntelligenceService.DISCLAIMER,
            }

        total_value = summary.get("total_value", 0)
        total_profit = summary.get("total_profit", 0)
        total_return = summary.get("total_return_percent", 0)
        health_score = health.get("score", 0)
        health_rating = health.get("rating", "unknown")
        risk_level = concentration.get("risk_level", "unknown")

        largest_holding = allocation.get("largest_holding")
        top_performer = performance.get("top_performer")
        weakest_performer = performance.get("weakest_performer")
        largest_profit = performance.get("largest_profit_contributor")
        largest_loss = performance.get("largest_loss_contributor")
        profitable_count = performance.get("profitable_holdings_count", 0)
        losing_count = performance.get("losing_holdings_count", 0)

        priorities = []

        if risk_level in {"high", "medium"}:
            priorities.append({
                "priority": 1,
                "category": "concentration",
                "severity": "high" if risk_level == "high" else "medium",
                "title": f"{risk_level.title()} concentration risk",
                "message": (
                    f"The top three holdings represent "
                    f"{concentration.get('top_three_percent', 0):.2f}% "
                    "of portfolio value."
                ),
                "evidence": [
                    f"Largest position: {concentration.get('largest_position_percent', 0):.2f}%",
                    f"Top three positions: {concentration.get('top_three_percent', 0):.2f}%",
                ],
                "suggested_action": (
                    "Review whether your largest positions still match "
                    "your risk tolerance and investment thesis."
                ),
                "affected_symbols": [
                    item.get("symbol")
                    for item in concentration.get("concentrated_positions", [])
                    if item.get("symbol")
                ],
            })

        if largest_loss:
            priorities.append({
                "priority": 2,
                "category": "performance",
                "severity": "medium",
                "title": f"{largest_loss.get('symbol')} needs attention",
                "message": (
                    f"{largest_loss.get('symbol')} is the largest "
                    f"unrealized loss contributor at "
                    f"${largest_loss.get('profit', 0):,.2f}."
                ),
                "evidence": [
                    f"Return: {largest_loss.get('profit_percent', 0):.2f}%",
                    f"Profit/loss: ${largest_loss.get('profit', 0):,.2f}",
                ],
                "suggested_action": (
                    "Revisit the investment thesis and confirm whether "
                    "the original reasons for owning it remain valid."
                ),
                "affected_symbols": [largest_loss.get("symbol")],
            })

        if health_score < 70:
            components = health.get("components", {})
            priorities.append({
                "priority": 3,
                "category": "health",
                "severity": "medium",
                "title": "Portfolio health needs improvement",
                "message": f"Your portfolio health score is {health_score:.2f}/100.",
                "evidence": [
                    f"Diversification: {components.get('diversification_score', 0):.2f}/25",
                    f"Concentration: {components.get('concentration_score', 0):.2f}/25",
                ],
                "suggested_action": (
                    "Focus first on diversification and concentration, "
                    "then review losing positions."
                ),
                "affected_symbols": [],
            })

        priorities.sort(
            key=lambda item: (
                {"high": 0, "medium": 1, "low": 2}.get(item["severity"], 3),
                item["priority"],
            )
        )
        for index, item in enumerate(priorities, start=1):
            item["priority"] = index

        strengths = []
        if total_profit > 0:
            strengths.append(
                f"The portfolio is profitable by ${total_profit:,.2f}, "
                f"with a total return of {total_return:.2f}%."
            )
        if profitable_count > 0:
            strengths.append(
                f"{profitable_count} of {holdings_count} holdings are profitable."
            )
        if top_performer:
            strengths.append(
                f"{top_performer.get('symbol')} is the strongest performer "
                f"at {top_performer.get('profit_percent', 0):.2f}%."
            )
        if largest_profit:
            strengths.append(
                f"{largest_profit.get('symbol')} contributes the largest "
                f"dollar profit at ${largest_profit.get('profit', 0):,.2f}."
            )
        if health_score >= 70:
            strengths.append(
                f"Portfolio health is rated {str(health_rating).title()} "
                f"at {health_score:.2f}/100."
            )

        risks = []
        if risk_level in {"high", "medium"}:
            risks.append(
                f"Concentration risk is {risk_level}; the top three holdings "
                f"represent {concentration.get('top_three_percent', 0):.2f}% "
                "of portfolio value."
            )
        if largest_holding and largest_holding.get("allocation_percent", 0) >= 20:
            risks.append(
                f"{largest_holding.get('symbol')} represents "
                f"{largest_holding.get('allocation_percent', 0):.2f}% "
                "of portfolio value."
            )
        if losing_count > 0:
            risks.append(f"{losing_count} holdings are below their average cost.")
        if largest_loss:
            risks.append(
                f"{largest_loss.get('symbol')} is the largest loss contributor "
                f"at {largest_loss.get('profit_percent', 0):.2f}%."
            )

        opportunities = []
        if health_score < 85:
            opportunities.append(
                "Improving diversification and reducing concentration could "
                "raise the portfolio health score."
            )
        if losing_count > 0:
            opportunities.append(
                "Reviewing the thesis for losing holdings may improve quality."
            )
        if top_performer:
            opportunities.append(
                f"Study the drivers behind {top_performer.get('symbol')}'s "
                "strong performance before changing allocation."
            )

        holdings_to_watch = []
        priced = [
            item for item in holdings
            if item.get("price_status") == "available"
        ]
        priced.sort(
            key=lambda item: (
                abs(item.get("profit_percent", 0)),
                item.get("allocation_percent", 0),
            ),
            reverse=True,
        )

        for item in priced[:5]:
            reasons = []
            if item.get("allocation_percent", 0) >= 20:
                reasons.append("Large portfolio allocation")
            if item.get("profit_percent", 0) <= -10:
                reasons.append("Meaningful unrealized loss")
            if item.get("profit_percent", 0) >= 50:
                reasons.append("Large unrealized gain")
            if not reasons:
                reasons.append("Material portfolio position")

            holdings_to_watch.append({
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "allocation_percent": item.get("allocation_percent", 0),
                "profit": item.get("profit", 0),
                "profit_percent": item.get("profit_percent", 0),
                "reason": ", ".join(reasons),
            })

        executive = [
            f"Your portfolio contains {holdings_count} holdings and is "
            f"valued at ${total_value:,.2f}.",
            f"It has an unrealized profit of ${total_profit:,.2f}, "
            f"representing a return of {total_return:.2f}%.",
            f"Portfolio health is rated {str(health_rating).title()} "
            f"at {health_score:.2f}/100.",
        ]
        if largest_holding:
            executive.append(
                f"{largest_holding.get('symbol')} is the largest holding "
                f"at {largest_holding.get('allocation_percent', 0):.2f}%."
            )
        if weakest_performer:
            executive.append(
                f"{weakest_performer.get('symbol')} is the weakest performer "
                f"at {weakest_performer.get('profit_percent', 0):.2f}%."
            )

        status = (
            "excellent" if health_score >= 85
            else "good" if health_score >= 70
            else "fair" if health_score >= 50
            else "weak"
        )

        return {
            "portfolio_status": status,
            "executive_summary": " ".join(executive),
            "priority_insights": priorities[:5],
            "strengths": strengths,
            "risks": risks,
            "opportunities": opportunities,
            "holdings_to_watch": holdings_to_watch,
            "recent_changes": changes.get("summary", []),
            "recommended_questions": [
                "What should I focus on today?",
                "Which holdings need the most attention?",
                "What is my biggest portfolio risk?",
                "Where is my portfolio strongest?",
                "What changed since my previous snapshot?",
                "How can I improve my portfolio health score?",
            ],
            "disclaimer": PortfolioIntelligenceService.DISCLAIMER,
        }
