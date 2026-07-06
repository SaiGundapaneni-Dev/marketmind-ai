from fastapi import APIRouter
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio_schema import PortfolioResponse

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


@router.get("/", response_model=PortfolioResponse)
def get_portfolio():
    return PortfolioService.calculate()