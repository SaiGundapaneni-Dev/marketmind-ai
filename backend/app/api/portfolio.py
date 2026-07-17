from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.portfolio_history_schema import (
    PortfolioChangesResponse,
    PortfolioContributorsResponse,
    PortfolioPerformanceResponse,
    PortfolioSnapshotResponse,
)
from app.schemas.portfolio_intelligence_schema import PortfolioIntelligenceResponse
from app.schemas.portfolio_schema import HoldingCreate, HoldingUpdate, PortfolioResponse
from app.services.portfolio_history_service import PortfolioHistoryService
from app.services.portfolio_intelligence_service import PortfolioIntelligenceService
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("/", response_model=PortfolioResponse)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioService.calculate(db, current_user.id)


@router.post("/holdings", status_code=status.HTTP_201_CREATED)
def create_holding(
    holding: HoldingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_holding = PortfolioService.create_holding(
        db, current_user.id, holding
    )
    return {
        "message": "Holding created successfully",
        "holding_id": new_holding.id,
        "symbol": new_holding.symbol,
    }


@router.get("/holdings/{holding_id}")
def get_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    holding = PortfolioService.get_holding_by_id(
        db, current_user.id, holding_id
    )
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding


@router.put("/holdings/{holding_id}")
def update_holding(
    holding_id: int,
    holding: HoldingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_holding = PortfolioService.update_holding(
        db, current_user.id, holding_id, holding
    )
    if updated_holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {
        "message": "Holding updated successfully",
        "holding_id": updated_holding.id,
        "symbol": updated_holding.symbol,
    }


@router.delete("/holdings/{holding_id}", status_code=status.HTTP_200_OK)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted_holding = PortfolioService.delete_holding(
        db, current_user.id, holding_id
    )
    if deleted_holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {
        "message": "Holding deleted successfully",
        "holding_id": holding_id,
    }


@router.post("/snapshot", response_model=PortfolioSnapshotResponse)
def create_portfolio_snapshot(
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.create_daily_snapshot(
        db, current_user.id, force=force
    )


@router.get("/history", response_model=list[PortfolioSnapshotResponse])
def get_portfolio_history(
    limit: int = Query(default=365, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_history(
        db, current_user.id, limit
    )


@router.get("/performance", response_model=PortfolioPerformanceResponse)
def get_portfolio_performance(
    limit: int = Query(default=365, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_performance(
        db, current_user.id, limit
    )


@router.get("/contributors", response_model=PortfolioContributorsResponse)
def get_portfolio_contributors(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_contributors(
        db, current_user.id
    )


@router.get("/changes", response_model=PortfolioChangesResponse)
def get_portfolio_changes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioHistoryService.get_changes(
        db, current_user.id
    )


@router.get(
    "/intelligence",
    response_model=PortfolioIntelligenceResponse,
)
def get_portfolio_intelligence(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PortfolioIntelligenceService.generate(
        db,
        current_user.id,
    )
