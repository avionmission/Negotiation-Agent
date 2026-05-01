from sqlalchemy.orm import Session
from app.core.database import Base


class BaseRepository:
    def __init__(self, db: Session, model: type[Base]):
        self.db = db
        self.model = model

    def add(self, entity):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
