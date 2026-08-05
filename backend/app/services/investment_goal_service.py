from datetime import date
from math import ceil

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.repositories.investment_goal_repository import InvestmentGoalRepository


class InvestmentGoalService:
    @staticmethod
    def _months_between(start: date, end: date) -> int:
        if end <= start:
            return 0
        months = (end.year - start.year) * 12 + end.month - start.month
        if end.day > start.day:
            months += 1
        return max(months, 0)

    @staticmethod
    def _progress(goal, today: date | None = None) -> dict:
        current_date = today or date.today()
        target = float(goal.target_amount or 0)
        current = float(goal.current_amount or 0)
        monthly = float(goal.monthly_contribution or 0)
        remaining = max(target - current, 0)
        progress_percent = 100 if target <= 0 else min(current / target * 100, 100)
        months_remaining = InvestmentGoalService._months_between(current_date, goal.target_date)
        required_monthly = remaining / months_remaining if remaining > 0 and months_remaining > 0 else 0
        contribution_gap = max(required_monthly - monthly, 0)

        projected_completion = None
        if remaining <= 0:
            projected_completion = current_date
        elif monthly > 0:
            projected_completion = current_date + relativedelta(months=ceil(remaining / monthly))

        if remaining <= 0:
            status = "completed"
            health_score = 100
            coach_message = "Goal completed. Preserve the funds or create the next goal."
        elif months_remaining <= 0:
            status = "off_track"
            health_score = 20
            coach_message = "The target date has passed. Increase funding or revise the date."
        elif monthly >= required_monthly:
            status = "on_track"
            health_score = min(100, 80 + progress_percent * 0.2)
            coach_message = "You are on track. Continue the current monthly contribution."
        elif monthly >= required_monthly * 0.8:
            status = "slightly_behind"
            health_score = 65
            coach_message = f"You are slightly behind. Increase monthly contributions by ${contribution_gap:,.2f}."
        else:
            status = "off_track"
            health_score = 40
            coach_message = f"The goal is off track. Increase monthly contributions by ${contribution_gap:,.2f} or extend the target date."

        return {
            "remaining_amount": round(remaining, 2),
            "progress_percent": round(progress_percent, 2),
            "months_remaining": months_remaining,
            "projected_completion_date": projected_completion,
            "required_monthly_contribution": round(required_monthly, 2),
            "contribution_gap": round(contribution_gap, 2),
            "health_score": round(health_score, 2),
            "status": status,
            "coach_message": coach_message,
        }

    @staticmethod
    def _serialize(goal, today: date | None = None) -> dict:
        data = {
            "id": goal.id,
            "user_id": goal.user_id,
            "name": goal.name,
            "category": goal.category,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "monthly_contribution": goal.monthly_contribution,
            "target_date": goal.target_date,
            "priority": goal.priority,
            "notes": goal.notes,
            "created_at": goal.created_at,
            "updated_at": goal.updated_at,
        }
        data.update(InvestmentGoalService._progress(goal, today=today))
        return data

    @staticmethod
    def list_goals(db: Session, user_id: int) -> dict:
        goals = InvestmentGoalRepository.list_goals(db, user_id)
        items = [InvestmentGoalService._serialize(goal) for goal in goals]
        total_target = sum(float(item["target_amount"]) for item in items)
        total_current = sum(float(item["current_amount"]) for item in items)
        return {
            "total_goals": len(items),
            "completed_goals": sum(item["status"] == "completed" for item in items),
            "on_track_goals": sum(item["status"] == "on_track" for item in items),
            "behind_goals": sum(item["status"] in {"slightly_behind", "off_track"} for item in items),
            "total_target_amount": round(total_target, 2),
            "total_current_amount": round(total_current, 2),
            "overall_progress_percent": round(total_current / total_target * 100, 2) if total_target else 0,
            "goals": items,
        }

    @staticmethod
    def get_goal(db: Session, user_id: int, goal_id: int) -> dict:
        goal = InvestmentGoalRepository.get_goal(db, user_id, goal_id)
        if goal is None:
            raise ValueError("The selected investment goal was not found.")
        return InvestmentGoalService._serialize(goal)

    @staticmethod
    def create_goal(db: Session, user_id: int, data) -> dict:
        return InvestmentGoalService._serialize(InvestmentGoalRepository.create_goal(db, user_id, data))

    @staticmethod
    def update_goal(db: Session, user_id: int, goal_id: int, data) -> dict:
        goal = InvestmentGoalRepository.get_goal(db, user_id, goal_id)
        if goal is None:
            raise ValueError("The selected investment goal was not found.")
        return InvestmentGoalService._serialize(InvestmentGoalRepository.update_goal(db, goal, data))

    @staticmethod
    def delete_goal(db: Session, user_id: int, goal_id: int) -> None:
        goal = InvestmentGoalRepository.get_goal(db, user_id, goal_id)
        if goal is None:
            raise ValueError("The selected investment goal was not found.")
        InvestmentGoalRepository.delete_goal(db, goal)
