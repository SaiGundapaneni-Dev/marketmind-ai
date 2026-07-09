from fastapi import APIRouter

from app.services.sec_service import SECService

router = APIRouter(
    prefix="/ipo",
    tags=["IPO"]
)


@router.get("/sec-search/{company_name}")
def search_sec_company(company_name: str):
    return SECService.search_company(company_name)