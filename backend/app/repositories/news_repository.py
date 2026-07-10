from sqlalchemy.orm import Session
from datetime import datetime
from app.models import NewsSearch


class NewsRepository:
    
    @staticmethod
    def get_recent_searches(db: Session, limit: int = 5):
        return (
            db.query(NewsSearch)
            .order_by(NewsSearch.searched_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_search_log(
        db: Session,
        symbol: str,
        result_count: int
    ):
        clean_symbol = symbol.upper()

        existing_search = (
            db.query(NewsSearch)
            .filter(NewsSearch.symbol == clean_symbol)
            .first()
        )

        if existing_search:
            existing_search.result_count = result_count
            existing_search.searched_at = datetime.utcnow()

            db.commit()
            db.refresh(existing_search)

            return existing_search

        search_log = NewsSearch(
            symbol=clean_symbol,
            result_count=result_count
        )

        db.add(search_log)
        db.commit()
        db.refresh(search_log)

        return search_log