import uuid
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import ForeignKey, String, Text, DateTime, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AgentStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NEGOTIATING = "NEGOTIATING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class SupplierStatus(str, Enum):
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    WON = "WON"
    LOST = "LOST"


class MessageRole(str, Enum):
    AGENT = "AGENT"
    SUPPLIER = "SUPPLIER"
    SYSTEM = "SYSTEM"


class DealStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FINALIZED = "FINALIZED"


class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    agents: Mapped[list["Agent"]] = relationship(
        "Agent", back_populates="buyer", cascade="all, delete-orphan"
    )


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    buyer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("buyers.id"), index=True
    )

    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(100))
    subdomain: Mapped[str | None] = mapped_column(String(100), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    base_price: Mapped[float] = mapped_column(Float, default=0.0)
    min_price: Mapped[float] = mapped_column(Float, default=0.0)
    budget: Mapped[float] = mapped_column(Float, default=0.0)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    knowledge_base: Mapped[str | None] = mapped_column(Text, default=None)

    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(AgentStatus), default=AgentStatus.DRAFT
    )

    max_negotiation_rounds: Mapped[int] = mapped_column(default=3)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="agents")
    suppliers: Mapped[list["Supplier"]] = relationship(
        "Supplier", back_populates="agent", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="agent", cascade="all, delete-orphan"
    )
    deal_summaries: Mapped[list["DealSummary"]] = relationship(
        "DealSummary", back_populates="agent", cascade="all, delete-orphan"
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id"), index=True
    )

    email: Mapped[str] = mapped_column(String(255), index=True)
    company_name: Mapped[str | None] = mapped_column(String(255), default=None)

    access_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    status: Mapped[SupplierStatus] = mapped_column(
        SQLEnum(SupplierStatus), default=SupplierStatus.INVITED
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="suppliers")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="supplier", cascade="all, delete-orphan"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id"), index=True
    )
    supplier_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("suppliers.id"), index=True
    )

    negotiation_round: Mapped[int] = mapped_column(default=0)
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="conversations")
    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="conversations"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), index=True
    )

    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole))
    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )


class DealSummary(Base):
    __tablename__ = "deal_summaries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id"), index=True
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=True
    )

    final_price: Mapped[float] = mapped_column(Float, default=0.0)
    terms: Mapped[str | None] = mapped_column(Text, default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    status: Mapped[DealStatus] = mapped_column(
        SQLEnum(DealStatus), default=DealStatus.PENDING
    )

    is_auto_generated: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="deal_summaries")
