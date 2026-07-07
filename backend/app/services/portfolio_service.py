from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.services.price_service import PriceService


class PortfolioService:
    
    @staticmethod
    def create_holding(db: Session, holding_data):
        return PortfolioRepository.create_holding(
            db,
            holding_data
        )
        
    @staticmethod
    def update_holding(db: Session, holding_id: int, holding_data):
        return PortfolioRepository.update_holding(db, holding_id, holding_data)
        
        
    @staticmethod
    def get_holding_by_id(db: Session, holding_id: int):
        return PortfolioRepository.get_holding_by_id(db, holding_id)
    
    @staticmethod
    def delete_holding(db: Session, holding_id: int):
        return PortfolioRepository.delete_holding(db, holding_id)

    @staticmethod
    def calculate(db: Session):

        db_holdings = PortfolioRepository.get_holdings(db)

        holdings = []

        total_cost = 0
        total_value = 0

        for asset in db_holdings:

            current_price = PriceService.get_live_price(asset.symbol)

            cost = asset.quantity * asset.average_price

            if current_price is None:
                holdings.append({
                    "asset_type": asset.asset_type,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "quantity": asset.quantity,
                    "average_price": round(asset.average_price, 2),
                    "current_price": 0,
                    "cost": round(cost, 2),
                    "current_value": 0,
                    "profit": 0,
                    "profit_percent": 0
                })
                total_cost += cost
                continue

            value = asset.quantity * current_price
            profit = value - cost
            profit_percent = (profit / cost) * 100 if cost > 0 else 0

            holdings.append({
                "id": asset.id,
                "asset_type": asset.asset_type,
                "symbol": asset.symbol,
                "name": asset.name,
                "quantity": asset.quantity,
                "average_price": round(asset.average_price, 2),
                "current_price": round(current_price, 2),
                "cost": round(cost, 2),
                "current_value": round(value, 2),
                "profit": round(profit, 2),
                "profit_percent": round(profit_percent, 2)
            })

            total_cost += cost
            total_value += value

        total_profit = total_value - total_cost
        total_return = (total_profit / total_cost) * 100 if total_cost > 0 else 0

        return {
            "summary": {
                "total_cost": round(total_cost, 2),
                "total_value": round(total_value, 2),
                "total_profit": round(total_profit, 2),
                "total_return_percent": round(total_return, 2)
            },
            "holdings": holdings
        }