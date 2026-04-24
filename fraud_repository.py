from sqlalchemy.orm import Session

from app.models.fraud_history import FraudHistory


class FraudRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, record: FraudHistory) -> FraudHistory:
        self.db.add(record)
        self.db.flush()
        return record
