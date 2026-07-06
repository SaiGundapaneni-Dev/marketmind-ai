import yfinance as yf


class PriceService:

    @staticmethod
    def get_live_price(symbol: str):

        ticker = yf.Ticker(symbol)

        history = ticker.history(period="1d")

        if history.empty:
            return None

        return round(float(history["Close"].iloc[-1]), 2)