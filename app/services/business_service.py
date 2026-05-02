import uuid
import secrets
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.models import (
    Buyer,
    Agent,
    Supplier,
    Conversation,
    Message,
    DealSummary,
    AgentStatus,
    ConversationStatus,
    SupplierStatus,
    MessageRole,
    DealStatus,
)
from app.schemas.schemas import (
    BuyerCreate,
    AgentCreate,
    AgentUpdate,
    SupplierCreate,
    ConversationCreate,
    MessageCreate,
    DealSummaryCreate,
    DealSummaryUpdate,
)


def create_buyer(db: Session, data: BuyerCreate) -> Buyer:
    buyer = Buyer(
        id=str(uuid.uuid4()),
        email=data.email,
        name=data.name,
    )
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def get_buyer(db: Session, buyer_id: str) -> Buyer | None:
    return db.get(Buyer, buyer_id)


def get_buyer_by_email(db: Session, email: str) -> Buyer | None:
    return db.query(Buyer).filter(Buyer.email == email).first()


def create_agent(db: Session, data: AgentCreate) -> Agent:
    agent = Agent(
        id=str(uuid.uuid4()),
        buyer_id=data.buyer_id,
        name=data.name,
        domain=data.domain,
        subdomain=data.subdomain,
        description=data.description,
        base_price=data.base_price,
        min_price=data.min_price,
        budget=data.budget,
        deadline=data.deadline,
        knowledge_base=data.knowledge_base,
        max_negotiation_rounds=data.max_negotiation_rounds,
        status=AgentStatus.DRAFT,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def get_agent(db: Session, agent_id: str) -> Agent | None:
    return db.get(Agent, agent_id)


def list_agents(db: Session, buyer_id: str | None = None) -> list[Agent]:
    query = db.query(Agent)
    if buyer_id:
        query = query.filter(Agent.buyer_id == buyer_id)
    return query.all()


def update_agent(db: Session, agent_id: str, data: AgentUpdate) -> Agent | None:
    agent = db.get(Agent, agent_id)
    if not agent:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return agent


def add_supplier(db: Session, agent_id: str, data: SupplierCreate) -> Supplier | None:
    agent = db.get(Agent, agent_id)
    if not agent:
        return None

    token = secrets.token_urlsafe(32)
    token_expiry = datetime.utcnow() + timedelta(days=7)

    supplier = Supplier(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        email=data.email,
        company_name=data.company_name,
        access_token=token,
        token_expiry=token_expiry,
        status=SupplierStatus.INVITED,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def get_supplier_by_token(db: Session, token: str) -> Supplier | None:
    return db.query(Supplier).filter(Supplier.access_token == token).first()


def get_supplier_by_id(db: Session, supplier_id: str) -> Supplier | None:
    return db.get(Supplier, supplier_id)


def get_agent_suppliers(db: Session, agent_id: str) -> list[Supplier]:
    return db.query(Supplier).filter(Supplier.agent_id == agent_id).all()


def get_conversation(db: Session, conversation_id: str) -> Conversation | None:
    return db.get(Conversation, conversation_id)


def get_supplier_conversation(
    db: Session, supplier_id: str, agent_id: str
) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter(
            Conversation.supplier_id == supplier_id,
            Conversation.agent_id == agent_id,
        )
        .first()
    )


def get_agent_conversations(db: Session, agent_id: str) -> list[Conversation]:
    return db.query(Conversation).filter(Conversation.agent_id == agent_id).all()


def get_conversation_messages(db: Session, conversation_id: str) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )


def add_message(
    db: Session, conversation_id: str, data: MessageCreate
) -> Message | None:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        return None

    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=data.role,
        content=data.content,
    )
    db.add(message)

    if data.role == MessageRole.SUPPLIER:
        conversation.negotiation_round += 1

    db.commit()
    db.refresh(message)
    return message


def create_deal_summary(db: Session, data: DealSummaryCreate) -> DealSummary:
    summary = DealSummary(
        id=str(uuid.uuid4()),
        agent_id=data.agent_id,
        final_price=data.final_price,
        terms=data.terms,
        notes=data.notes,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


def get_agent_deal_summaries(db: Session, agent_id: str) -> list[DealSummary]:
    return db.query(DealSummary).filter(DealSummary.agent_id == agent_id).all()


def get_deal_summary(db: Session, summary_id: str) -> DealSummary | None:
    return db.get(DealSummary, summary_id)


def update_deal_summary(
    db: Session, summary_id: str, data: DealSummaryUpdate
) -> DealSummary | None:
    summary = db.get(DealSummary, summary_id)
    if not summary:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(summary, field, value)

    db.commit()
    db.refresh(summary)
    return summary


def activate_agent(db: Session, agent_id: str) -> Agent | None:
    agent = db.get(Agent, agent_id)
    if not agent:
        return None
    if agent.status != AgentStatus.DRAFT:
        return None

    agent.status = AgentStatus.ACTIVE
    db.commit()
    db.refresh(agent)
    return agent


def create_conversation_for_supplier(
    db: Session, agent_id: str, supplier_id: str
) -> Conversation | None:
    agent = db.get(Agent, agent_id)
    if not agent or agent.status != AgentStatus.ACTIVE:
        return None

    supplier = db.get(Supplier, supplier_id)
    if not supplier or supplier.agent_id != agent_id:
        return None

    existing = (
        db.query(Conversation)
        .filter(
            Conversation.agent_id == agent_id,
            Conversation.supplier_id == supplier_id,
        )
        .first()
    )
    if existing:
        return existing

    supplier.status = SupplierStatus.ACTIVE
    conversation = Conversation(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        supplier_id=supplier_id,
        negotiation_round=0,
        status=ConversationStatus.ACTIVE,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def renegotiate_conversation(db: Session, conversation_id: str) -> Conversation | None:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        return None

    if conversation.status not in [
        ConversationStatus.REJECTED,
        ConversationStatus.EXPIRED,
    ]:
        if conversation.negotiation_round >= 1:
            return None

    conversation.negotiation_round = 0
    conversation.status = ConversationStatus.ACTIVE
    db.commit()
    db.refresh(conversation)
    return conversation


def create_auto_summary(
    db: Session,
    agent_id: str,
    conversation_id: str,
    final_price: float,
    terms: str | None = None,
) -> DealSummary:
    summary = DealSummary(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        conversation_id=conversation_id,
        final_price=final_price,
        terms=terms,
        is_auto_generated=True,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


def approve_summary(db: Session, summary_id: str) -> DealSummary | None:
    summary = db.get(DealSummary, summary_id)
    if not summary:
        return None

    summary.status = DealStatus.APPROVED

    agent = db.get(Agent, summary.agent_id)
    if agent:
        agent.status = AgentStatus.COMPLETED

    db.commit()
    db.refresh(summary)
    return summary


def reject_summary(db: Session, summary_id: str) -> DealSummary | None:
    summary = db.get(DealSummary, summary_id)
    if not summary:
        return None

    summary.status = DealStatus.REJECTED
    db.commit()
    db.refresh(summary)
    return summary


def update_supplier_status(
    db: Session, supplier_id: str, status: SupplierStatus
) -> Supplier | None:
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        return None

    supplier.status = status
    db.commit()
    db.refresh(supplier)
    return supplier


def update_conversation_status(
    db: Session, conversation_id: str, status: ConversationStatus
) -> Conversation | None:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        return None

    conversation.status = status
    db.commit()
    db.refresh(conversation)
    return conversation
