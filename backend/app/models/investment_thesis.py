from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvestmentThesis(Base):
    __tablename__ = "investment_theses"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    holding_id = Column(
        Integer,
        ForeignKey("holdings.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    thesis = Column(
        Text,
        nullable=False,
    )

    target_price = Column(
        Float,
        nullable=True,
    )

    investment_horizon = Column(
        String(50),
        nullable=True,
    )

    conviction_score = Column(
        Integer,
        nullable=True,
    )

    risk_level = Column(
        String(30),
        nullable=True,
    )

    buy_reasons = Column(
        Text,
        nullable=True,
    )

    sell_conditions = Column(
        Text,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    review_date = Column(
        Date,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    holding = relationship(
        "Holding",
        back_populates="investment_thesis",
    )