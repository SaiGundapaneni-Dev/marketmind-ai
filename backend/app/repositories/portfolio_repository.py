from sqlalchemy.orm import Session

from app.models import Holding


class PortfolioRepository:

    @staticmethod
    def get_holdings(db: Session):
        return db.query(Holding).all()

    @staticmethod
    def create_holding(db: Session, holding_data):
        holding = Holding(
            asset_type=holding_data.asset_type,
            symbol=holding_data.symbol.upper(),
            name=holding_data.name,
            quantity=holding_data.quantity,
            average_price=holding_data.average_price,
            currency=holding_data.currency.upper(),
            portfolio_id=holding_data.portfolio_id
        )

        db.add(holding)
        db.commit()
        db.refresh(holding)

        return holding