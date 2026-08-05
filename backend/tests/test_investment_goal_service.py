from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import patch

from app.services.investment_goal_service import InvestmentGoalService


def make_goal(target_amount=10000, current_amount=4000, monthly_contribution=500, target_date=date(2027, 8, 4)):
    return SimpleNamespace(
        id=1, user_id=7, name="House Down Payment", category="house",
        target_amount=target_amount, current_amount=current_amount,
        monthly_contribution=monthly_contribution, target_date=target_date,
        priority="high", notes=None, created_at=datetime(2026, 8, 4),
        updated_at=datetime(2026, 8, 4),
    )


def test_goal_progress_on_track():
    result = InvestmentGoalService._progress(make_goal(), today=date(2026, 8, 4))
    assert result["progress_percent"] == 40
    assert result["remaining_amount"] == 6000
    assert result["status"] == "on_track"
    assert result["required_monthly_contribution"] == 500


def test_goal_progress_off_track():
    goal = make_goal(target_amount=12000, current_amount=2000, monthly_contribution=200)
    result = InvestmentGoalService._progress(goal, today=date(2026, 8, 4))
    assert result["status"] == "off_track"
    assert result["contribution_gap"] > 600


@patch("app.services.investment_goal_service.InvestmentGoalRepository.list_goals")
def test_goal_summary(mock_list):
    mock_list.return_value = [make_goal(), make_goal(target_amount=5000, current_amount=5000, monthly_contribution=0)]
    result = InvestmentGoalService.list_goals(db=object(), user_id=7)
    assert result["total_goals"] == 2
    assert result["completed_goals"] == 1
    assert result["total_target_amount"] == 15000
