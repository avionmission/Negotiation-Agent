from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Negotiation(Base):
    __tablename__ = "negotiations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    system_prompt = Column(String)
    target_price = Column(Float)
    max_budget = Column(Float)
    status = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())
