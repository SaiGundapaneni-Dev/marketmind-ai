from fastapi import APIRouter

router = APIRouter(
    prefix="/ipo",
    tags=["IPO"]
)


@router.get("/search/{company_name}")
def search_ipo(company_name: str):
    return {
        "company_name": company_name,
        "message": "IPO analyzer endpoint working"
    }