from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.portfolio_history_schema import (
    PortfolioChangesResponse,
    PortfolioContributorsResponse,
    PortfolioPerformanceResponse,
    PortfolioSnapshotResponse,
)
from app.schemas.portfolio_schema import (
    HoldingCreate,
    HoldingUpdate,
    PortfolioResponse,
)
from app.services.portfolio_history_service import PortfolioHistoryService
from app.services.portfolio_service import PortfolioService


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get("/", response_model=PortfolioResponse)
def get_portfolio(db: Session = Depends(get_db)):
    return PortfolioService.calculate(db)


@router.post(
    "/holdings",
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    holding: HoldingCreate,
    db: Session = Depends(get_db),
):
    new_holding = PortfolioService.create_holding(db, holding)

    return {
        "message": "Holding created successfully",
        "holding_id": new_holding.id,
        "symbol": new_holding.symbol,
    }


@router.delete(
    "/holdings/{holding_id}",
    status_code=status.HTTP_200_OK,
)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
):
    deleted_holding = PortfolioService.delete_holding(db, holding_id)

    if deleted_holding is None:
        raise HTTPException(
            status_code=404,
            detail="Holding not found",
        )

    return {
        "message": "Holding deleted successfully",
        "holding_id": holding_id,
    }


@router.get("/holdings/{holding_id}")
def get_holding(
    holding_id: int,
    db: Session = Depends(get_db),
):
    holding = PortfolioService.get_holding_by_id(db, holding_id)

    if holding is None:
        raise HTTPException(
            status_code=404,
            detail="Holding not found",
        )

    return holding


@router.put("/holdings/{holding_id}")
def update_holding(
    holding_id: int,
    holding: HoldingUpdate,
    db: Session = Depends(get_db),
):
    updated_holding = PortfolioService.update_holding(
        db,
        holding_id,
        holding,
    )

    if updated_holding is None:
        raise HTTPException(
            status_code=404,
            detail="Holding not found",
        )

    return {
        "message": "Holding updated successfully",
        "holding_id": updated_holding.id,
        "symbol": updated_holding.symbol,
    }


@router.post(
    "/snapshot",
    response_model=PortfolioSnapshotResponse,
)
def create_portfolio_snapshot(
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return PortfolioHistoryService.create_daily_snapshot(
        db,
        force=force,
    )


@router.get(
    "/history",
    response_model=list[PortfolioSnapshotResponse],
)
def get_portfolio_history(
    limit: int = Query(default=365, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    return PortfolioHistoryService.get_history(db, limit)


@router.get(
    "/performance",
    response_model=PortfolioPerformanceResponse,
)
def get_portfolio_performance(
    limit: int = Query(default=365, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    return PortfolioHistoryService.get_performance(db, limit)


@router.get(
    "/contributors",
    response_model=PortfolioContributorsResponse,
)
def get_portfolio_contributors(
    db: Session = Depends(get_db),
):
    return PortfolioHistoryService.get_contributors(db)


@router.get(
    "/changes",
    response_model=PortfolioChangesResponse,
)
def get_portfolio_changes(
    db: Session = Depends(get_db),
):
    return PortfolioHistoryService.get_changes(db)
