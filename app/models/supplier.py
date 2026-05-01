from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_info = Column(String)
    category = Column(String)
    rating = Column(Float)

    negotiations = relationship("Negotiation", secondary="negotiation_suppliers", back_populates="suppliers")
