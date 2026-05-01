from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.message_repo import MessageRepository
from app.repositories.supplier_repo import SupplierRepository
from app.services.negotiation_agent import NegotiationAgent
from app.services.gemini_client import GeminiClient

router = APIRouter()


@router.post("/chat/{negotiation_id}/{supplier_id}")
def chat(negotiation_id: int, supplier_id: int, content: str, db: Session = Depends(get_db)):
    message_repo = MessageRepository(db)
    supplier_repo = SupplierRepository(db)

    supplier = supplier_repo.get_by_id(supplier_id)

    message_repo.create_message(negotiation_id, supplier_id, "supplier", content)

    agent = NegotiationAgent(GeminiClient())
    reply = agent.generate_reply("", None, supplier, [])

    message_repo.create_message(negotiation_id, supplier_id, "agent", reply)

    return {"reply": reply}
