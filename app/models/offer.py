from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    negotiation_id = Column(Integer, ForeignKey("negotiations.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    price = Column(Float, nullable=False)
    terms = Column(String)
    created_at = Column(DateTime, server_default=func.now())
