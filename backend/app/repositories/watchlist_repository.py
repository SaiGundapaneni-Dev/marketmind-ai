from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import WatchlistItem


class WatchlistRepository:

    @staticmethod
    def list_items(
        db: Session,
        user_id: int,
    ):
        return (
            db.query(WatchlistItem)
            .filter(WatchlistItem.user_id == user_id)
            .order_by(WatchlistItem.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
        item_id: int,
    ):
        return (
            db.query(WatchlistItem)
            .filter(
                WatchlistItem.id == item_id,
                WatchlistItem.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        data,
    ):
        item = WatchlistItem(
            user_id=user_id,
            symbol=data.symbol.strip().upper(),
            company_name=(
                data.company_name.strip()
                if data.company_name
                else None
            ),
            notes=data.notes.strip() if data.notes else None,
        )

        db.add(item)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None

        db.refresh(item)
        return item

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        item_id: int,
        data,
    ):
        item = WatchlistRepository.get_by_id(
            db,
            user_id,
            item_id,
        )

        if item is None:
            return None

        if data.company_name is not None:
            item.company_name = data.company_name.strip() or None

        if data.notes is not None:
            item.notes = data.notes.strip() or None

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(
        db: Session,
        user_id: int,
        item_id: int,
    ):
        item = WatchlistRepository.get_by_id(
            db,
            user_id,
            item_id,
        )

        if item is None:
            return None

        db.delete(item)
        db.commit()
        return item
