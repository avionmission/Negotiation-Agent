from pydantic import BaseModel
from datetime import datetime


class OfferCreate(BaseModel):
    negotiation_id: int
    supplier_id: int
    price: float
    terms: str | None = None


class OfferResponse(BaseModel):
    id: int
    negotiation_id: int
    supplier_id: int
    price: float
    terms: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
