from pydantic import BaseModel
from datetime import datetime


class NegotiationCreate(BaseModel):
    title: str
    raw_requirements: str
    system_prompt: str | None = None


class NegotiationResponse(BaseModel):
    id: int
    title: str
    system_prompt: str | None = None
    target_price: float | None = None
    max_budget: float | None = None
    buyer_budget: float | None = None
    round_number: int = 0
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True
