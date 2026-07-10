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

    if not result.get("error") and result.get("count", 0) > 0:
        NewsRepository.create_search_log(
            db=db,
            symbol=result["symbol"],
            result_count=result["count"]
        )

    return result
    
@router.get("/recent")
def get_recent_news_searches(
    db: Session = Depends(get_db)
):
    searches = NewsRepository.get_recent_searches(db)

    return {
        "count": len(searches),
        "searches": [
            {
                "id": item.id,
                "symbol": item.symbol,
                "result_count": item.result_count,
                "searched_at": item.searched_at
            }
            for item in searches
        ]
    }