from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
    BuyerCreate,
    BuyerLoginRequest,
    BuyerLoginResponse,
    BuyerResponse,
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationDetail,
    ConversationResponse,
    ConversationWithMessages,
    DealSummaryCreate,
    DealSummaryResponse,
    DealSummaryUpdate,
    MessageCreate,
    MessageResponse,
    SupplierCreate,
    SupplierLoginRequest,
    SupplierLoginResponse,
    SupplierResponse,
)
from app.services import business_service, agent_service
from app.models.models import (
    MessageRole,
    ConversationStatus,
    DealStatus,
    AgentStatus,
    SupplierStatus,
)


router = APIRouter()


@router.post(
    "/buyers", response_model=BuyerResponse, status_code=status.HTTP_201_CREATED
)
def create_buyer(data: BuyerCreate, db: Session = Depends(get_db)):
    existing = business_service.get_buyer_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer with this email already exists",
        )
    return business_service.create_buyer(db, data)


@router.post("/buyers/login", response_model=BuyerLoginResponse)
def buyer_login(data: BuyerLoginRequest, db: Session = Depends(get_db)):
    buyer = business_service.login_buyer(db, data.email)
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found",
        )
    if not buyer.access_token or not buyer.token_expiry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate access token",
        )
    return BuyerLoginResponse(
        buyer_id=buyer.id,
        access_token=buyer.access_token,
        token_expiry=buyer.token_expiry,
    )


@router.post("/suppliers/login", response_model=SupplierLoginResponse)
def supplier_login(data: SupplierLoginRequest, db: Session = Depends(get_db)):
    supplier = business_service.login_supplier(db, data.email, data.agent_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found for this agent",
        )
    if not supplier.access_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supplier has no access token",
        )
    return SupplierLoginResponse(
        supplier_id=supplier.id,
        access_token=supplier.access_token,
        token_expiry=supplier.token_expiry,
    )


@router.get("/buyers/{buyer_id}", response_model=BuyerResponse)
def get_buyer(buyer_id: str, db: Session = Depends(get_db)):
    buyer = business_service.get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found"
        )
    return buyer


@router.post(
    "/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED
)
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    buyer = business_service.get_buyer(db, data.buyer_id)
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found"
        )
    return business_service.create_agent(db, data)


@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )
    return agent


@router.patch("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: str,
    data: AgentUpdate,
    db: Session = Depends(get_db),
):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    if agent.status != AgentStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent cannot be modified after activation",
        )

    return business_service.update_agent(db, agent_id, data)


@router.get("/agents", response_model=list[AgentResponse])
def list_agents(buyer_id: str | None = None, db: Session = Depends(get_db)):
    return business_service.list_agents(db, buyer_id)


@router.post(
    "/agents/{agent_id}/activate",
    response_model=AgentResponse,
)
def activate_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    if agent.status != AgentStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DRAFT agents can be activated",
        )

    result = business_service.activate_agent(db, agent_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to activate agent",
        )
    return result


@router.post(
    "/agents/{agent_id}/suppliers",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_supplier(agent_id: str, data: SupplierCreate, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    if agent.status == AgentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add suppliers to completed agent",
        )

    supplier = business_service.add_supplier(db, agent_id, data)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add supplier"
        )
    return supplier


@router.get("/agents/{agent_id}/suppliers", response_model=list[SupplierResponse])
def get_agent_suppliers(agent_id: str, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )
    return business_service.get_agent_suppliers(db, agent_id)


@router.post(
    "/agents/{agent_id}/conversations",
    response_model=ConversationResponse,
)
def create_conversation(agent_id: str, supplier_id: str, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    if agent.status != AgentStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent must be ACTIVE to start conversation",
        )

    conversation = business_service.create_conversation_for_supplier(
        db, agent_id, supplier_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create conversation",
        )
    return conversation


@router.get(
    "/agents/{agent_id}/conversations", response_model=list[ConversationWithMessages]
)
def get_agent_conversations(agent_id: str, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    conversations = business_service.get_agent_conversations(db, agent_id)
    result = []
    for conv in conversations:
        messages = business_service.get_conversation_messages(db, conv.id)
        supplier = business_service.get_supplier_by_id(db, conv.supplier_id)
        result.append(
            ConversationWithMessages(
                id=conv.id,
                agent_id=conv.agent_id,
                supplier_id=conv.supplier_id,
                negotiation_round=conv.negotiation_round,
                status=conv.status,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                messages=[
                    MessageResponse(
                        id=m.id,
                        conversation_id=m.conversation_id,
                        role=m.role,
                        content=m.content,
                        created_at=m.created_at,
                    )
                    for m in messages
                ],
            )
        )
    return result


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetail,
)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = business_service.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    agent = business_service.get_agent(db, conversation.agent_id)
    supplier = business_service.get_supplier_by_id(db, conversation.supplier_id)

    return ConversationDetail(
        id=conversation.id,
        agent_id=conversation.agent_id,
        supplier_id=conversation.supplier_id,
        negotiation_round=conversation.negotiation_round,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        supplier_status=supplier.status if supplier else SupplierStatus.INACTIVE,
        max_rounds=agent.max_negotiation_rounds if agent else 3,
        is_final=conversation.negotiation_round
        >= (agent.max_negotiation_rounds if agent else 3),
    )


