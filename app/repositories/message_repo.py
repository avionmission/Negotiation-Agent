from app.repositories.base import BaseRepository
from app.models.message import Message


class MessageRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Message)

    def create_message(self, negotiation_id: int, supplier_id: int, sender: str, content: str):
        message = Message(
            negotiation_id=negotiation_id,
            supplier_id=supplier_id,
            sender=sender,
            content=content,
        )
        return self.add(message)

    def get_history(self, negotiation_id: int, limit: int = 10):
        return (
            self.db.query(Message)
            .filter(Message.negotiation_id == negotiation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
            .all()
        )
