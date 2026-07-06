from fastapi import APIRouter
from app.services.portfolio_service import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)

@router.get("/")
def get_portfolio():

    return PortfolioService.calculate()