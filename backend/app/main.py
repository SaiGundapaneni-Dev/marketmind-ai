from fastapi import FastAPI
from app.api.portfolio import router as portfolio_router

app = FastAPI(
    title="MarketMind AI",
    version="1.0.0"
)

app.include_router(portfolio_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to MarketMind AI 🚀"
    }