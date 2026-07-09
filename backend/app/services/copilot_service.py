from sqlalchemy.orm import Session

from app.services.portfolio_service import PortfolioService


class CopilotService:

    @staticmethod
    def detect_intent(question: str):
        text = question.lower()

        if any(word in text for word in ["portfolio", "holding", "holdings", "profit", "loss"]):
            return "portfolio"

        if any(word in text for word in ["stock", "company", "price", "valuation", "pe ratio"]):
            return "stock"

        if any(word in text for word in ["news", "headline", "sentiment"]):
            return "news"

        if any(word in text for word in ["ipo", "s-1", "filing", "sec"]):
            return "ipo"

        return "general"

    @staticmethod
    def answer(question: str, db: Session):
        intent = CopilotService.detect_intent(question)

        if intent == "portfolio":
            portfolio = PortfolioService.calculate(db)

            return {
                "question": question,
                "intent": intent,
                "answer": (
                    f"Your portfolio has {len(portfolio['holdings'])} holdings. "
                    f"Total value is ${portfolio['summary']['total_value']}. "
                    f"Total profit is ${portfolio['summary']['total_profit']}."
                ),
                "data": portfolio,
                "status": "success",
            }

        return {
            "question": question,
            "intent": intent,
            "answer": (
                f"I classified your question as a {intent} question. "
                "Next, I will connect this intent to MarketMind data sources."
            ),
            "status": "success",
        }