from fastapi import APIRouter
from app.services.stock_service import StockService

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)


@router.get("/search/{symbol}")
def search_stock(symbol: str):
    return StockService.search_stock(symbol)