from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.models import Portfolio


class PortfolioSnapshotRepository:

    @staticmethod
    def _portfolio_id(
        db: Session,
        user_id: int,
    ) -> int:
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .order_by(Portfolio.id.asc())
            .first()
        )

        if portfolio is None:
            raise ValueError("User portfolio does not exist.")

        return portfolio.id

    @staticmethod
    def get_latest(
        db: Session,
        user_id: int,
    ):
        portfolio_id = PortfolioSnapshotRepository._portfolio_id(
            db,
            user_id,
        )

        return (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id
            )
            .order_by(PortfolioSnapshot.created_at.desc())
            .first()
        )

    @staticmethod
    def get_previous(
        db: Session,
        user_id: int,
    ):
        portfolio_id = PortfolioSnapshotRepository._portfolio_id(
            db,
            user_id,
        )

        return (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id
            )
            .order_by(PortfolioSnapshot.created_at.desc())
            .offset(1)
            .first()
        )

    @staticmethod
    def get_for_day(
        db: Session,
        user_id: int,
        target_date: date,
    ):
        portfolio_id = PortfolioSnapshotRepository._portfolio_id(
            db,
            user_id,
        )
        start = datetime.combine(target_date, time.min)
        end = datetime.combine(target_date, time.max)

        return (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.created_at >= start,
                PortfolioSnapshot.created_at <= end,
            )
            .order_by(PortfolioSnapshot.created_at.desc())
            .first()
        )

    @staticmethod
    def list_history(
        db: Session,
        user_id: int,
        limit: int = 365,
    ):
        portfolio_id = PortfolioSnapshotRepository._portfolio_id(
            db,
            user_id,
        )

        items = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id
            )
            .order_by(PortfolioSnapshot.created_at.desc())
            .limit(limit)
            .all()
        )

        return list(reversed(items))

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        portfolio: dict,
    ):
        portfolio_id = PortfolioSnapshotRepository._portfolio_id(
            db,
            user_id,
        )
        summary = portfolio["summary"]
        health = portfolio["health_score"]

        snapshot = PortfolioSnapshot(
            portfolio_id=portfolio_id,
            total_cost=summary["total_cost"],
            total_value=summary["total_value"],
            total_profit=summary["total_profit"],
            total_return_percent=summary[
                "total_return_percent"
            ],
            health_score=health["score"],
            holdings_count=summary["holdings_count"],
        )

        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot
