from sqlalchemy.orm import Session

from app.models.investment_thesis import InvestmentThesis
from app.models.models import Holding, Portfolio
from app.schemas.investment_thesis_schema import (
    InvestmentThesisCreate,
    InvestmentThesisUpdate,
)


class InvestmentThesisRepository:
    @staticmethod
    def get_holding_for_user(
        db: Session,
        holding_id: int,
        user_id: int,
    ) -> Holding | None:
        """
        Return a holding only when it belongs to a portfolio
        owned by the authenticated user.
        """

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
    def get_by_holding_id(
        db: Session,
        holding_id: int,
        user_id: int,
    ) -> InvestmentThesis | None:
        """
        Retrieve an investment thesis only when its holding
        belongs to the authenticated user.
        """

        return (
            db.query(InvestmentThesis)
            .join(
                Holding,
                InvestmentThesis.holding_id == Holding.id,
            )
            .join(
                Portfolio,
                Holding.portfolio_id == Portfolio.id,
            )
            .filter(
                InvestmentThesis.holding_id == holding_id,
                Portfolio.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        thesis_data: InvestmentThesisCreate,
        user_id: int,
    ) -> InvestmentThesis:
        """
        Create a thesis for a holding owned by the user.

        This method assumes that the service layer has already
        checked that the holding exists and that no thesis has
        been created for it.
        """

        holding = InvestmentThesisRepository.get_holding_for_user(
            db=db,
            holding_id=thesis_data.holding_id,
            user_id=user_id,
        )

        if holding is None:
            raise ValueError(
                "The selected holding was not found."
            )

        existing_thesis = (
            InvestmentThesisRepository.get_by_holding_id(
                db=db,
                holding_id=thesis_data.holding_id,
                user_id=user_id,
            )
        )

        if existing_thesis is not None:
            raise ValueError(
                "An investment thesis already exists for this holding."
            )

        investment_thesis = InvestmentThesis(
            holding_id=thesis_data.holding_id,
            thesis=thesis_data.thesis.strip(),
            target_price=thesis_data.target_price,
            investment_horizon=(
                thesis_data.investment_horizon.strip()
                if thesis_data.investment_horizon
                else None
            ),
            conviction_score=thesis_data.conviction_score,
            risk_level=thesis_data.risk_level,
            buy_reasons=(
                thesis_data.buy_reasons.strip()
                if thesis_data.buy_reasons
                else None
            ),
            sell_conditions=(
                thesis_data.sell_conditions.strip()
                if thesis_data.sell_conditions
                else None
            ),
            notes=(
                thesis_data.notes.strip()
                if thesis_data.notes
                else None
            ),
            review_date=thesis_data.review_date,
        )

        try:
            db.add(investment_thesis)
            db.commit()
            db.refresh(investment_thesis)

            return investment_thesis

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update(
        db: Session,
        thesis: InvestmentThesis,
        thesis_data: InvestmentThesisUpdate,
    ) -> InvestmentThesis:
        """
        Update only the fields supplied in the request.
        """

        update_data = thesis_data.model_dump(
            exclude_unset=True,
        )

        text_fields = {
            "thesis",
            "investment_horizon",
            "buy_reasons",
            "sell_conditions",
            "notes",
        }

        for field_name, field_value in update_data.items():
            if (
                field_name in text_fields
                and isinstance(field_value, str)
            ):
                field_value = field_value.strip()

            setattr(
                thesis,
                field_name,
                field_value,
            )

        try:
            db.commit()
            db.refresh(thesis)

            return thesis

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete(
        db: Session,
        thesis: InvestmentThesis,
    ) -> None:
        """
        Permanently delete an investment thesis.
        """

        try:
            db.delete(thesis)
            db.commit()

        except Exception:
            db.rollback()
            raise