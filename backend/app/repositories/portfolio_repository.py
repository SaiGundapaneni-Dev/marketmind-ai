from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Holding, Portfolio


class PortfolioRepository:
    @staticmethod
    def get_or_create_default_portfolio(
        db: Session,
        user_id: int,
    ) -> Portfolio:
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
    ) -> list[Holding]:
        portfolio = (
            PortfolioRepository.get_or_create_default_portfolio(
                db,
                user_id,
            )
        )

        return (
            db.query(Holding)
            .filter(
                Holding.portfolio_id == portfolio.id,
            )
            .order_by(Holding.created_at.asc())
            .all()
        )

    @staticmethod
    def get_holding_by_symbol(
        db: Session,
        user_id: int,
        symbol: str,
    ) -> Holding | None:
        """
        Find a holding by symbol inside the user's default portfolio.

        Symbol matching is case-insensitive.
        """

        portfolio = (
            PortfolioRepository.get_or_create_default_portfolio(
                db,
                user_id,
            )
        )

        normalized_symbol = symbol.strip().upper()

        return (
            db.query(Holding)
            .filter(
                Holding.portfolio_id == portfolio.id,
                func.upper(Holding.symbol)
                == normalized_symbol,
            )
            .first()
        )

    @staticmethod
    def create_holding(
        db: Session,
        user_id: int,
        holding_data,
    ) -> Holding:
        portfolio = (
            PortfolioRepository.get_or_create_default_portfolio(
                db,
                user_id,
            )
        )

        symbol = holding_data.symbol.strip().upper()

        holding = Holding(
            asset_type=holding_data.asset_type.strip().lower(),
            symbol=symbol,
            name=(
                holding_data.name.strip()
                if holding_data.name
                else symbol
            ),
            quantity=float(holding_data.quantity),
            average_price=float(
                holding_data.average_price
            ),
            currency=holding_data.currency.strip().upper(),
            portfolio_id=portfolio.id,
        )

        db.add(holding)
        db.commit()
        db.refresh(holding)

        return holding

    @staticmethod
    def add_holding_without_commit(
        db: Session,
        portfolio_id: int,
        holding_data,
    ) -> Holding:
        """
        Add a holding to the current database transaction.

        The caller is responsible for committing or rolling back.
        """

        symbol = holding_data.symbol.strip().upper()

        holding = Holding(
            asset_type=holding_data.asset_type.strip().lower(),
            symbol=symbol,
            name=(
                holding_data.name.strip()
                if holding_data.name
                else symbol
            ),
            quantity=float(holding_data.quantity),
            average_price=float(
                holding_data.average_price
            ),
            currency=holding_data.currency.strip().upper(),
            portfolio_id=portfolio_id,
        )

        db.add(holding)

        return holding

    @staticmethod
    def get_holding_by_id(
        db: Session,
        user_id: int,
        holding_id: int,
    ) -> Holding | None:
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
    ) -> Holding | None:
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
    ) -> Holding | None:
        holding = PortfolioRepository.get_holding_by_id(
            db,
            user_id,
            holding_id,
        )

        if holding is None:
            return None

        symbol = holding_data.symbol.strip().upper()

        holding.asset_type = (
            holding_data.asset_type.strip().lower()
        )
        holding.symbol = symbol
        holding.name = (
            holding_data.name.strip()
            if holding_data.name
            else symbol
        )
        holding.quantity = float(
            holding_data.quantity
        )
        holding.average_price = float(
            holding_data.average_price
        )
        holding.currency = (
            holding_data.currency.strip().upper()
        )

        db.commit()
        db.refresh(holding)

        return holding