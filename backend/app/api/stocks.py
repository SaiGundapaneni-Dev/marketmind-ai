from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
):
    return StockAnalysisService.analyze(symbol, db)
