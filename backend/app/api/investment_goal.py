from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.investment_goal_schema import GoalProgressResponse, GoalSummaryResponse, InvestmentGoalCreate, InvestmentGoalUpdate
from app.services.investment_goal_service import InvestmentGoalService

router = APIRouter(prefix="/goals", tags=["Goal-Based Investing"])


@router.get("", response_model=GoalSummaryResponse)
def list_goals(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return InvestmentGoalService.list_goals(db, current_user.id)


@router.get("/{goal_id}", response_model=GoalProgressResponse)
def get_goal(goal_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return InvestmentGoalService.get_goal(db, current_user.id, goal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=GoalProgressResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: InvestmentGoalCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return InvestmentGoalService.create_goal(db, current_user.id, payload)


@router.put("/{goal_id}", response_model=GoalProgressResponse)
def update_goal(goal_id: int, payload: InvestmentGoalUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return InvestmentGoalService.update_goal(db, current_user.id, goal_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        InvestmentGoalService.delete_goal(db, current_user.id, goal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
