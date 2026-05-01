from pydantic import BaseModel
from datetime import datetime


class NegotiationCreate(BaseModel):
    title: str
    system_prompt: str | None = None
    target_price: float | None = None
    max_budget: float | None = None


class NegotiationResponse(BaseModel):
    id: int
    title: str
    system_prompt: str | None = None
    target_price: float | None = None
    max_budget: float | None = None
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True
