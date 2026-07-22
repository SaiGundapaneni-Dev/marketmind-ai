import re

from sqlalchemy.orm import Session

from app.repositories.thesis_ai_repository import (
    ThesisAIRepository,
)

from app.services.ipo_service import IPOService
from app.services.news_service import NewsService
from app.services.portfolio_intelligence_service import (
    PortfolioIntelligenceService,
)
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
        thesis_terms = {
            "thesis",
            "investment thesis",
            "why did i buy",
            "why i bought",
            "reason i bought",
            "reasons i bought",
            "buy reason",
            "buy reasons",
            "target price",
            "price target",
            "conviction",
            "confidence",
            "investment horizon",
            "sell condition",
            "sell conditions",
            "when should i sell",
            "what would make me sell",
            "review date",
        }
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
            "focus on today",
            "focus today",
            "attention today",
            "needs attention",
            "need attention",
            "deserves attention",
            "holding to watch",
            "holdings to watch",
            "what changed",
            "changed since yesterday",
            "changed since",
            "recent changes",
            "portfolio update",
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
        
        if any(term in text for term in thesis_terms):
            return "thesis"

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

        risk_terms = {
            "risk",
            "risks",
            "risky",
            "biggest risk",
            "main risk",
            "concern",
            "concerns",
            "concerned",
            "what is wrong",
            "what's wrong",
            "weakness",
            "weaknesses",
            "problem",
            "problems",
            "danger",
            "downside",
        }

        recommendation_terms = {
            "improve",
            "improvement",
            "recommend",
            "recommendation",
            "recommendations",
            "suggest",
            "suggestion",
            "suggestions",
            "what should i do",
            "what should i focus on",
            "focus on next",
            "next step",
            "how can i improve",
            "how to improve",
            "what can i change",
            "what should i change",
        }

        diversification_terms = {
            "diversified",
            "diversification",
            "well diversified",
            "enough diversification",
            "too concentrated",
            "concentrated",
            "concentration",
            "spread out",
            "balanced portfolio",
        }

        health_terms = {
            "healthy",
            "health",
            "health score",
            "portfolio health",
            "why is my health score",
            "explain my health score",
            "score breakdown",
            "overall score",
        }

        focus_terms = {
            "focus on today",
            "focus today",
            "attention today",
            "what should i focus on",
            "priority",
            "priorities",
            "most important",
        }

        watch_terms = {
            "needs attention",
            "need attention",
            "deserves attention",
            "holding to watch",
            "holdings to watch",
            "watch closely",
            "which holding",
        }

        changes_terms = {
            "what changed",
            "changed since yesterday",
            "changed since",
            "recent changes",
            "portfolio update",
            "since my previous snapshot",
        }

        if any(term in text for term in changes_terms):
            return "changes"

        if any(term in text for term in watch_terms):
            return "holdings_to_watch"

        if any(term in text for term in focus_terms):
            return "focus"

        if any(term in text for term in strength_terms):
            return "strengths"

        if any(term in text for term in recommendation_terms):
            return "recommendations"

        if any(term in text for term in health_terms):
            return "health"

        if any(term in text for term in diversification_terms):
            return "diversification"

        if any(term in text for term in risk_terms):
            return "risks"

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
    def build_portfolio_risks(
        portfolio: dict,
    ) -> str:
        summary = portfolio.get("summary", {})

        allocation = portfolio.get(
            "allocation",
            {},
        )

        concentration = portfolio.get(
            "concentration_risk",
            {},
        )

        performance = portfolio.get(
            "performance_insights",
            {},
        )

        health = portfolio.get(
            "health_score",
            {},
        )

        holdings_count = summary.get(
            "holdings_count",
            0,
        )

        unpriced_count = summary.get(
            "unpriced_holdings_count",
            0,
        )

        largest_holding = allocation.get(
            "largest_holding"
        )

        risk_level = concentration.get(
            "risk_level",
            "unknown",
        )

        top_three_percent = concentration.get(
            "top_three_percent",
            0,
        )

        losing_count = performance.get(
            "losing_holdings_count",
            0,
        )

        weakest_performer = performance.get(
            "weakest_performer"
        )

        largest_loss = performance.get(
            "largest_loss_contributor"
        )

        health_score = health.get(
            "score",
            0,
        )

        components = health.get(
            "components",
            {},
        )

        diversification_score = components.get(
            "diversification_score",
            0,
        )

        risks = []

        if risk_level in {"medium", "high"}:
            risks.append(
                (
                    f"Your portfolio has {risk_level} concentration "
                    f"risk, with the top three holdings representing "
                    f"{top_three_percent:.2f}% of total portfolio value."
                )
            )

        if largest_holding:
            allocation_percent = largest_holding.get(
                "allocation_percent",
                0,
            )

            if allocation_percent >= 20:
                risks.append(
                    (
                        f"{largest_holding.get('symbol')} is your "
                        f"largest holding at {allocation_percent:.2f}%, "
                        "so a large price movement in this stock could "
                        "significantly affect the portfolio."
                    )
                )

        if losing_count > 0:
            risks.append(
                (
                    f"{losing_count} of your {holdings_count} holdings "
                    "are currently trading below their average cost."
                )
            )

        if largest_loss:
            loss_amount = abs(
                largest_loss.get("profit", 0)
            )

            risks.append(
                (
                    f"{largest_loss.get('symbol')} is currently your "
                    f"largest unrealized loss contributor at "
                    f"-${loss_amount:,.2f}, or "
                    f"{largest_loss.get('profit_percent', 0):.2f}%."
                )
            )

        if (
            weakest_performer
            and largest_loss
            and weakest_performer.get("symbol")
            != largest_loss.get("symbol")
        ):
            risks.append(
                (
                    f"{weakest_performer.get('symbol')} has the weakest "
                    f"percentage return at "
                    f"{weakest_performer.get('profit_percent', 0):.2f}%."
                )
            )

        if diversification_score < 20:
            risks.append(
                (
                    f"Your diversification component is only "
                    f"{diversification_score:.2f}/25, indicating that "
                    "the portfolio may benefit from broader exposure."
                )
            )

        if health_score < 70:
            risks.append(
                (
                    f"Your portfolio health score is "
                    f"{health_score:.2f}/100, which indicates several "
                    "areas may need attention."
                )
            )

        if unpriced_count > 0:
            risks.append(
                (
                    f"{unpriced_count} holdings do not currently have "
                    "live pricing, so portfolio calculations may be "
                    "incomplete."
                )
            )

        if not risks:
            return (
                "No major portfolio risks were detected from the "
                "currently available holdings and pricing data."
            )

        return (
            "The main risks in your portfolio are: "
            + " ".join(risks)
            + " These observations are informational and are not "
            "personalized financial advice."
        )

    @staticmethod
    def build_portfolio_recommendations(
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
        health = portfolio.get(
            "health_score",
            {},
        )

        holdings_count = summary.get(
            "holdings_count",
            0,
        )

        unpriced_count = summary.get(
            "unpriced_holdings_count",
            0,
        )

        largest_holding = allocation.get(
            "largest_holding"
        )

        risk_level = concentration.get(
            "risk_level",
            "unknown",
        )

        top_three_percent = concentration.get(
            "top_three_percent",
            0,
        )

        losing_count = performance.get(
            "losing_holdings_count",
            0,
        )

        largest_loss = performance.get(
            "largest_loss_contributor"
        )

        health_score = health.get(
            "score",
            0,
        )

        components = health.get(
            "components",
            {},
        )

        diversification_score = components.get(
            "diversification_score",
            0,
        )

        profitability_score = components.get(
            "profitability_score",
            0,
        )

        recommendations = []

        if risk_level in {"medium", "high"}:
            recommendations.append(
                (
                    f"Review your position sizing because the top three "
                    f"holdings represent {top_three_percent:.2f}% of "
                    "the portfolio."
                )
            )

        if largest_holding:
            largest_percent = largest_holding.get(
                "allocation_percent",
                0,
            )

            if largest_percent >= 20:
                recommendations.append(
                    (
                        f"Monitor {largest_holding.get('symbol')} closely "
                        f"because it represents {largest_percent:.2f}% "
                        "of total portfolio value."
                    )
                )

        if diversification_score < 20:
            recommendations.append(
                (
                    f"Consider broader diversification. Your "
                    f"diversification score is "
                    f"{diversification_score:.2f}/25 across "
                    f"{holdings_count} holdings."
                )
            )

        if losing_count > 0:
            recommendations.append(
                (
                    f"Review the investment thesis for your "
                    f"{losing_count} losing holdings instead of relying "
                    "only on short-term price movement."
                )
            )

        if largest_loss:
            loss_amount = abs(
                largest_loss.get("profit", 0)
            )

            recommendations.append(
                (
                    f"Pay particular attention to "
                    f"{largest_loss.get('symbol')}, currently the "
                    f"largest unrealized loss contributor at "
                    f"-${loss_amount:,.2f}."
                )
            )

        if profitability_score < 20:
            recommendations.append(
                (
                    f"Only part of the portfolio is currently profitable. "
                    f"Your profitability component is "
                    f"{profitability_score:.2f}/25, so review which "
                    "holdings are contributing positively and negatively."
                )
            )

        if health_score < 85:
            recommendations.append(
                (
                    f"Focus on improving diversification and reducing "
                    f"concentration to raise the portfolio health score "
                    f"from {health_score:.2f}/100."
                )
            )

        if unpriced_count > 0:
            recommendations.append(
                (
                    f"Resolve missing live-price coverage for "
                    f"{unpriced_count} holdings before making portfolio "
                    "decisions based on the current analytics."
                )
            )

        if not recommendations:
            return (
                "Your portfolio does not currently show any major areas "
                "requiring improvement based on the available data."
            )

        return (
            "Here are the main areas to improve: "
            + " ".join(recommendations)
            + " These suggestions are informational and are not "
            "personalized financial advice."
        )

    @staticmethod
    def build_portfolio_diversification(
        portfolio: dict,
    ) -> str:
        summary = portfolio.get(
            "summary",
            {},
        )

        allocation = portfolio.get(
            "allocation",
            {},
        )

        concentration = portfolio.get(
            "concentration_risk",
            {},
        )

        health = portfolio.get(
            "health_score",
            {},
        )

        holdings_count = summary.get(
            "holdings_count",
            0,
        )

        allocation_by_asset_type = allocation.get(
            "by_asset_type",
            [],
        )

        largest_holding = allocation.get(
            "largest_holding"
        )

        risk_level = concentration.get(
            "risk_level",
            "unknown",
        )

        top_three_percent = concentration.get(
            "top_three_percent",
            0,
        )

        components = health.get(
            "components",
            {},
        )

        diversification_score = components.get(
            "diversification_score",
            0,
        )

        asset_type_count = len(
            allocation_by_asset_type
        )

        category_label = (
            "category"
            if asset_type_count == 1
            else "categories"
        )

        parts = [
            (
                f"Your portfolio has {holdings_count} holdings "
                f"across {asset_type_count} asset-type "
                f"{category_label}."
            ),
            (
                f"Your diversification score is "
                f"{diversification_score:.2f}/25."
            ),
            (
                f"Your concentration risk is {risk_level}, "
                f"with the top three holdings representing "
                f"{top_three_percent:.2f}% of portfolio value."
            ),
        ]

        if largest_holding:
            parts.append(
                (
                    f"{largest_holding.get('symbol')} is your "
                    f"largest position at "
                    f"{largest_holding.get('allocation_percent', 0):.2f}%."
                )
            )

        if (
            diversification_score >= 20
            and risk_level == "low"
        ):
            conclusion = (
                "Overall, the portfolio appears reasonably "
                "diversified based on the current holdings and "
                "concentration thresholds."
            )

        elif diversification_score >= 15:
            conclusion = (
                "Overall, the portfolio has moderate "
                "diversification, but broader exposure could "
                "reduce concentration risk."
            )

        else:
            conclusion = (
                "Overall, the portfolio has limited "
                "diversification and may rely too heavily on "
                "a small number of positions."
            )

        return (
            " ".join(parts)
            + " "
            + conclusion
            + " This assessment is informational and is not "
            + "personalized financial advice."
        )

    @staticmethod
    def build_portfolio_health(
        portfolio: dict,
    ) -> str:
        health = portfolio.get(
            "health_score",
            {},
        )

        concentration = portfolio.get(
            "concentration_risk",
            {},
        )

        performance = portfolio.get(
            "performance_insights",
            {},
        )

        score = health.get(
            "score",
            0,
        )

        rating = health.get(
            "rating",
            "unknown",
        )

        components = health.get(
            "components",
            {},
        )

        diversification_score = components.get(
            "diversification_score",
            0,
        )

        concentration_score = components.get(
            "concentration_score",
            0,
        )

        profitability_score = components.get(
            "profitability_score",
            0,
        )

        pricing_coverage_score = components.get(
            "pricing_coverage_score",
            0,
        )

        profitable_count = performance.get(
            "profitable_holdings_count",
            0,
        )

        losing_count = performance.get(
            "losing_holdings_count",
            0,
        )

        risk_level = concentration.get(
            "risk_level",
            "unknown",
        )

        return (
            f"Your portfolio health score is {score:.2f}/100, "
            f"rated {str(rating).title()}. "
            f"The score includes {diversification_score:.2f}/25 "
            f"for diversification, {concentration_score:.2f}/25 "
            f"for concentration, {profitability_score:.2f}/25 "
            f"for profitability, and "
            f"{pricing_coverage_score:.2f}/25 for live-price coverage. "
            f"Your concentration risk is {risk_level}. "
            f"{profitable_count} holdings are profitable and "
            f"{losing_count} are currently at a loss. "
            f"The main opportunities to improve the score are broader "
            f"diversification and lower concentration in the largest "
            f"positions. This assessment is informational and is not "
            f"personalized financial advice."
        )

    @staticmethod
    def build_daily_focus(
        intelligence: dict,
    ) -> str:
        executive_summary = intelligence.get(
            "executive_summary",
            "",
        )

        priority_insights = intelligence.get(
            "priority_insights",
            [],
        )

        if not priority_insights:
            return (
                f"{executive_summary} "
                "No urgent portfolio priorities were identified today."
            ).strip()

        priority = priority_insights[0]

        return (
            f"{executive_summary} "
            f"Your highest-priority area today is "
            f"{priority.get('title', 'portfolio review')}. "
            f"{priority.get('message', '')} "
            f"Suggested action: "
            f"{priority.get('suggested_action', '')}"
        ).strip()

    @staticmethod
    def build_holdings_to_watch(
        intelligence: dict,
    ) -> str:
        holdings = intelligence.get(
            "holdings_to_watch",
            [],
        )

        if not holdings:
            return (
                "No individual holding currently stands out as "
                "requiring special attention."
            )

        messages = []

        for holding in holdings[:3]:
            messages.append(
                (
                    f"{holding.get('symbol')} represents "
                    f"{holding.get('allocation_percent', 0):.2f}% "
                    f"of the portfolio and has an unrealized return of "
                    f"{holding.get('profit_percent', 0):.2f}%. "
                    f"Reason to watch: {holding.get('reason')}."
                )
            )

        return (
            "The holdings that deserve the most attention are: "
            + " ".join(messages)
            + " These observations are informational and are not "
            + "personalized financial advice."
        )

    @staticmethod
    def build_recent_changes(
        intelligence: dict,
    ) -> str:
        changes = intelligence.get(
            "recent_changes",
            [],
        )

        if not changes:
            return (
                "I do not have enough snapshot history to identify "
                "recent portfolio changes yet. Create another daily "
                "snapshot after the portfolio changes."
            )

        return (
            "Here is what changed since your previous portfolio "
            "snapshot: "
            + " ".join(changes)
        )
        
    @staticmethod
    def build_thesis_answer(
        symbol: str,
        thesis,
    ) -> str:
        parts = [
            (
                f"Your investment thesis for {symbol} is: "
                f"{thesis.thesis}"
            )
        ]

        if thesis.buy_reasons:
            parts.append(
                f"Your recorded buy reasons are: "
                f"{thesis.buy_reasons}."
            )

        if thesis.target_price is not None:
            parts.append(
                f"Your target price is "
                f"${thesis.target_price:,.2f}."
            )

        if thesis.investment_horizon:
            parts.append(
                f"Your investment horizon is "
                f"{thesis.investment_horizon}."
            )

        if thesis.conviction_score is not None:
            parts.append(
                f"Your conviction score is "
                f"{thesis.conviction_score}/10."
            )

        if thesis.risk_level:
            parts.append(
                f"You classified the risk level as "
                f"{thesis.risk_level}."
            )

        if thesis.sell_conditions:
            parts.append(
                f"Your sell conditions are: "
                f"{thesis.sell_conditions}."
            )

        if thesis.review_date:
            parts.append(
                f"Your next review date is "
                f"{thesis.review_date.strftime('%B %d, %Y')}."
            )

        if thesis.notes:
            parts.append(
                f"Additional notes: {thesis.notes}"
            )

        return " ".join(parts)

    @staticmethod
    def answer(
        question: str,
        db: Session,
        user_id: int,
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
        
        if intent == "thesis":
            symbol = CopilotService.extract_symbol(
                clean_question
            )

            if not symbol:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        "Please include a stock ticker or company "
                        "name, such as AAPL, Apple, NVDA, or Nvidia."
                    ),
                    "status": "needs_more_info",
                }

            thesis = ThesisAIRepository.get_user_thesis(
                db=db,
                user_id=user_id,
                symbol=symbol,
            )

            if thesis is None:
                return {
                    "question": clean_question,
                    "intent": intent,
                    "answer": (
                        f"You have not created an investment thesis "
                        f"for {symbol} yet."
                    ),
                    "data": {
                        "symbol": symbol,
                        "thesis": None,
                    },
                    "status": "not_found",
                }

            return {
                "question": clean_question,
                "intent": intent,
                "answer": CopilotService.build_thesis_answer(
                    symbol=symbol,
                    thesis=thesis,
                ),
                "data": {
                    "symbol": symbol,
                    "thesis": {
                        "id": thesis.id,
                        "holding_id": thesis.holding_id,
                        "thesis": thesis.thesis,
                        "target_price": thesis.target_price,
                        "investment_horizon": (
                            thesis.investment_horizon
                        ),
                        "conviction_score": (
                            thesis.conviction_score
                        ),
                        "risk_level": thesis.risk_level,
                        "buy_reasons": thesis.buy_reasons,
                        "sell_conditions": (
                            thesis.sell_conditions
                        ),
                        "notes": thesis.notes,
                        "review_date": (
                            thesis.review_date.isoformat()
                            if thesis.review_date
                            else None
                        ),
                    },
                },
                "status": "success",
            }

        if intent == "portfolio":
            portfolio_question_type = (
                CopilotService.detect_portfolio_question_type(
                    clean_question
                )
            )

            intelligence_question_types = {
                "focus",
                "holdings_to_watch",
                "changes",
            }

            if (
                portfolio_question_type
                in intelligence_question_types
            ):
                intelligence = (
                    PortfolioIntelligenceService.generate(
                        db,
                        user_id,
                    )
                )

                if portfolio_question_type == "focus":
                    answer_text = (
                        CopilotService.build_daily_focus(
                            intelligence
                        )
                    )

                elif (
                    portfolio_question_type
                    == "holdings_to_watch"
                ):
                    answer_text = (
                        CopilotService.build_holdings_to_watch(
                            intelligence
                        )
                    )

                else:
                    answer_text = (
                        CopilotService.build_recent_changes(
                            intelligence
                        )
                    )

                return {
                    "question": clean_question,
                    "intent": intent,
                    "portfolio_question_type": (
                        portfolio_question_type
                    ),
                    "answer": answer_text,
                    "data": intelligence,
                    "status": "success",
                }

            portfolio = PortfolioService.calculate(
                db,
                user_id,
            )

            if portfolio_question_type == "strengths":
                answer_text = (
                    CopilotService.build_portfolio_strengths(
                        portfolio
                    )
                )

            elif portfolio_question_type == "risks":
                answer_text = (
                    CopilotService.build_portfolio_risks(
                        portfolio
                    )
                )

            elif portfolio_question_type == "recommendations":
                answer_text = (
                    CopilotService.build_portfolio_recommendations(
                        portfolio
                    )
                )

            elif portfolio_question_type == "diversification":
                answer_text = (
                    CopilotService.build_portfolio_diversification(
                        portfolio
                    )
                )

            elif portfolio_question_type == "health":
                answer_text = (
                    CopilotService.build_portfolio_health(
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