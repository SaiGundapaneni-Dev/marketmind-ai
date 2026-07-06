from app.core.database import SessionLocal
from app.models import User, Portfolio, Holding


db = SessionLocal()

try:
    user = User(name="Sai", email="sai@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    portfolio = Portfolio(name="Sai Main Portfolio", user_id=user.id)
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    holdings = [
        Holding(
            asset_type="US",
            symbol="NVDA",
            name="NVIDIA",
            quantity=2,
            average_price=145,
            currency="USD",
            portfolio_id=portfolio.id,
        ),
        Holding(
            asset_type="US",
            symbol="PLTR",
            name="Palantir",
            quantity=2,
            average_price=35,
            currency="USD",
            portfolio_id=portfolio.id,
        ),
        Holding(
            asset_type="India",
            symbol="TRENT.NS",
            name="Trent",
            quantity=5,
            average_price=2780,
            currency="INR",
            portfolio_id=portfolio.id,
        ),
    ]

    db.add_all(holdings)
    db.commit()

    print("Seed data inserted successfully")

finally:
    db.close()