from app.services.price_service import PriceService

print(PriceService.get_live_price("NVDA"))
print(PriceService.get_live_price("AAPL"))
print(PriceService.get_live_price("TRENT.NS"))
print(PriceService.get_live_price("BTC-USD"))