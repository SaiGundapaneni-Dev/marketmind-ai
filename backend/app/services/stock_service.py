import logging
import yfinance as yf

logger = logging.getLogger("marketmind")


class StockService:

    @staticmethod
    def search_stock(symbol: str):
        try:
            ticker_symbol = symbol.upper()
            ticker = yf.Ticker(ticker_symbol)

            info = ticker.info
            history = ticker.history(period="1d")

            current_price = None

            if not history.empty:
                current_price = round(float(history["Close"].iloc[-1]), 2)

            return {
                "symbol": ticker_symbol,
                "company_name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "current_price": current_price,
                "currency": info.get("currency"),
                "website": info.get("website"),
                "summary": info.get("longBusinessSummary"),
                
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "eps": info.get("trailingEps"),
                "profit_margin": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "analyst_target_price": info.get("targetMeanPrice"),
                "recommendation": info.get("recommendationKey"),
            }

        except Exception:
            logger.exception("Failed to search stock: %s", symbol)
            return {
                "symbol": symbol.upper(),
                "error": "Unable to fetch stock data"
            }