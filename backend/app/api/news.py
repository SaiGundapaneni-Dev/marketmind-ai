from fastapi import APIRouter

router = APIRouter(
    prefix="/news",
    tags=["News"]
)


@router.get("/search/{symbol}")
def search_news(symbol: str):
    return {
        "symbol": symbol.upper(),
        "message": "News search endpoint working"
    }