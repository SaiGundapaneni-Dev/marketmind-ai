from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=True,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    portfolios = relationship(
        "Portfolio",
        back_populates="user",
    )

    watchlist_items = relationship(
        "WatchlistItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    snapshots = relationship(
        "PortfolioSnapshot",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="holdings")


class NewsSearch(Base):
    __tablename__ = "news_searches"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, unique=True, index=True)
    result_count = Column(Integer, nullable=False, default=0)
    searched_at = Column(DateTime, default=datetime.utcnow)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "symbol",
            name="uq_watchlist_user_symbol",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    symbol = Column(String, nullable=False, index=True)
    company_name = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="watchlist_items")
