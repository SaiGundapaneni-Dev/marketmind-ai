from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)
from app.services.portfolio_calculation_service import (
    PortfolioCalculationService,
)
from app.services.portfolio_health_service import (
    PortfolioHealthService,
)


class PortfolioService:
    @staticmethod
    def create_holding(db: Session, holding_data):
        return PortfolioRepository.create_holding(db, holding_data)

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
    def calculate(db: Session) -> dict:
        portfolio = PortfolioCalculationService.calculate(db)

        holdings = portfolio["holdings"]
        allocation = portfolio["allocation"]

        concentration_risk = (
            PortfolioAnalyticsService.calculate_concentration_risk(
                holdings
            )
        )

        performance_insights = (
            PortfolioAnalyticsService.calculate_performance_insights(
                holdings
            )
        )

        health_score = (
            PortfolioHealthService.calculate_health_score(
                holdings,
                concentration_risk,
                performance_insights,
            )
        )

        actionable_insights = (
            PortfolioAnalyticsService.generate_actionable_insights(
                holdings,
                allocation,
                concentration_risk,
                performance_insights,
                health_score,
            )
        )

        return {
            "summary": portfolio["summary"],
            "allocation": allocation,
            "concentration_risk": concentration_risk,
            "performance_insights": performance_insights,
            "health_score": health_score,
            "actionable_insights": actionable_insights,
            "holdings": holdings,
        }
