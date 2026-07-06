from fastapi import FastAPI
from backend.services.portfolio_service import calculate_portfolio

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Portfolio AI running"}

@app.get("/portfolio")
def portfolio():
    return calculate_portfolio()