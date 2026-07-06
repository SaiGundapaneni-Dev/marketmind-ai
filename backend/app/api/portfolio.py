from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.portfolio_schema import (
    HoldingCreate,
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