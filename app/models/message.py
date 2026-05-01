from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    negotiation_id = Column(Integer, ForeignKey("negotiations.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    sender = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
