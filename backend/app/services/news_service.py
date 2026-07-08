import logging
import yfinance as yf

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

                results.append({
                    "title": content.get("title"),
                    "publisher": content.get("provider", {}).get("displayName"),
                    "link": content.get("canonicalUrl", {}).get("url"),
                    "published_at": content.get("pubDate"),
                    "summary": content.get("summary"),
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