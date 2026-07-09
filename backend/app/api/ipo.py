from fastapi import APIRouter

from app.services.ipo_service import IPOService

router = APIRouter(
    prefix="/ipo",
    tags=["IPO"]
)


@router.get("/search/{company_name}")
def search_ipo(company_name: str):
    return IPOService.search_ipo(company_name)