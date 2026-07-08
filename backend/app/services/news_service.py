import logging
import yfinance as yf

from app.services.sentiment_service import SentimentService

logger = logging.getLogger("marketmind")


class NewsService:

    @staticmethod
    def search_news(symbol: str):
        try:
            ticker_symbol = symbol.upper()
            ticker = yf.Ticker(ticker_symbol)

            news_items = ticker.news or []
            results = []

            for item in news_items[:10]:
                content = item.get("content", item)

                title = content.get("title")
                summary = content.get("summary")

                text_for_sentiment = f"{title or ''} {summary or ''}"

                results.append({
                    "title": title,
                    "publisher": content.get("provider", {}).get("displayName"),
                    "link": content.get("canonicalUrl", {}).get("url"),
                    "published_at": content.get("pubDate"),
                    "summary": summary,
                    "sentiment": SentimentService.analyze(text_for_sentiment),
                })

            return {
                "symbol": ticker_symbol,
                "count": len(results),
                "news": results
            }

        except Exception:
            logger.exception("Failed to fetch news for symbol: %s", symbol)

            return {
                "symbol": symbol.upper(),
                "count": 0,
                "news": [],
                "error": "Unable to fetch news"
            }