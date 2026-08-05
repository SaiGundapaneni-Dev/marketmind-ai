from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvestmentGoal(Base):
    __tablename__ = "investment_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(50), nullable=False, default="custom", server_default="custom")
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False, default=0, server_default="0")
    monthly_contribution = Column(Float, nullable=False, default=0, server_default="0")
    target_date = Column(Date, nullable=False)
    priority = Column(String(20), nullable=False, default="medium", server_default="medium")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="investment_goals")
