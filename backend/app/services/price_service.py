import logging
import yfinance as yf

logger = logging.getLogger("marketmind")


class PriceService:

    @staticmethod
    def get_live_price(symbol: str):
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1d", timeout=10)

            if history.empty:
                logger.warning("No price data found for symbol: %s", symbol)
                return None

            return round(float(history["Close"].iloc[-1]), 2)

        except Exception as exc:
            logger.exception("Failed to fetch price for symbol: %s", symbol)
            return None