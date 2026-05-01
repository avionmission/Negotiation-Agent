from app.repositories.base import BaseRepository
from app.models.supplier import Supplier


class SupplierRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Supplier)

    def get_all(self):
        return self.db.query(Supplier).all()

    def get_by_id(self, supplier_id: int):
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
