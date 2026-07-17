from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.news_service import NewsService
from app.services.portfolio_service import PortfolioService
from app.services.stock_service import StockService


class StockAnalysisService:
    """Build a deterministic, explainable stock-intelligence report."""

    @staticmethod
    def _number(value: Any) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)
        return None

    @staticmethod
    def _normalize_sentiment(value: Any) -> str:
        sentiment = str(value or "neutral").lower()
        if sentiment not in {"positive", "negative", "neutral"}:
            return "neutral"
        return sentiment

    @staticmethod
    def _extract_articles(news_payload: dict) -> list[dict]:
        articles = news_payload.get("news", [])
        return articles if isinstance(articles, list) else []

    @staticmethod
    def _build_news_summary(news_payload: dict) -> dict:
        articles = StockAnalysisService._extract_articles(news_payload)

        positive = 0
        negative = 0
        neutral = 0

        for article in articles:
            sentiment = StockAnalysisService._normalize_sentiment(
                article.get("sentiment")
            )
            if sentiment == "positive":
                positive += 1
            elif sentiment == "negative":
                negative += 1
            else:
                neutral += 1

        if positive > negative:
            overall = "positive"
        elif negative > positive:
            overall = "negative"
        else:
            overall = "neutral"

        return {
            "article_count": len(articles),
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "overall_sentiment": overall,
            "articles": articles[:5],
        }

    @staticmethod
    def _build_portfolio_exposure(
        symbol: str,
        portfolio: dict,
    ) -> dict:
        holdings = portfolio.get("holdings", [])

        holding = next(
            (
                item
                for item in holdings
                if str(item.get("symbol", "")).upper() == symbol
            ),
            None,
        )

        if not holding:
            return {
                "owned": False,
                "quantity": 0,
                "current_value": 0.0,
                "allocation_percent": 0.0,
                "profit": 0.0,
                "profit_percent": 0.0,
                "message": (
                    f"{symbol} is not currently held in your portfolio."
                ),
            }

        return {
            "owned": True,
            "quantity": holding.get("quantity", 0),
            "current_value": holding.get("current_value", 0.0),
            "allocation_percent": holding.get(
                "allocation_percent",
                0.0,
            ),
            "profit": holding.get("profit", 0.0),
            "profit_percent": holding.get(
                "profit_percent",
                0.0,
            ),
            "message": (
                f"You own {holding.get('quantity', 0)} shares of {symbol}. "
                f"It represents "
                f"{holding.get('allocation_percent', 0.0):.2f}% "
                f"of your portfolio."
            ),
        }

    @staticmethod
    def _build_bull_case(stock: dict, news_summary: dict) -> list[str]:
        points: list[str] = []

        revenue_growth = StockAnalysisService._number(
            stock.get("revenue_growth")
        )
        profit_margin = StockAnalysisService._number(
            stock.get("profit_margin")
        )
        forward_pe = StockAnalysisService._number(
            stock.get("forward_pe")
        )
        target = StockAnalysisService._number(
            stock.get("analyst_target_price")
        )
        price = StockAnalysisService._number(
            stock.get("current_price")
        )

        if revenue_growth is not None and revenue_growth > 0.10:
            points.append(
                f"Revenue growth is strong at {revenue_growth * 100:.1f}%."
            )

        if profit_margin is not None and profit_margin > 0.15:
            points.append(
                f"Profit margin is healthy at {profit_margin * 100:.1f}%."
            )

        if (
            target is not None
            and price is not None
            and price > 0
            and target > price
        ):
            upside = ((target - price) / price) * 100
            points.append(
                f"The mean analyst target implies about "
                f"{upside:.1f}% upside."
            )

        if forward_pe is not None and 0 < forward_pe < 30:
            points.append(
                "Forward valuation is within a moderate range "
                "relative to many growth companies."
            )

        if news_summary["overall_sentiment"] == "positive":
            points.append(
                "Recent relevant news sentiment is net positive."
            )

        score = stock.get("marketmind_score") or {}
        if (score.get("score") or 0) >= 70:
            points.append(
                "The MarketMind score indicates several supportive "
                "fundamental signals."
            )

        if not points:
            points.append(
                "The available data does not currently show a strong "
                "quantitative bull case."
            )

        return points

    @staticmethod
    def _build_bear_case(stock: dict, news_summary: dict) -> list[str]:
        points: list[str] = []

        pe = StockAnalysisService._number(stock.get("pe_ratio"))
        forward_pe = StockAnalysisService._number(
            stock.get("forward_pe")
        )
        revenue_growth = StockAnalysisService._number(
            stock.get("revenue_growth")
        )
        profit_margin = StockAnalysisService._number(
            stock.get("profit_margin")
        )
        high = StockAnalysisService._number(
            stock.get("fifty_two_week_high")
        )
        price = StockAnalysisService._number(
            stock.get("current_price")
        )

        if pe is not None and pe > 40:
            points.append(
                f"Trailing P/E of {pe:.1f} suggests a demanding valuation."
            )

        if forward_pe is not None and forward_pe > 35:
            points.append(
                f"Forward P/E of {forward_pe:.1f} leaves limited room "
                "for execution misses."
            )

        if revenue_growth is not None and revenue_growth < 0:
            points.append(
                f"Revenue is contracting at "
                f"{abs(revenue_growth) * 100:.1f}%."
            )

        if profit_margin is not None and profit_margin < 0:
            points.append("The company is currently unprofitable.")

        if (
            high is not None
            and price is not None
            and high > 0
            and price >= high * 0.95
        ):
            points.append(
                "The stock is trading near its 52-week high, "
                "which may increase downside sensitivity."
            )

        if news_summary["overall_sentiment"] == "negative":
            points.append(
                "Recent relevant news sentiment is net negative."
            )

        if not points:
            points.append(
                "No severe quantitative bear signal was detected, "
                "but valuation, competition, and execution still require review."
            )

        return points

    @staticmethod
    def _build_key_risks(stock: dict, news_summary: dict) -> list[str]:
        risks: list[str] = []

        pe = StockAnalysisService._number(stock.get("pe_ratio"))
        market_cap = StockAnalysisService._number(
            stock.get("market_cap")
        )
        revenue_growth = StockAnalysisService._number(
            stock.get("revenue_growth")
        )

        if pe is None:
            risks.append(
                "Valuation data is incomplete, reducing confidence."
            )
        elif pe > 40:
            risks.append("High valuation risk.")

        if revenue_growth is None:
            risks.append("Revenue-growth data is unavailable.")
        elif revenue_growth < 0.05:
            risks.append("Low or negative revenue-growth risk.")

        if market_cap is not None and market_cap < 2_000_000_000:
            risks.append("Smaller-company volatility and liquidity risk.")

        if news_summary["negative_count"] > 0:
            risks.append(
                f"{news_summary['negative_count']} recent relevant "
                "article(s) carry negative sentiment."
            )

        if not risks:
            risks.extend(
                [
                    "Competitive and industry execution risk.",
                    "Macroeconomic and market-volatility risk.",
                ]
            )

        return risks

    @staticmethod
    def _build_movement_explanation(
        stock: dict,
        news_summary: dict,
    ) -> str:
        symbol = stock.get("symbol", "The stock")

        if news_summary["article_count"] == 0:
            return (
                f"No highly relevant recent articles were found for "
                f"{symbol}. The current move may be driven by broader "
                "market, sector, earnings-expectation, or technical factors."
            )

        sentiment = news_summary["overall_sentiment"]

        if sentiment == "positive":
            return (
                f"Recent coverage for {symbol} is net positive, so favorable "
                "company developments or analyst commentary may be supporting "
                "investor sentiment."
            )

        if sentiment == "negative":
            return (
                f"Recent coverage for {symbol} is net negative, which may be "
                "adding pressure through company-specific concerns or weaker "
                "market expectations."
            )

        return (
            f"Recent coverage for {symbol} is mixed or neutral. The move may "
            "reflect a combination of company news, sector performance, "
            "valuation changes, and broader market conditions."
        )

    @staticmethod
    def _build_recommendation(
        stock: dict,
        news_summary: dict,
        exposure: dict,
    ) -> dict:
        score_data = stock.get("marketmind_score") or {}
        score = float(score_data.get("score") or 0)
        sentiment = news_summary["overall_sentiment"]

        adjusted_score = score

        if sentiment == "positive":
            adjusted_score += 5
        elif sentiment == "negative":
            adjusted_score -= 7

        pe = StockAnalysisService._number(stock.get("pe_ratio"))
        if pe is not None and pe > 45:
            adjusted_score -= 7

        growth = StockAnalysisService._number(
            stock.get("revenue_growth")
        )
        if growth is not None and growth > 0.15:
            adjusted_score += 5

        if exposure.get("allocation_percent", 0) >= 25:
            adjusted_score -= 5

        adjusted_score = max(0, min(100, adjusted_score))

        if adjusted_score >= 80:
            label = "strong research candidate"
        elif adjusted_score >= 65:
            label = "positive"
        elif adjusted_score >= 50:
            label = "neutral"
        elif adjusted_score >= 35:
            label = "cautious"
        else:
            label = "high risk"

        available_signals = sum(
            value is not None
            for value in [
                stock.get("current_price"),
                stock.get("pe_ratio"),
                stock.get("revenue_growth"),
                stock.get("profit_margin"),
                stock.get("analyst_target_price"),
            ]
        )

        confidence = min(
            95,
            45
            + available_signals * 8
            + min(news_summary["article_count"], 3) * 3,
        )

        reason = (
            f"The recommendation combines the MarketMind score "
            f"({score:.0f}/100), recent news sentiment "
            f"({sentiment}), valuation, growth, and portfolio exposure."
        )

        return {
            "label": label,
            "score": round(adjusted_score, 2),
            "confidence": confidence,
            "reason": reason,
            "disclaimer": (
                "This is an informational research classification, "
                "not personalized investment advice or a buy/sell instruction."
            ),
        }

    @staticmethod
    def analyze(
        symbol: str, 
        db: Session,
        user_id: int,
    ) -> dict:
        ticker = symbol.strip().upper()

        if not ticker:
            return {
                "symbol": ticker,
                "status": "needs_more_info",
                "error": "A stock ticker is required.",
            }

        stock = StockService.search_stock(ticker)

        if stock.get("error"):
            return {
                "symbol": ticker,
                "status": "not_found",
                "error": stock["error"],
                "stock": stock,
            }

        try:
            news = NewsService.search_news(ticker)
        except Exception:
            news = {
                "symbol": ticker,
                "news": [],
                "error": "Unable to fetch news",
            }

        try:
            portfolio = PortfolioService.calculate(db, user_id)
        except Exception:
            portfolio = {"holdings": []}

        news_summary = StockAnalysisService._build_news_summary(news)
        exposure = StockAnalysisService._build_portfolio_exposure(
            ticker,
            portfolio,
        )

        bull_case = StockAnalysisService._build_bull_case(
            stock,
            news_summary,
        )
        bear_case = StockAnalysisService._build_bear_case(
            stock,
            news_summary,
        )
        key_risks = StockAnalysisService._build_key_risks(
            stock,
            news_summary,
        )
        recommendation = StockAnalysisService._build_recommendation(
            stock,
            news_summary,
            exposure,
        )

        return {
            "symbol": ticker,
            "status": "success",
            "stock": stock,
            "news_summary": news_summary,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "key_risks": key_risks,
            "why_moving": (
                StockAnalysisService._build_movement_explanation(
                    stock,
                    news_summary,
                )
            ),
            "portfolio_exposure": exposure,
            "recommendation": recommendation,
        }
