from fastapi import FastAPI
from app.api.investment_thesis import router as investment_thesis_router
from app.api.investment_review import router as investment_review_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.ai_coach import router as ai_coach_router
from app.api.auth import router as auth_router
from app.api.copilot import router as copilot_router
from app.api.ipo import router as ipo_router
from app.api.news import router as news_router
from app.api.portfolio import router as portfolio_router
from app.api.scenario_simulator import router as scenario_simulator_router
from app.api.sec import router as sec_router
from app.api.stocks import router as stocks_router
from app.api.watchlist import router as watchlist_router
from app.api.watchtower import router as watchtower_router
from app.core.config import settings
from app.core.exceptions import global_exception_handler
from app.core.logger import setup_logger


logger = setup_logger()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ai_coach_router)
app.include_router(news_router)
app.include_router(stocks_router)
app.include_router(ipo_router)
app.include_router(sec_router)
app.include_router(scenario_simulator_router)
app.include_router(copilot_router)
app.include_router(portfolio_router)
app.include_router(watchlist_router)
app.include_router(watchtower_router)
app.include_router(investment_thesis_router)
app.include_router(investment_review_router)

app.add_exception_handler(Exception, global_exception_handler)


@app.get("/")
def home():
    logger.info("Root endpoint called")

    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
    }
