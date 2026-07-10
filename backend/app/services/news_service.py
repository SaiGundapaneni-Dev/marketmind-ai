import logging
import yfinance as yf

from app.services.sentiment_service import SentimentService

logger = logging.getLogger("marketmind")


class NewsService:

    @staticmethod
    def _build_keywords(symbol: str, company_name: str | None):
        keywords = {symbol.lower()}

        if company_name:
            clean_name = (
                company_name
                .replace("Inc.", "")
                .replace("Corporation", "")
                .replace("Corp.", "")
                .replace("Class A", "")
                .replace("Common Stock", "")
                .strip()
            )

            if clean_name:
                keywords.add(clean_name.lower())

            for word in clean_name.split():
                if len(word) > 3:
                    keywords.add(word.lower())

        return list(keywords)

    @staticmethod
    def _relevance_score(text: str, keywords: list[str]):
        text = (text or "").lower()

        score = 0

        for keyword in keywords:
            if keyword and keyword in text:
                score += 1

        return score

    @staticmethod
    def search_news(symbol: str):
        try:
            ticker_symbol = symbol.upper()
            ticker = yf.Ticker(ticker_symbol)

            info = ticker.info or {}
            company_name = info.get("longName") or info.get("shortName")

            keywords = NewsService._build_keywords(
                ticker_symbol,
                company_name
            )

            news_items = ticker.news or []
            results = []
            seen_links = set()

            for item in news_items:
                content = item.get("content", item)

                title = content.get("title")
                summary = content.get("summary")
                link = content.get("canonicalUrl", {}).get("url")

                combined_text = f"{title or ''} {summary or ''}"

                relevance_score = NewsService._relevance_score(
                    combined_text,
                    keywords
                )

                if relevance_score == 0:
                    continue

                if link and link in seen_links:
                    continue

                if link:
                    seen_links.add(link)

                sentiment_result = SentimentService.analyze(combined_text)

                results.append({
                    "title": title,
                    "publisher": content.get("provider", {}).get("displayName"),
                    "link": link,
                    "published_at": content.get("pubDate"),
                    "summary": summary,
                    "sentiment": sentiment_result["label"],
                    "sentiment_confidence": sentiment_result["confidence"],
                    "sentiment_reason": sentiment_result["reason"],
                    "relevance_score": relevance_score,
                })

            return {
                "symbol": ticker_symbol,
                "company_name": company_name,
                "keywords_used": keywords,
                "count": len(results),
                "news": results[:10]
            }

        except Exception:
            logger.exception("Failed to fetch news for symbol: %s", symbol)

            return {
                "symbol": symbol.upper(),
                "count": 0,
                "news": [],
                "error": "Unable to fetch news"
            }