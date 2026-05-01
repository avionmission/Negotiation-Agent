from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    negotiation_id: int
    supplier_id: int
    sender: str
    content: str


class MessageResponse(BaseModel):
    id: int
    negotiation_id: int
    supplier_id: int
    sender: str
    content: str
    timestamp: datetime | None = None

    class Config:
        from_attributes = True
