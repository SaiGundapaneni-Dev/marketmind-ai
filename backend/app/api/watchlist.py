from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return WatchlistService.list_items(db, current_user.id)


@router.post(
    "/",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_watchlist_item(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = WatchlistService.create_item(
        db, current_user.id, payload
    )
    if item is None:
        raise HTTPException(
            status_code=409,
            detail="This symbol is already in your watchlist.",
        )
    return item


@router.put("/{item_id}", response_model=WatchlistItemResponse)
def update_watchlist_item(
    item_id: int,
    payload: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = WatchlistService.update_item(
        db, current_user.id, item_id, payload
    )
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
    current_user=Depends(get_current_user),
):
    item = WatchlistService.delete_item(
        db, current_user.id, item_id
    )
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return WatchlistService.analyze_watchlist(
        db, current_user.id
    )
