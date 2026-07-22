from sqlalchemy.orm import Session
from app.models.models import Portfolio
from app.models.investment_thesis import InvestmentThesis
from app.models.models import Holding


class ThesisAIRepository:

    @staticmethod
    def get_user_thesis(
        db: Session,
        user_id: int,
        symbol: str,
    ):
        return (
            db.query(InvestmentThesis)
            .join(
                Holding,
                Holding.id == InvestmentThesis.holding_id,
            )
            .join(
                Portfolio,
                Portfolio.id == Holding.portfolio_id,
            )
            .filter(
                Portfolio.user_id == user_id,
                Holding.symbol == symbol.upper(),
            )
            .first()
        )