@router.post("/chat/{conversation_id}/message", response_model=ChatResponse)
def post_chat_message(
    conversation_id: str,
    data: ChatRequest,
    db: Session = Depends(get_db),
):
    supplier = business_service.get_supplier_by_token(db, data.token)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    if supplier.status != SupplierStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supplier is not active",
        )

    conversation = business_service.get_conversation(db, conversation_id)
    if not conversation or conversation.supplier_id != supplier.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.status not in [
        ConversationStatus.ACTIVE,
        ConversationStatus.NEGOTIATING,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conversation is not active (status: {conversation.status})",
        )

    agent = business_service.get_agent(db, conversation.agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    if conversation.negotiation_round >= agent.max_negotiation_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max negotiation rounds reached",
        )

    if conversation.negotiation_round >= agent.max_negotiation_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max negotiation rounds reached",
        )

    current_round = conversation.negotiation_round

    business_service.add_message(
        db,
        conversation_id,
        MessageCreate(role=MessageRole.SUPPLIER, content=data.message),
    )

    agent_svc = agent_service.get_agent_service()
    summary_id = None

    if current_round == 0:
        initial_offer = agent_svc.generate_initial_offer(
            buyer_name=agent.buyer.name,
            budget=agent.budget,
            requirements=agent.description,
            knowledge_base=agent.knowledge_base,
        )

        business_service.add_message(
            db,
            conversation_id,
            MessageCreate(role=MessageRole.AGENT, content=initial_offer),
        )

        conversation.status = ConversationStatus.NEGOTIATING
        db.commit()

        return ChatResponse(
            response=initial_offer,
            negotiation_round=current_round + 1,
            is_final=False,
            status=ConversationStatus.NEGOTIATING,
            summary_id=None,
        )

    current_offer = agent.budget * 0.9
    conversation_history = [
        m.content
        for m in business_service.get_conversation_messages(db, conversation_id)
    ]

    response_text, new_offer, is_final = agent_svc.process_supplier_response(
        supplier_message=data.message,
        current_offer=current_offer,
        budget=agent.budget,
        negotiation_round=current_round,
        max_rounds=agent.max_negotiation_rounds,
        conversation_history=conversation_history,
    )

    business_service.add_message(
        db,
        conversation_id,
        MessageCreate(role=MessageRole.AGENT, content=response_text),
    )

    new_status = ConversationStatus.NEGOTIATING

    if is_final or conversation.negotiation_round >= agent.max_negotiation_rounds - 1:
        decision = agent_svc.evaluate_acceptance(response_text, new_offer, agent.budget)

        if decision == "ACCEPT":
            summary = business_service.create_auto_summary(
                db,
                agent_id=agent.id,
                conversation_id=conversation_id,
                final_price=new_offer,
                terms=f"Negotiated price based on {conversation.negotiation_round} rounds",
            )
            summary_id = summary.id

            conversation.status = ConversationStatus.ACCEPTED
            new_status = ConversationStatus.ACCEPTED

            business_service.update_supplier_status(db, supplier.id, SupplierStatus.WON)

        elif decision == "REJECT":
            conversation.status = ConversationStatus.REJECTED
            new_status = ConversationStatus.REJECTED

            business_service.update_supplier_status(
                db, supplier.id, SupplierStatus.LOST
            )
        else:
            conversation.status = ConversationStatus.NEGOTIATING
    else:
        conversation.status = ConversationStatus.NEGOTIATING

    db.commit()

    return ChatResponse(
        response=response_text,
        negotiation_round=conversation.negotiation_round,
        is_final=is_final
        or new_status in [ConversationStatus.ACCEPTED, ConversationStatus.REJECTED],
        status=new_status,
        summary_id=summary_id,
    )


@router.post(
    "/conversations/{conversation_id}/renegotiate",
    response_model=ConversationResponse,
)
def renegotiate_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    conversation = business_service.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.status not in [
        ConversationStatus.REJECTED,
        ConversationStatus.EXPIRED,
    ]:
        if conversation.negotiation_round > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only renegotiate rejected or expired conversations",
            )

    result = business_service.renegotiate_conversation(db, conversation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to renegotiate",
        )
    return result


@router.get("/summaries/{agent_id}", response_model=list[DealSummaryResponse])
def get_summaries(agent_id: str, db: Session = Depends(get_db)):
    agent = business_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )
    return business_service.get_agent_deal_summaries(db, agent_id)


@router.post(
    "/summaries/{summary_id}/approve",
    response_model=DealSummaryResponse,
)
def approve_summary(summary_id: str, db: Session = Depends(get_db)):
    summary = business_service.get_deal_summary(db, summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    result = business_service.approve_summary(db, summary_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to approve summary",
        )
    return result


@router.post(
    "/summaries/{summary_id}/reject",
    response_model=DealSummaryResponse,
)
def reject_summary(summary_id: str, db: Session = Depends(get_db)):
    summary = business_service.get_deal_summary(db, summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    result = business_service.reject_summary(db, summary_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reject summary",
        )
    return result


@router.patch("/summaries/{summary_id}", response_model=DealSummaryResponse)
def update_summary(
    summary_id: str,
    data: DealSummaryUpdate,
    db: Session = Depends(get_db),
):
    summary = business_service.get_deal_summary(db, summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    if data.status and data.status not in [DealStatus.APPROVED, DealStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only set status to APPROVED or REJECTED",
        )

    return business_service.update_deal_summary(db, summary_id, data)
