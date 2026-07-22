from sqlalchemy.orm import Session

from app.models.investment_thesis import InvestmentThesis
from app.repositories.investment_thesis_repository import (
    InvestmentThesisRepository,
)
from app.schemas.investment_thesis_schema import (
    InvestmentThesisCreate,
    InvestmentThesisUpdate,
)


class InvestmentThesisService:
    @staticmethod
    def create_thesis(
        db: Session,
        thesis_data: InvestmentThesisCreate,
        user_id: int,
    ) -> InvestmentThesis:
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

        return InvestmentThesisRepository.create(
            db=db,
            thesis_data=thesis_data,
            user_id=user_id,
        )

    @staticmethod
    def get_thesis(
        db: Session,
        holding_id: int,
        user_id: int,
    ) -> InvestmentThesis:
        thesis = InvestmentThesisRepository.get_by_holding_id(
            db=db,
            holding_id=holding_id,
            user_id=user_id,
        )

        if thesis is None:
            raise ValueError(
                "No investment thesis was found for this holding."
            )

        return thesis

    @staticmethod
    def update_thesis(
        db: Session,
        holding_id: int,
        thesis_data: InvestmentThesisUpdate,
        user_id: int,
    ) -> InvestmentThesis:
        thesis = InvestmentThesisRepository.get_by_holding_id(
            db=db,
            holding_id=holding_id,
            user_id=user_id,
        )

        if thesis is None:
            raise ValueError(
                "No investment thesis was found for this holding."
            )

        update_data = thesis_data.model_dump(
            exclude_unset=True,
        )

        if not update_data:
            raise ValueError(
                "At least one field must be provided for the update."
            )

        return InvestmentThesisRepository.update(
            db=db,
            thesis=thesis,
            thesis_data=thesis_data,
        )

    @staticmethod
    def delete_thesis(
        db: Session,
        holding_id: int,
        user_id: int,
    ) -> None:
        thesis = InvestmentThesisRepository.get_by_holding_id(
            db=db,
            holding_id=holding_id,
            user_id=user_id,
        )

        if thesis is None:
            raise ValueError(
                "No investment thesis was found for this holding."
            )

        InvestmentThesisRepository.delete(
            db=db,
            thesis=thesis,
        )