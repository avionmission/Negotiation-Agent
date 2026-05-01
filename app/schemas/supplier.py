from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    contact_info: str | None = None
    category: str | None = None
    rating: float | None = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_info: str | None = None
    category: str | None = None
    rating: float | None = None

    class Config:
        from_attributes = True
