from sqlalchemy.orm import Session

from app.models import NewsSearch


class NewsRepository:

    @staticmethod
    def create_search_log(
        db: Session,
        symbol: str,
        result_count: int
    ):
        search_log = NewsSearch(
            symbol=symbol.upper(),
            result_count=result_count
        )

        db.add(search_log)
        db.commit()
        db.refresh(search_log)

        return search_log