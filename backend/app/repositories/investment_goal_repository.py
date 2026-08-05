from sqlalchemy.orm import Session

from app.models.investment_goal import InvestmentGoal


class InvestmentGoalRepository:
    @staticmethod
    def list_goals(db: Session, user_id: int):
        return (
            db.query(InvestmentGoal)
            .filter(InvestmentGoal.user_id == user_id)
            .order_by(InvestmentGoal.target_date.asc())
            .all()
        )

    @staticmethod
    def get_goal(db: Session, user_id: int, goal_id: int):
        return (
            db.query(InvestmentGoal)
            .filter(InvestmentGoal.id == goal_id, InvestmentGoal.user_id == user_id)
            .first()
        )

    @staticmethod
    def create_goal(db: Session, user_id: int, data):
        goal = InvestmentGoal(
            user_id=user_id,
            name=data.name.strip(),
            category=data.category,
            target_amount=data.target_amount,
            current_amount=data.current_amount,
            monthly_contribution=data.monthly_contribution,
            target_date=data.target_date,
            priority=data.priority,
            notes=data.notes.strip() if data.notes else None,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update_goal(db: Session, goal: InvestmentGoal, data):
        values = data.model_dump(exclude_unset=True)
        for field, value in values.items():
            if field in {"name", "notes"} and isinstance(value, str):
                value = value.strip()
            setattr(goal, field, value)
        if goal.current_amount > goal.target_amount:
            goal.current_amount = goal.target_amount
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(db: Session, goal: InvestmentGoal):
        db.delete(goal)
        db.commit()
