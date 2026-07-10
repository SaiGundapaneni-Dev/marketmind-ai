import re

from sqlalchemy.orm import Session

from app.services.ipo_service import IPOService
from app.services.news_service import NewsService
from app.services.portfolio_service import PortfolioService
from app.services.sec_service import SECService
from app.services.stock_service import StockService


class CopilotService:

    COMPANY_SYMBOLS = {
        "apple": "AAPL",
        "apple inc": "AAPL",
        "microsoft": "MSFT",
        "microsoft corporation": "MSFT",
        "nvidia": "NVDA",
        "tesla": "TSLA",
        "amazon": "AMZN",
        "amazon.com": "AMZN",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "meta": "META",
        "meta platforms": "META",
        "facebook": "META",
        "netflix": "NFLX",
        "amd": "AMD",
        "advanced micro devices": "AMD",
        "intel": "INTC",
        "palantir": "PLTR",
        "sofi": "SOFI",
        "coinbase": "COIN",
        "salesforce": "CRM",
        "oracle": "ORCL",
        "ibm": "IBM",
        "walmart": "WMT",
        "disney": "DIS",
        "berkshire hathaway": "BRK.B",
    }

    SYMBOL_STOP_WORDS = {
        "A",
        "AI",
        "AM",
        "AN",
        "AND",
        "ARE",
        "ABOUT",
        "ANALYSIS",
        "ANALYZE",
        "ARTICLE",
        "ARTICLES",
        "COMPANY",
        "CURRENT",
        "DEVELOPMENT",
        "DEVELOPMENTS",
        "DO",
        "DOING",
        "FOR",
        "FROM",
        "FUNDAMENTAL",
        "FUNDAMENTALS",
        "GET",
        "GIVE",
        "HEADLINE",
        "HEADLINES",
        "HOW",
        "I",
        "IN",
        "IS",
        "IT",
        "LATEST",
        "ME",
        "MY",
        "NEWS",
        "OF",
        "ON",
        "PLEASE",
        "PRICE",
        "RESEARCH",
        "SENTIMENT",
        "SHARE",
        "SHOW",
        "STOCK",
        "TELL",
        "THAT",
        "THE",
        "THESE",
        "THIS",
        "THOSE",
        "TO",
        "TODAY",
        "UPDATE",
        "VALUATION",
        "WHAT",
        "WITH",
    }

    @staticmethod
    def detect_intent(question: str) -> str:
        text = question.lower().strip()

        ipo_terms = {
            "ipo",
            "initial public offering",
            "s-1",
            "s1",
            "f-1",
            "filing",
            "prospectus",
            "sec filing",
        }

        news_terms = {
            "news",
            "headline",
            "headlines",
            "sentiment",
            "article",
            "articles",
            "latest development",
            "latest developments",
        }

        portfolio_terms = {
            "portfolio",
            "holding",
            "holdings",
            "position",
            "positions",
            "total value",
            "total profit",
            "total loss",
            "allocation",
            "performance",
        }

        stock_terms = {
            "stock",
            "share price",
            "price",
            "company",
            "valuation",
            "pe ratio",
            "p/e",
            "market cap",
            "fundamental",
            "fundamentals",
        }

        if any(term in text for term in ipo_terms):
            return "ipo"

        if any(term in text for term in news_terms):
            return "news"

        if any(term in text for term in portfolio_terms):
            return "portfolio"

        if any(term in text for term in stock_terms):
            return "stock"

        return "general"

    @staticmethod
    def extract_symbol(question: str) -> str | None:
        normalized_question = question.lower().strip()

        # First resolve company names to verified ticker symbols.
        # Longer company names are checked first.
        sorted_companies = sorted(
            CopilotService.COMPANY_SYMBOLS,
            key=len,
            reverse=True,
        )

        for company_name in sorted_companies:
            pattern = rf"(?<!\w){re.escape(company_name)}(?!\w)"

            if re.search(pattern, normalized_question):
                return CopilotService.COMPANY_SYMBOLS[company_name]

        words = re.findall(r"\b[A-Za-z]{1,5}\b", question)

        # Prefer explicitly uppercase ticker symbols such as NVDA or AAPL.
        for word in words:
            candidate = word.upper()

            if (
                word.isupper()
                and candidate not in CopilotService.SYMBOL_STOP_WORDS
                and 1 <= len(candidate) <= 5
            ):
                return candidate

        # Support lowercase tickers only when they appear after clear
        # stock-related context words.
        ticker_patterns = [
            r"\b(?:stock|ticker|symbol|shares?)\s+(?:for|of|on)?\s*([a-z]{1,5})\b",
            r"\b(?:news|headlines?|sentiment|articles?)\s+(?:for|of|on|about)?\s*([a-z]{1,5})\b",
            r"\b(?:analyze|research|check|show)\s+([a-z]{1,5})\b",
            r"\b(?:about|on|for)\s+([a-z]{1,5})\b",
        ]

        for pattern in ticker_patterns:
            match = re.search(
                pattern,
                normalized_question,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            candidate = match.group(1).upper()

            if candidate not in CopilotService.SYMBOL_STOP_WORDS:
                return candidate

        return None

    @staticmethod
    def extract_ipo_company(question: str) -> str | None:
        patterns = [
            r"\bipo\s+(?:for|of|on|about)?\s*(.+)",
            r"\banalyze\s+(?:the\s+)?ipo\s+(?:for|of)?\s*(.+)",
            r"\bresearch\s+(?:the\s+)?ipo\s+(?:for|of)?\s*(.+)",
            r"\bsec\s+filings?\s+(?:for|of)?\s*(.+)",
            r"\bfilings?\s+(?:for|of)?\s*(.+)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match:
                company_name = match.group(1)

                company_name = re.sub(
                    r"[?.!,]+$",
                    "",
                    company_name,
                ).strip()

                if company_name:
                    return company_name

        return None

    @staticmethod
    def answer(question: str, db: Session):
        clean_question = question.strip()

        if not clean_question:
            return {
                "question": question,
                "intent": "general",
                "answer": "Please enter a question.",
                "status": "needs_more_info",
            }

        intent = CopilotService.detect_intent(clean_question)

        if intent == "portfolio":
            portfolio = PortfolioService.calculate(db)

            summary = portfolio["summary"]
            holdings = portfolio["holdings"]

            return {
                "question": clean_question,
                "intent": intent,
                "answer": (
                    f"Your portfolio contains {len(holdings)} holdings. "
                    f"Its current value is "
                    f"${summary['total_value']:,.2f}, with total profit of "
                    f"${summary['total_profit']:,.2f} and a return of "
                    f"{summary['total_return_percent']:.2f}%."
                ),
                "data": portfolio,
                "status": "success",
            }

        if intent == "stock":
            symbol = CopilotService.extract_symbol(clean_question)

            if not symbol:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include a US stock ticker or company name, "
                        "such as AAPL, Nvidia, Microsoft, or Tesla."
                    ),
                    "status": "needs_more_info",
                }

            stock = StockService.search_stock(symbol)

            if stock.get("error"):
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        f"I could not retrieve verified stock information "
                        f"for {symbol}. Please check the ticker and try again."
                    ),
                    "data": stock,
                    "status": "not_found",
                }

            score = stock.get("marketmind_score") or {}

            return {
                "question": clean_question,
                "intent": intent,
                "answer": (
                    f"{stock.get('company_name') or symbol} is trading around "
                    f"{stock.get('currency') or 'USD'} "
                    f"{stock.get('current_price', 'N/A')}. "
                    f"Its MarketMind score is "
                    f"{score.get('score', 'N/A')}/100, rated "
                    f"{score.get('rating', 'N/A')}."
                ),
                "data": stock,
                "status": "success",
            }

        if intent == "news":
            symbol = CopilotService.extract_symbol(clean_question)

            if not symbol:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include a US stock ticker or company name, "
                        "such as AAPL, Nvidia, Microsoft, or Tesla."
                    ),
                    "status": "needs_more_info",
                }

            news = NewsService.search_news(symbol)
            articles = news.get("news", [])

            positive_count = sum(
                item.get("sentiment") == "positive"
                for item in articles
            )

            neutral_count = sum(
                item.get("sentiment") == "neutral"
                for item in articles
            )

            negative_count = sum(
                item.get("sentiment") == "negative"
                for item in articles
            )

            if news.get("error"):
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        f"I could not retrieve news for {symbol}."
                    ),
                    "data": news,
                    "status": "error",
                }

            if not articles:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        f"No highly relevant recent articles were found "
                        f"for {symbol}. Please verify the ticker."
                    ),
                    "data": news,
                    "status": "not_found",
                }

            return {
                "question": clean_question,
                "intent": intent,
                "answer": (
                    f"I found {len(articles)} relevant articles for "
                    f"{symbol}. Positive: {positive_count}, "
                    f"neutral: {neutral_count}, "
                    f"negative: {negative_count}."
                ),
                "data": news,
                "status": "success",
            }

        if intent == "ipo":
            company_name = CopilotService.extract_ipo_company(
                clean_question
            )

            if not company_name:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include the company name. For example: "
                        "'Analyze IPO for Stripe'."
                    ),
                    "status": "needs_more_info",
                }

            ipo = IPOService.search_ipo(company_name)
            sec = SECService.search_company(company_name)

            analysis = ipo.get("analysis") or {}

            return {
                "question": clean_question,
                "intent": intent,
                "answer": (
                    f"IPO research status for "
                    f"{ipo.get('company_name', company_name)}: "
                    f"{analysis.get('recommendation', 'Not enough data')}. "
                    f"SEC company matches found: {sec.get('count', 0)}."
                ),
                "data": {
                    "ipo": ipo,
                    "sec": sec,
                },
                "status": "success",
            }

        return {
            "question": clean_question,
            "intent": "general",
            "answer": (
                "I can help with portfolio performance, US stock research, "
                "company news, and IPO research. Include a ticker or company "
                "name in your question."
            ),
            "status": "needs_more_info",
        }