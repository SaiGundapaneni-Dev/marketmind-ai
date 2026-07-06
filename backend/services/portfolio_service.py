import json
from backend.services.price_service import get_price

def load_portfolio():
    with open("backend/portfolio.json", "r") as f:
        return json.load(f)


def calculate_portfolio():
    portfolio = load_portfolio()

    result = []
    total_value = 0
    total_cost = 0

    for asset_class, holdings in portfolio.items():
        for h in holdings:
            price = get_price(h["symbol"])
            if price is None:
                continue

            value = price * h["qty"]
            cost = h["avg_price"] * h["qty"]

            pnl = value - cost

            result.append({
                "symbol": h["symbol"],
                "qty": h["qty"],
                "price": price,
                "value": value,
                "pnl": pnl,
                "asset_class": asset_class
            })

            total_value += value
            total_cost += cost

    return {
        "holdings": result,
        "total_value": total_value,
        "total_pnl": total_value - total_cost
    }