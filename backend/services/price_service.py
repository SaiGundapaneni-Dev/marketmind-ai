import yfinance as yf

def get_price(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        return None

    return float(data["Close"].iloc[-1])