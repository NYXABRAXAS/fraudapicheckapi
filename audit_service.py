from app.models.fraud_history import FraudHistory
from app.repositories.fraud_repository import FraudRepository
from app.schemas.fraud import FraudCheckResponse


class AuditService:
    def __init__(self, fraud_repository: FraudRepository) -> None:
        self.fraud_repository = fraud_repository

    def log_decision(
        self,
        application_id: int,
        customer_id: str,
        response: FraudCheckResponse,
        evaluated_by: str,
    ) -> FraudHistory:
        record = FraudHistory(
            application_id=application_id,
            customer_id=customer_id,
            fraud_score=response.fraud_score,
            risk_level=response.risk_level,
            decision=response.decision,
            flags=response.flags,
            explanation=[item.model_dump() for item in response.explanations],
            evaluated_by=evaluated_by,
        )
        return self.fraud_repository.create(record)
