from collections import defaultdict

from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.services.price_service import PriceService


class PortfolioService:

    @staticmethod
    def create_holding(db: Session, holding_data):
        return PortfolioRepository.create_holding(
            db,
            holding_data,
        )

    @staticmethod
    def update_holding(
        db: Session,
        holding_id: int,
        holding_data,
    ):
        return PortfolioRepository.update_holding(
            db,
            holding_id,
            holding_data,
        )

    @staticmethod
    def get_holding_by_id(
        db: Session,
        holding_id: int,
    ):
        return PortfolioRepository.get_holding_by_id(
            db,
            holding_id,
        )

    @staticmethod
    def delete_holding(
        db: Session,
        holding_id: int,
    ):
        return PortfolioRepository.delete_holding(
            db,
            holding_id,
        )

    @staticmethod
    def calculate(db: Session):
        db_holdings = PortfolioRepository.get_holdings(db)

        holdings = []

        total_cost = 0.0
        total_value = 0.0

        priced_holdings_count = 0
        unpriced_holdings_count = 0

        for asset in db_holdings:
            current_price = PriceService.get_live_price(
                asset.symbol
            )

            quantity = float(asset.quantity)
            average_price = float(asset.average_price)

            cost = quantity * average_price
            total_cost += cost

            if current_price is None:
                unpriced_holdings_count += 1

                holdings.append({
                    "id": asset.id,
                    "asset_type": asset.asset_type,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "quantity": quantity,
                    "average_price": round(
                        average_price,
                        2,
                    ),
                    "current_price": None,
                    "cost": round(cost, 2),
                    "current_value": 0.0,
                    "profit": 0.0,
                    "profit_percent": 0.0,
                    "allocation_percent": 0.0,
                    "price_status": "unavailable",
                })

                continue

            priced_holdings_count += 1

            current_price = float(current_price)

            value = quantity * current_price
            profit = value - cost

            profit_percent = (
                (profit / cost) * 100
                if cost > 0
                else 0.0
            )

            total_value += value

            holdings.append({
                "id": asset.id,
                "asset_type": asset.asset_type,
                "symbol": asset.symbol,
                "name": asset.name,
                "quantity": quantity,
                "average_price": round(
                    average_price,
                    2,
                ),
                "current_price": round(
                    current_price,
                    2,
                ),
                "cost": round(cost, 2),
                "current_value": round(value, 2),
                "profit": round(profit, 2),
                "profit_percent": round(
                    profit_percent,
                    2,
                ),
                "allocation_percent": 0.0,
                "price_status": "available",
            })

        allocation_by_asset_type = defaultdict(float)

        for holding in holdings:
            current_value = holding["current_value"]

            allocation_percent = (
                (current_value / total_value) * 100
                if total_value > 0
                else 0.0
            )

            holding["allocation_percent"] = round(
                allocation_percent,
                2,
            )

            asset_type = (
                holding["asset_type"]
                or "unknown"
            )

            allocation_by_asset_type[
                asset_type
            ] += current_value

        asset_type_allocation = []

        for asset_type, value in allocation_by_asset_type.items():
            percentage = (
                (value / total_value) * 100
                if total_value > 0
                else 0.0
            )

            asset_type_allocation.append({
                "asset_type": asset_type,
                "value": round(value, 2),
                "allocation_percent": round(
                    percentage,
                    2,
                ),
            })

        asset_type_allocation.sort(
            key=lambda item: item["value"],
            reverse=True,
        )

        largest_holding = None

        priced_holdings = [
            holding
            for holding in holdings
            if holding["current_value"] > 0
        ]

        if priced_holdings:
            largest = max(
                priced_holdings,
                key=lambda holding: holding[
                    "current_value"
                ],
            )

            largest_holding = {
                "symbol": largest["symbol"],
                "name": largest["name"],
                "current_value": largest[
                    "current_value"
                ],
                "allocation_percent": largest[
                    "allocation_percent"
                ],
            }

        total_profit = total_value - total_cost

        total_return = (
            (total_profit / total_cost) * 100
            if total_cost > 0
            else 0.0
        )

        return {
            "summary": {
                "total_cost": round(total_cost, 2),
                "total_value": round(total_value, 2),
                "total_profit": round(
                    total_profit,
                    2,
                ),
                "total_return_percent": round(
                    total_return,
                    2,
                ),
                "holdings_count": len(holdings),
                "priced_holdings_count": (
                    priced_holdings_count
                ),
                "unpriced_holdings_count": (
                    unpriced_holdings_count
                ),
            },
            "allocation": {
                "by_asset_type": (
                    asset_type_allocation
                ),
                "largest_holding": (
                    largest_holding
                ),
            },
            "holdings": holdings,
        }