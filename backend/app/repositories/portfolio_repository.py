from sqlalchemy.orm import Session

from app.models.models import Holding, Portfolio


class PortfolioRepository:

    @staticmethod
    def get_or_create_default_portfolio(
        db: Session,
        user_id: int,
    ):
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .order_by(Portfolio.id.asc())
            .first()
        )

        if portfolio is not None:
            return portfolio

        portfolio = Portfolio(
            name="My Portfolio",
            user_id=user_id,
        )

        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

        return portfolio

    @staticmethod
    def get_holdings(
        db: Session,
        user_id: int,
    ):
        portfolio = (
            PortfolioRepository.get_or_create_default_portfolio(
                db,
                user_id,
            )
        )

        return (
            db.query(Holding)
            .filter(Holding.portfolio_id == portfolio.id)
            .order_by(Holding.created_at.asc())
            .all()
        )

    @staticmethod
    def create_holding(
        db: Session,
        user_id: int,
        holding_data,
    ):
        portfolio = (
            PortfolioRepository.get_or_create_default_portfolio(
                db,
                user_id,
            )
        )

        holding = Holding(
            asset_type=holding_data.asset_type,
            symbol=holding_data.symbol.upper(),
            name=holding_data.name,
            quantity=holding_data.quantity,
            average_price=holding_data.average_price,
            currency=holding_data.currency.upper(),
            portfolio_id=portfolio.id,
        )

        db.add(holding)
        db.commit()
        db.refresh(holding)

        return holding

    @staticmethod
    def get_holding_by_id(
        db: Session,
        user_id: int,
        holding_id: int,
    ):
        return (
            db.query(Holding)
            .join(
                Portfolio,
                Holding.portfolio_id == Portfolio.id,
            )
            .filter(
                Holding.id == holding_id,
                Portfolio.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def delete_holding(
        db: Session,
        user_id: int,
        holding_id: int,
    ):
        holding = PortfolioRepository.get_holding_by_id(
            db,
            user_id,
            holding_id,
        )

        if holding is None:
            return None

        db.delete(holding)
        db.commit()

        return holding

    @staticmethod
    def update_holding(
        db: Session,
        user_id: int,
        holding_id: int,
        holding_data,
    ):
        holding = PortfolioRepository.get_holding_by_id(
            db,
            user_id,
            holding_id,
        )

        if holding is None:
            return None

        holding.asset_type = holding_data.asset_type
        holding.symbol = holding_data.symbol.upper()
        holding.name = holding_data.name
        holding.quantity = holding_data.quantity
        holding.average_price = holding_data.average_price
        holding.currency = holding_data.currency.upper()

        db.commit()
        db.refresh(holding)

        return holding
