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
            "diversified",
            "diversification",
            "concentration",
            "health score",
            "portfolio health",
            "biggest risk",
            "strongest holding",
            "weakest holding",
            "strength",
            "strengths",
            "what is good",
            "what's good",
            "doing well",
            "performing well",
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
    def detect_portfolio_question_type(
        question: str,
    ) -> str:
        text = question.lower().strip()

        strength_terms = {
            "strength",
            "strengths",
            "what is good",
            "what's good",
            "doing well",
            "performing well",
            "positive",
            "positives",
            "best part",
            "strongest",
        }

        if any(term in text for term in strength_terms):
            return "strengths"

        return "summary"

    @staticmethod
    def extract_symbol(question: str) -> str | None:
        normalized_question = question.lower().strip()

        sorted_companies = sorted(
            CopilotService.COMPANY_SYMBOLS,
            key=len,
            reverse=True,
        )

        for company_name in sorted_companies:
            pattern = rf"(?<!\w){re.escape(company_name)}(?!\w)"

            if re.search(pattern, normalized_question):
                return CopilotService.COMPANY_SYMBOLS[
                    company_name
                ]

        words = re.findall(
            r"\b[A-Za-z]{1,5}\b",
            question,
        )

        for word in words:
            candidate = word.upper()

            if (
                word.isupper()
                and candidate
                not in CopilotService.SYMBOL_STOP_WORDS
                and 1 <= len(candidate) <= 5
            ):
                return candidate

        ticker_patterns = [
            (
                r"\b(?:stock|ticker|symbol|shares?)"
                r"\s+(?:for|of|on)?\s*"
                r"([a-z]{1,5})\b"
            ),
            (
                r"\b(?:news|headlines?|sentiment|articles?)"
                r"\s+(?:for|of|on|about)?\s*"
                r"([a-z]{1,5})\b"
            ),
            (
                r"\b(?:analyze|research|check|show)"
                r"\s+([a-z]{1,5})\b"
            ),
            (
                r"\b(?:about|on|for)"
                r"\s+([a-z]{1,5})\b"
            ),
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

            if (
                candidate
                not in CopilotService.SYMBOL_STOP_WORDS
            ):
                return candidate

        return None

    @staticmethod
    def extract_ipo_company(
        question: str,
    ) -> str | None:
        patterns = [
            r"\bipo\s+(?:for|of|on|about)?\s*(.+)",
            (
                r"\banalyze\s+(?:the\s+)?ipo"
                r"\s+(?:for|of)?\s*(.+)"
            ),
            (
                r"\bresearch\s+(?:the\s+)?ipo"
                r"\s+(?:for|of)?\s*(.+)"
            ),
            (
                r"\bsec\s+filings?"
                r"\s+(?:for|of)?\s*(.+)"
            ),
            (
                r"\bfilings?"
                r"\s+(?:for|of)?\s*(.+)"
            ),
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
    def build_portfolio_summary(
        portfolio: dict,
    ) -> str:
        summary = portfolio.get("summary", {})
        allocation = portfolio.get("allocation", {})
        concentration = portfolio.get(
            "concentration_risk",
            {},
        )
        performance = portfolio.get(
            "performance_insights",
            {},
        )
        health = portfolio.get("health_score", {})

        holdings_count = summary.get(
            "holdings_count",
            len(portfolio.get("holdings", [])),
        )

        total_value = summary.get("total_value", 0)
        total_profit = summary.get("total_profit", 0)
        total_return = summary.get(
            "total_return_percent",
            0,
        )

        largest_holding = allocation.get(
            "largest_holding"
        )

        risk_level = concentration.get(
            "risk_level",
            "unknown",
        )

        profitable_count = performance.get(
            "profitable_holdings_count",
            0,
        )

        losing_count = performance.get(
            "losing_holdings_count",
            0,
        )

        top_performer = performance.get(
            "top_performer"
        )

        weakest_performer = performance.get(
            "weakest_performer"
        )

        health_score = health.get("score", 0)
        health_rating = health.get(
            "rating",
            "unknown",
        )

        parts = [
            (
                f"Your portfolio contains {holdings_count} holdings "
                f"and is currently valued at ${total_value:,.2f}."
            ),
            (
                f"It has an unrealized profit of "
                f"${total_profit:,.2f}, representing an overall "
                f"return of {total_return:.2f}%."
            ),
        ]

        if largest_holding:
            parts.append(
                (
                    f"{largest_holding.get('symbol')} is your "
                    f"largest holding at "
                    f"{largest_holding.get('allocation_percent', 0):.2f}% "
                    f"of portfolio value."
                )
            )

        if risk_level != "unknown":
            parts.append(
                (
                    f"Your concentration risk is currently "
                    f"{risk_level}."
                )
            )

        parts.append(
            (
                f"{profitable_count} holdings are profitable, "
                f"while {losing_count} are currently at a loss."
            )
        )

        if top_performer:
            parts.append(
                (
                    f"{top_performer.get('symbol')} is your "
                    f"strongest performer with a return of "
                    f"{top_performer.get('profit_percent', 0):.2f}%."
                )
            )

        if weakest_performer:
            parts.append(
                (
                    f"{weakest_performer.get('symbol')} is your "
                    f"weakest performer at "
                    f"{weakest_performer.get('profit_percent', 0):.2f}%."
                )
            )

        parts.append(
            (
                f"Your portfolio health score is "
                f"{health_score:.2f}/100, rated "
                f"{str(health_rating).title()}."
            )
        )

        return " ".join(parts)

    @staticmethod
    def build_portfolio_strengths(
        portfolio: dict,
    ) -> str:
        summary = portfolio.get("summary", {})
        performance = portfolio.get(
            "performance_insights",
            {},
        )
        health = portfolio.get("health_score", {})
        concentration = portfolio.get(
            "concentration_risk",
            {},
        )

        total_return = summary.get(
            "total_return_percent",
            0,
        )

        total_profit = summary.get(
            "total_profit",
            0,
        )

        profitable_count = performance.get(
            "profitable_holdings_count",
            0,
        )

        holdings_count = summary.get(
            "holdings_count",
            0,
        )

        top_performer = performance.get(
            "top_performer"
        )

        largest_profit = performance.get(
            "largest_profit_contributor"
        )

        health_score = health.get("score", 0)

        health_rating = health.get(
            "rating",
            "unknown",
        )

        risk_level = concentration.get(
            "risk_level",
            "unknown",
        )

        strengths = []

        if total_profit > 0:
            strengths.append(
                (
                    f"Your portfolio is profitable by "
                    f"${total_profit:,.2f}, with an overall "
                    f"return of {total_return:.2f}%."
                )
            )

        if profitable_count > 0:
            strengths.append(
                (
                    f"{profitable_count} of your "
                    f"{holdings_count} holdings are currently "
                    f"profitable."
                )
            )

        if top_performer:
            strengths.append(
                (
                    f"{top_performer.get('symbol')} is your "
                    f"strongest performer, returning "
                    f"{top_performer.get('profit_percent', 0):.2f}%."
                )
            )

        if largest_profit:
            strengths.append(
                (
                    f"{largest_profit.get('symbol')} is your "
                    f"largest dollar-profit contributor at "
                    f"${largest_profit.get('profit', 0):,.2f}."
                )
            )

        if health_score >= 70:
            strengths.append(
                (
                    f"Your portfolio health score is "
                    f"{health_score:.2f}/100, rated "
                    f"{str(health_rating).title()}."
                )
            )

        if risk_level == "low":
            strengths.append(
                (
                    "Your portfolio currently has low "
                    "concentration risk."
                )
            )

        elif risk_level == "medium":
            strengths.append(
                (
                    "Your position sizes remain manageable, "
                    "although the largest holdings should still "
                    "be monitored."
                )
            )

        if not strengths:
            return (
                "I could not identify clear portfolio strengths "
                "from the currently available pricing and "
                "holding data."
            )

        return (
            "The main strengths of your portfolio are: "
            + " ".join(strengths)
        )

    @staticmethod
    def answer(
        question: str,
        db: Session,
    ):
        clean_question = question.strip()

        if not clean_question:
            return {
                "question": question,
                "intent": "general",
                "answer": "Please enter a question.",
                "status": "needs_more_info",
            }

        intent = CopilotService.detect_intent(
            clean_question
        )

        if intent == "portfolio":
            portfolio = PortfolioService.calculate(db)

            portfolio_question_type = (
                CopilotService.detect_portfolio_question_type(
                    clean_question
                )
            )

            if portfolio_question_type == "strengths":
                answer_text = (
                    CopilotService.build_portfolio_strengths(
                        portfolio
                    )
                )
            else:
                answer_text = (
                    CopilotService.build_portfolio_summary(
                        portfolio
                    )
                )

            return {
                "question": clean_question,
                "intent": intent,
                "portfolio_question_type": (
                    portfolio_question_type
                ),
                "answer": answer_text,
                "data": portfolio,
                "status": "success",
            }

        if intent == "stock":
            symbol = CopilotService.extract_symbol(
                clean_question
            )

            if not symbol:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include a US stock ticker or "
                        "company name, such as AAPL, Nvidia, "
                        "Microsoft, or Tesla."
                    ),
                    "status": "needs_more_info",
                }

            stock = StockService.search_stock(symbol)

            if stock.get("error"):
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        f"I could not retrieve verified stock "
                        f"information for {symbol}. Please check "
                        f"the ticker and try again."
                    ),
                    "data": stock,
                    "status": "not_found",
                }

            score = stock.get(
                "marketmind_score"
            ) or {}

            return {
                "question": clean_question,
                "intent": intent,
                "answer": (
                    f"{stock.get('company_name') or symbol} "
                    f"is trading around "
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
            symbol = CopilotService.extract_symbol(
                clean_question
            )

            if not symbol:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include a US stock ticker or "
                        "company name, such as AAPL, Nvidia, "
                        "Microsoft, or Tesla."
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
                        f"I could not retrieve news for "
                        f"{symbol}."
                    ),
                    "data": news,
                    "status": "error",
                }

            if not articles:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        f"No highly relevant recent articles "
                        f"were found for {symbol}. Please verify "
                        f"the ticker."
                    ),
                    "data": news,
                    "status": "not_found",
                }

            return {
                "question": clean_question,
                "intent": intent,
                "answer": (
                    f"I found {len(articles)} relevant articles "
                    f"for {symbol}. Positive: {positive_count}, "
                    f"neutral: {neutral_count}, "
                    f"negative: {negative_count}."
                ),
                "data": news,
                "status": "success",
            }

        if intent == "ipo":
            company_name = (
                CopilotService.extract_ipo_company(
                    clean_question
                )
            )

            if not company_name:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include the company name. "
                        "For example: "
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
                    f"SEC company matches found: "
                    f"{sec.get('count', 0)}."
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
                "I can help with portfolio performance, "
                "US stock research, company news, and IPO "
                "research. Include a ticker or company name "
                "in your question."
            ),
            "status": "needs_more_info",
        }