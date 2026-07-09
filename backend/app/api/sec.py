from fastapi import APIRouter

from app.services.sec_service import SECService


router = APIRouter(
    prefix="/ipo",
    tags=["IPO"],
)


@router.get("/sec-search/{company_name}")
def search_sec_company(company_name: str):
    return SECService.search_company(company_name)


@router.get("/sec-filings/{cik}")
def get_sec_company_filings(cik: str):
    return SECService.get_company_filings(cik)
    
@router.get("/sec-ipo-filings/{cik}")
def get_sec_ipo_filings(cik: str):
    return SECService.get_ipo_filings(cik)