from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models.models import (
    AgentStatus,
    ConversationStatus,
    SupplierStatus,
    MessageRole,
    DealStatus,
)


class BuyerBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)


class BuyerCreate(BuyerBase):
    pass


class BuyerResponse(BuyerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    domain: str = Field(min_length=1, max_length=100)
    subdomain: str | None = None
    description: str | None = None
    base_price: float = Field(ge=0)
    min_price: float = Field(ge=0)
    budget: float = Field(ge=0)
    deadline: datetime | None = None
    knowledge_base: str | None = None
    max_negotiation_rounds: int = Field(default=3, ge=1, le=10)


class AgentCreate(AgentBase):
    buyer_id: str


class AgentUpdate(BaseModel):
    name: str | None = None
    domain: str | None = None
    subdomain: str | None = None
    description: str | None = None
    base_price: float | None = None
    min_price: float | None = None
    budget: float | None = None
    deadline: datetime | None = None
    knowledge_base: str | None = None
    max_negotiation_rounds: int | None = None
    status: AgentStatus | None = None


class AgentResponse(AgentBase):
    id: str
    buyer_id: str
    status: AgentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplierBase(BaseModel):
    email: EmailStr
    company_name: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: str
    agent_id: str
    access_token: str
    status: SupplierStatus
    token_expiry: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    content: str = Field(min_length=1)


class MessageCreate(MessageBase):
    role: MessageRole


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    role: MessageRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    pass


class ConversationCreate(ConversationBase):
    agent_id: str
    supplier_id: str


class ConversationResponse(BaseModel):
    id: str
    agent_id: str
    supplier_id: str
    negotiation_round: int
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationWithMessages(ConversationResponse):
    messages: list[MessageResponse] = []


class ConversationDetail(ConversationResponse):
    supplier_status: SupplierStatus
    max_rounds: int
    is_final: bool

    model_config = ConfigDict(from_attributes=True)


class DealSummaryBase(BaseModel):
    final_price: float = Field(ge=0)
    terms: str | None = None
    notes: str | None = None


class DealSummaryCreate(DealSummaryBase):
    agent_id: str
    conversation_id: str | None = None


class DealSummaryUpdate(BaseModel):
    status: DealStatus | None = None


class DealSummaryResponse(DealSummaryBase):
    id: str
    agent_id: str
    conversation_id: str | None
    status: DealStatus
    is_auto_generated: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    token: str


class ChatResponse(BaseModel):
    response: str
    negotiation_round: int
    is_final: bool = False
    status: ConversationStatus
    summary_id: str | None = None
