from sqlalchemy.orm import Session
from app.services.stock_service import StockService
from app.services.news_service import NewsService
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
            
        if intent == "stock":
            words = question.upper().split()
            symbol = None

            for word in words:
                clean_word = word.replace("?", "").replace(".", "").replace(",", "")
                if clean_word.isalpha() and 1 <= len(clean_word) <= 5:
                    symbol = clean_word
                    break

            if not symbol:
                return {
                    "question": question,
                    "intent": intent,
                    "answer": "Please include a valid stock symbol like AAPL, NVDA, or MSFT.",
                    "status": "needs_more_info",
                }

            stock = StockService.search_stock(symbol)

            return {
                "question": question,
                "intent": intent,
                "answer": (
                    f"{stock.get('company_name', symbol)} is trading around "
                    f"{stock.get('currency', 'USD')} {stock.get('current_price')}. "
                    f"MarketMind score: "
                    f"{stock.get('marketmind_score', {}).get('score', 'N/A')}/100."
                ),
                "data": stock,
                "status": "success",
            }
            
        if intent == "news":
            words = question.upper().split()
            symbol = None

            for word in words:
                clean_word = word.replace("?", "").replace(".", "").replace(",", "")
                if clean_word.isalpha() and 1 <= len(clean_word) <= 5:
                    symbol = clean_word
                    break

            if not symbol:
                return {
                    "question": question,
                    "intent": intent,
                    "answer": "Please include a valid stock symbol like AAPL, NVDA, or MSFT.",
                    "status": "needs_more_info",
                }

            news = NewsService.search_news(symbol)

            positive_count = len([
                item for item in news.get("news", [])
                if item.get("sentiment") == "positive"
            ])

            negative_count = len([
                item for item in news.get("news", [])
                if item.get("sentiment") == "negative"
            ])

            return {
                "question": question,
                "intent": intent,
                "answer": (
                    f"I found {news.get('count', 0)} relevant articles for {symbol}. "
                    f"Positive: {positive_count}, Negative: {negative_count}."
                ),
                "data": news,
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