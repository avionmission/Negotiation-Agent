from app.repositories.base import BaseRepository
from app.models.negotiation import Negotiation


class NegotiationRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Negotiation)

    def get_all(self):
        return self.db.query(Negotiation).all()

    def get_by_id(self, negotiation_id: int):
        return self.db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
