from sqlalchemy.orm import Session

from app.services.portfolio_service import PortfolioService
from app.services.portfolio_score_service import PortfolioScoreService
from app.services.portfolio_intelligence_service import PortfolioIntelligenceService
from app.services.portfolio_history_service import PortfolioHistoryService


class InvestmentContextService:

    @staticmethod
    def build(db: Session, user_id: int):

        return {
            "portfolio":
                PortfolioService.calculate(db, user_id),

            "portfolio_score":
                PortfolioScoreService.generate(db, user_id),

            "portfolio_intelligence":
                PortfolioIntelligenceService.generate(db, user_id),

            "portfolio_history":
                PortfolioHistoryService.get_history(
                    db,
                    user_id,
                    limit=30,
                ),

            "goals": [],
            "watchlists": [],
            "investment_theses": [],
            "research_notes": [],

            "context_version": "1.0",
        }