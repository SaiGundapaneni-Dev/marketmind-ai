from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.ai_coach import router as ai_coach_router
from app.api.auth import router as auth_router
from app.api.copilot import router as copilot_router
from app.api.investment_goal import router as investment_goal_router
from app.api.investment_review import router as investment_review_router
from app.api.investment_thesis import router as investment_thesis_router
from app.api.ipo import router as ipo_router
from app.api.news import router as news_router
from app.api.portfolio import router as portfolio_router
from app.api.scenario_simulator import router as scenario_simulator_router
from app.api.sec import router as sec_router
from app.api.stocks import router as stocks_router
from app.api.watchlist import router as watchlist_router
from app.api.watchtower import router as watchtower_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import global_exception_handler
from app.core.logger import setup_logger


logger = setup_logger()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in [
    auth_router,
    ai_coach_router,
    news_router,
    stocks_router,
    ipo_router,
    sec_router,
    scenario_simulator_router,
    copilot_router,
    portfolio_router,
    watchlist_router,
    watchtower_router,
    investment_thesis_router,
    investment_review_router,
    investment_goal_router,
]:
    app.include_router(router)

app.add_exception_handler(Exception, global_exception_handler)


@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health/database", tags=["Health"])
def database_health_check(response: Response):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }
    except SQLAlchemyError:
        logger.exception("Database health check failed.")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "database": "unavailable",
        }
