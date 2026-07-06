import json
from app.services.price_service import PriceService


class PortfolioService:

    @staticmethod
    def load_portfolio():
        with open("portfolio.json", "r") as f:
            return json.load(f)

    @staticmethod
    def calculate():

        portfolio = PortfolioService.load_portfolio()

        holdings = []

        total_cost = 0
        total_value = 0

        for asset_type, assets in portfolio.items():

            for asset in assets:
                    
                current_price = PriceService.get_live_price(asset["symbol"])

                if current_price is None:
                    holdings.append({
                        "asset_type": asset_type,
                        "symbol": asset["symbol"],
                        "name": asset.get("name", asset["symbol"]),
                        "quantity": asset["qty"],
                        "average_price": round(asset["avg_price"], 2),
                        "current_price": 0,
                        "cost": round(asset["qty"] * asset["avg_price"], 2),
                        "current_value": 0,
                        "profit": 0,
                        "profit_percent": 0
                    })
                    continue

                cost = asset["qty"] * asset["avg_price"]
                value = asset["qty"] * current_price

                profit = value - cost

                profit_percent = (profit / cost) * 100 if cost > 0 else 0

                holdings.append({
                    "asset_type": asset_type,
                    "symbol": asset["symbol"],
                    "name": asset["name"],
                    "quantity": asset["qty"],
                    "average_price": round(asset["avg_price"], 2),
                    "current_price": round(current_price, 2),
                    "cost": round(cost, 2),
                    "current_value": round(value, 2),
                    "profit": round(profit, 2),
                    "profit_percent": round(profit_percent, 2)
                })

                total_cost += cost
                total_value += value

        total_profit = total_value - total_cost

        total_return = (
            (total_profit / total_cost) * 100
            if total_cost > 0 else 0
        )

        return {
            "summary": {
                "total_cost": round(total_cost, 2),
                "total_value": round(total_value, 2),
                "total_profit": round(total_profit, 2),
                "total_return_percent": round(total_return, 2)
            },
            "holdings": holdings
        }