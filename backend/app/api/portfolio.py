from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from app.core.database import get_db
from app.schemas.portfolio_schema import (
    HoldingCreate,
    HoldingUpdate,
    PortfolioResponse
)
from app.services.portfolio_service import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


@router.get("/", response_model=PortfolioResponse)
def get_portfolio(db: Session = Depends(get_db)):
    return PortfolioService.calculate(db)
    
@router.post(
    "/holdings",
    status_code=status.HTTP_201_CREATED
)
def create_holding(
    holding: HoldingCreate,
    db: Session = Depends(get_db)
):
    new_holding = PortfolioService.create_holding(
        db,
        holding
    )

    return {
        "message": "Holding created successfully",
        "holding_id": new_holding.id,
        "symbol": new_holding.symbol
    }
   
@router.delete(
    "/holdings/{holding_id}",
    status_code=status.HTTP_200_OK
)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db)
):
    deleted_holding = PortfolioService.delete_holding(db, holding_id)

    if deleted_holding is None:
        raise HTTPException(
            status_code=404,
            detail="Holding not found"
        )

    return {
        "message": "Holding deleted successfully",
        "holding_id": holding_id
    }
    
@router.get("/holdings/{holding_id}")
def get_holding(
    holding_id: int,
    db: Session = Depends(get_db)
):
    holding = PortfolioService.get_holding_by_id(db, holding_id)

    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")

    return holding
    
    
@router.put("/holdings/{holding_id}")
def update_holding(
    holding_id: int,
    holding: HoldingUpdate,
    db: Session = Depends(get_db)
):
    updated_holding = PortfolioService.update_holding(
        db,
        holding_id,
        holding
    )

    if updated_holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")

    return {
        "message": "Holding updated successfully",
        "holding_id": updated_holding.id,
        "symbol": updated_holding.symbol
    }