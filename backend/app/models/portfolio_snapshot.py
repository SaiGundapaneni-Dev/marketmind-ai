from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        Integer,
        ForeignKey("portfolios.id"),
        nullable=False,
        index=True,
    )
    total_cost = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    total_profit = Column(Float, nullable=False)
    total_return_percent = Column(Float, nullable=False)
    health_score = Column(Float, nullable=False)
    holdings_count = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    portfolio = relationship("Portfolio", back_populates="snapshots")
