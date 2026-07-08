from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.news_repository import NewsRepository
from app.services.news_service import NewsService

router = APIRouter(
    prefix="/news",
    tags=["News"]
)


@router.get("/search/{symbol}")
def search_news(
    symbol: str,
    db: Session = Depends(get_db)
):
    result = NewsService.search_news(symbol)

    NewsRepository.create_search_log(
        db=db,
        symbol=result["symbol"],
        result_count=result["count"]
    )

    return result