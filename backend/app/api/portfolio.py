from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.portfolio_schema import PortfolioResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


@router.get("/", response_model=PortfolioResponse)
def get_portfolio(db: Session = Depends(get_db)):
    return PortfolioService.calculate(db)