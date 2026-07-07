from fastapi import APIRouter

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)


@router.get("/search/{symbol}")
def search_stock(symbol: str):
    return {
        "symbol": symbol.upper(),
        "message": "Stock search endpoint working"
    }