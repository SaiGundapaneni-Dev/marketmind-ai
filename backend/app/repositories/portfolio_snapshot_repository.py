from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot


class PortfolioSnapshotRepository:

    @staticmethod
    def get_latest(db: Session):
        return (
            db.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.created_at.desc())
            .first()
        )

    @staticmethod
    def get_previous(db: Session):
        return (
            db.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.created_at.desc())
            .offset(1)
            .first()
        )

    @staticmethod
    def get_for_day(db: Session, target_date: date):
        start = datetime.combine(target_date, time.min)
        end = datetime.combine(target_date, time.max)

        return (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.created_at >= start,
                PortfolioSnapshot.created_at <= end,
            )
            .order_by(PortfolioSnapshot.created_at.desc())
            .first()
        )

    @staticmethod
    def list_history(db: Session, limit: int = 365):
        items = (
            db.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(items))

    @staticmethod
    def create(db: Session, portfolio: dict):
        summary = portfolio["summary"]
        health = portfolio["health_score"]

        snapshot = PortfolioSnapshot(
            total_cost=summary["total_cost"],
            total_value=summary["total_value"],
            total_profit=summary["total_profit"],
            total_return_percent=summary["total_return_percent"],
            health_score=health["score"],
            holdings_count=summary["holdings_count"],
        )

        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot
