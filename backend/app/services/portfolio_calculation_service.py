from collections import defaultdict

from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.services.price_service import PriceService


class PortfolioCalculationService:
    @staticmethod
    def calculate(
        db: Session,
        user_id: int,
    ) -> dict:
        db_holdings = PortfolioRepository.get_holdings(
            db,
            user_id,
        )
        
        holdings = []
        total_cost = 0.0
        total_value = 0.0
        priced_count = 0
        unpriced_count = 0

        for asset in db_holdings:
            current_price = PriceService.get_live_price(asset.symbol)
            quantity = float(asset.quantity)
            average_price = float(asset.average_price)
            cost = quantity * average_price
            total_cost += cost

            holding = {
                "id": asset.id,
                "asset_type": asset.asset_type,
                "symbol": asset.symbol,
                "name": asset.name,
                "quantity": quantity,
                "average_price": round(average_price, 2),
                "cost": round(cost, 2),
                "allocation_percent": 0.0,
            }

            if current_price is None:
                unpriced_count += 1
                holding.update({
                    "current_price": None,
                    "current_value": 0.0,
                    "profit": 0.0,
                    "profit_percent": 0.0,
                    "price_status": "unavailable",
                })
                holdings.append(holding)
                continue

            priced_count += 1
            current_price = float(current_price)
            current_value = quantity * current_price
            profit = current_value - cost
            profit_percent = (
                (profit / cost) * 100
                if cost > 0
                else 0.0
            )
            total_value += current_value

            holding.update({
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "profit": round(profit, 2),
                "profit_percent": round(profit_percent, 2),
                "price_status": "available",
            })
            holdings.append(holding)

        allocation_by_asset_type = defaultdict(float)

        for holding in holdings:
            value = holding["current_value"]
            holding["allocation_percent"] = round(
                (value / total_value) * 100
                if total_value > 0
                else 0.0,
                2,
            )
            allocation_by_asset_type[
                holding["asset_type"] or "unknown"
            ] += value

        by_asset_type = []

        for asset_type, value in allocation_by_asset_type.items():
            by_asset_type.append({
                "asset_type": asset_type,
                "value": round(value, 2),
                "allocation_percent": round(
                    (value / total_value) * 100
                    if total_value > 0
                    else 0.0,
                    2,
                ),
            })

        by_asset_type.sort(
            key=lambda item: item["value"],
            reverse=True,
        )

        priced_holdings = [
            h for h in holdings
            if h["price_status"] == "available"
        ]

        largest_holding = None

        if priced_holdings:
            largest = max(
                priced_holdings,
                key=lambda h: h["current_value"],
            )
            largest_holding = {
                "symbol": largest["symbol"],
                "name": largest["name"],
                "current_value": largest["current_value"],
                "allocation_percent": largest[
                    "allocation_percent"
                ],
            }

        total_profit = total_value - total_cost
        total_return_percent = (
            (total_profit / total_cost) * 100
            if total_cost > 0
            else 0.0
        )

        return {
            "summary": {
                "total_cost": round(total_cost, 2),
                "total_value": round(total_value, 2),
                "total_profit": round(total_profit, 2),
                "total_return_percent": round(
                    total_return_percent,
                    2,
                ),
                "holdings_count": len(holdings),
                "priced_holdings_count": priced_count,
                "unpriced_holdings_count": unpriced_count,
            },
            "allocation": {
                "by_asset_type": by_asset_type,
                "largest_holding": largest_holding,
            },
            "holdings": holdings,
        }
