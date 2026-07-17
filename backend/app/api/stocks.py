from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.services.stock_analysis_service import StockAnalysisService
from app.services.stock_service import StockService


router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
)


@router.get("/search/{symbol}")
def search_stock(symbol: str):
    return StockService.search_stock(symbol)


@router.get("/analyze/{symbol}")
def analyze_stock(
    symbol: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return StockAnalysisService.analyze(
        symbol=symbol,
        db=db,
        user_id=current_user.id,
    )
