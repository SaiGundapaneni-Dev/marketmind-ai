from sqlalchemy.orm import Session
from app.models import Holding


class PortfolioRepository:

    @staticmethod
    def get_holdings(db: Session):
        return db.query(Holding).all()