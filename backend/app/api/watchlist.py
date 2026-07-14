from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.watchlist_schema import (
    WatchlistCreate,
    WatchlistItemResponse,
    WatchlistSummaryResponse,
    WatchlistUpdate,
)
from app.services.watchlist_service import WatchlistService


router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("/", response_model=list[WatchlistItemResponse])
def list_watchlist(
    user_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return WatchlistService.list_items(db, user_id)


@router.post(
    "/",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_watchlist_item(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
):
    item = WatchlistService.create_item(db, payload)

    if item is None:
        raise HTTPException(
            status_code=409,
            detail="This symbol is already in the watchlist.",
        )

    return item


@router.put("/{item_id}", response_model=WatchlistItemResponse)
def update_watchlist_item(
    item_id: int,
    payload: WatchlistUpdate,
    db: Session = Depends(get_db),
):
    item = WatchlistService.update_item(db, item_id, payload)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist item not found.",
        )

    return item


@router.delete("/{item_id}")
def delete_watchlist_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = WatchlistService.delete_item(db, item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist item not found.",
        )

    return {
        "message": "Watchlist item deleted successfully.",
        "item_id": item_id,
    }


@router.get("/analysis", response_model=WatchlistSummaryResponse)
def analyze_watchlist(
    user_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return WatchlistService.analyze_watchlist(db, user_id)
