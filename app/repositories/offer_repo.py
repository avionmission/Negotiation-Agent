from app.repositories.base import BaseRepository
from app.models.offer import Offer


class OfferRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Offer)

    def create_offer(self, negotiation_id: int, supplier_id: int, price: float, terms: str | None = None):
        offer = Offer(
            negotiation_id=negotiation_id,
            supplier_id=supplier_id,
            price=price,
            terms=terms,
        )
        return self.add(offer)

    def get_best_offer(self, negotiation_id: int):
        return (
            self.db.query(Offer)
            .filter(Offer.negotiation_id == negotiation_id)
            .order_by(Offer.price.asc())
            .first()
        )
