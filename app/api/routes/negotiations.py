from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.negotiation import NegotiationCreate, NegotiationResponse
from app.repositories.negotiation_repo import NegotiationRepository
from app.repositories.supplier_repo import SupplierRepository
from app.services.knowledge_builder import KnowledgeBuilder
from app.services.gemini_client import GeminiClient
from app.models.negotiation import Negotiation
from app.models.negotiation_supplier import NegotiationSupplier

router = APIRouter()


@router.post("/negotiations", response_model=NegotiationResponse)
def create_negotiation(data: NegotiationCreate, db: Session = Depends(get_db)):
    knowledge_builder = KnowledgeBuilder(GeminiClient())
    context = knowledge_builder.build_context(data.raw_requirements)

    negotiation = Negotiation(
        title=data.title,
        system_prompt=data.system_prompt,
        target_price=context.get("target_price"),
        max_budget=context.get("budget"),
        buyer_budget=context.get("budget"),
        status="initialized",
    )
    repo = NegotiationRepository(db)
    return repo.add(negotiation)


@router.post("/negotiations/{negotiation_id}/run")
def run_negotiation(negotiation_id: int, db: Session = Depends(get_db)):
    repo = NegotiationRepository(db)
    negotiation = repo.get_by_id(negotiation_id)
    if negotiation:
        negotiation.status = "negotiating"
        db.commit()
    return {"message": f"Negotiation {negotiation_id} started", "status": negotiation.status if negotiation else "not found"}


@router.post("/negotiations/{negotiation_id}/join/{supplier_id}")
def join_negotiation(negotiation_id: int, supplier_id: int, db: Session = Depends(get_db)):
    negotiation_repo = NegotiationRepository(db)
    supplier_repo = SupplierRepository(db)

    negotiation = negotiation_repo.get_by_id(negotiation_id)
    supplier = supplier_repo.get_by_id(supplier_id)

    if not negotiation or not supplier:
        return {"error": "Negotiation or Supplier not found"}

    existing = (
        db.query(NegotiationSupplier)
        .filter_by(negotiation_id=negotiation_id, supplier_id=supplier_id)
        .first()
    )
    if existing:
        return {"message": f"Supplier {supplier_id} already joined"}

    link = NegotiationSupplier(negotiation_id=negotiation_id, supplier_id=supplier_id)
    db.add(link)
    db.commit()
    return {"message": f"Supplier {supplier.name} joined negotiation {negotiation.title}"}
