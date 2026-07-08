from fastapi import APIRouter

from app.services.news_service import NewsService

router = APIRouter(
    prefix="/news",
    tags=["News"]
)


@router.get("/search/{symbol}")
def search_news(symbol: str):
    return NewsService.search_news(symbol)