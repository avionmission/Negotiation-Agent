from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.negotiation import Negotiation
from app.repositories.message_repo import MessageRepository
from app.repositories.negotiation_repo import NegotiationRepository
from app.repositories.supplier_repo import SupplierRepository
from app.services.negotiation_agent import NegotiationAgent
from app.services.gemini_client import GeminiClient

router = APIRouter()


@router.post("/chat/{negotiation_id}/{supplier_id}")
def chat(negotiation_id: int, supplier_id: int, content: str, db: Session = Depends(get_db)):
    message_repo = MessageRepository(db)
    supplier_repo = SupplierRepository(db)
    negotiation_repo = NegotiationRepository(db)

    negotiation = negotiation_repo.get_by_id(negotiation_id)
    supplier = supplier_repo.get_by_id(supplier_id)

    if not negotiation or not supplier:
        return {"error": "Negotiation or Supplier not found"}

    # Step 1: Save supplier message
    message_repo.create_message(negotiation_id, supplier_id, "supplier", content)

    # Step 2: Initialize agent
    agent = NegotiationAgent(GeminiClient())

    # Step 3: Interpret supplier message
    extracted = agent.interpret_message(content)

    # Step 4: Update memory/state
    if extracted.get("price"):
        agent.update_memory(negotiation, extracted["price"])
        db.commit()

    # Step 5: Get history for context
    history = message_repo.get_history(negotiation_id, limit=10)

    # Step 6: Decide strategy
    strategy = agent.decide_strategy(negotiation, extracted.get("price"))

    # Step 7: Generate response
    reply = agent.generate_response(strategy, negotiation, supplier, history)

    # Step 8: Save agent reply
    message_repo.create_message(negotiation_id, supplier_id, "agent", reply)

    return {"reply": reply, "strategy": strategy, "round": negotiation.round_number}
