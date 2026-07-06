from fastapi import FastAPI
from app.api.portfolio import router as portfolio_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.include_router(portfolio_router)


@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.app_name} 🚀",
        "environment": settings.environment
    }