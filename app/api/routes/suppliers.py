from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.supplier import SupplierCreate, SupplierResponse
from app.repositories.supplier_repo import SupplierRepository

router = APIRouter()


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    repo = SupplierRepository(db)
    supplier = SupplierCreate(**data.model_dump())
    return repo.add(supplier)


@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db)):
    repo = SupplierRepository(db)
    return repo.get_all()
