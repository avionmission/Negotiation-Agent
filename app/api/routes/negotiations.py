from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.negotiation import NegotiationCreate, NegotiationResponse
from app.repositories.negotiation_repo import NegotiationRepository

router = APIRouter()


@router.post("/negotiations", response_model=NegotiationResponse)
def create_negotiation(data: NegotiationCreate, db: Session = Depends(get_db)):
    repo = NegotiationRepository(db)
    return repo.add(data)


@router.post("/negotiations/{negotiation_id}/run")
def run_negotiation(negotiation_id: int, db: Session = Depends(get_db)):
    return {"message": f"Negotiation {negotiation_id} started"}
