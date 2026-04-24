from __future__ import annotations

import hashlib
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.db.session import get_cache
from app.models.application import Application
from app.models.device_log import DeviceLog
from app.repositories.application_repository import ApplicationRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.fraud_repository import FraudRepository
from app.schemas.fraud import FraudCheckRequest, FraudCheckResponse, RuleExplanation
from app.services.audit_service import AuditService
from app.services.event_publisher import EventPublisher
from app.services.rule_engine import RuleEngine
from app.services.rules.base import RuleContext, RuleResult


class FraudScoringService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.cache = get_cache()
        self.applications = ApplicationRepository(db)
        self.devices = DeviceRepository(db)
        self.fraud_repo = FraudRepository(db)
        self.rule_engine = RuleEngine()
        self.audit_service = AuditService(self.fraud_repo)
        self.event_publisher = EventPublisher()

    def evaluate(self, request: FraudCheckRequest, evaluated_by: str) -> FraudCheckResponse:
        context = RuleContext(
            request=request,
            repositories={"applications": self.applications, "devices": self.devices},
            cache=self.cache,
            config=self.rule_engine.rule_definitions,
        )
        results = self.rule_engine.evaluate(context)
        response = self._build_response(results)
        application = self._persist_application(request)
        if request.device_fingerprint:
            self._persist_device_log(request, application.id)
        self.audit_service.log_decision(
            application_id=application.id,
            customer_id=request.customer_id,
            response=response,
            evaluated_by=evaluated_by,
        )
        self.db.commit()
        self.event_publisher.publish_fraud_decision(
            {
                "application_id": application.id,
                "customer_id": request.customer_id,
                "fraud_score": response.fraud_score,
                "risk_level": response.risk_level,
                "decision": response.decision,
            }
        )
        return response

    def _build_response(self, results: Iterable[RuleResult]) -> FraudCheckResponse:
        result_list = list(results)
        total_weight = sum(rule.weight for rule in self.rule_engine.rules) or 1
        raw_score = sum(item.score for item in result_list)
        normalized_score = round(min((raw_score / total_weight) * 100, 100), 2)
        risk_level = self._classify_risk(normalized_score)
        decision = self._decision_for_risk(risk_level)
        flags = [item.reason for item in result_list if item.triggered]
        explanations = [
            RuleExplanation(
                rule=item.rule,
                triggered=item.triggered,
                score=item.score,
                reason=item.reason,
                metadata=item.metadata,
            )
            for item in result_list
        ]
        return FraudCheckResponse(
            fraud_score=normalized_score,
            risk_level=risk_level,
            flags=flags,
            decision=decision,
            explanations=explanations,
        )

    def _persist_application(self, request: FraudCheckRequest) -> Application:
        masked_notes = self._masked_identity(request.pan, request.mobile)
        application = Application(
            customer_id=request.customer_id,
            name=request.name,
            pan=request.pan,
            mobile=request.mobile,
            email=request.email,
            ip_address=request.ip_address,
            income=request.income,
            submitted_at=request.timestamp,
            device_fingerprint=request.device_fingerprint,
            source_system=request.source_system,
            status="EVALUATED",
            notes=f"masked_identity={masked_notes}",
        )
        return self.applications.create(application)

    def _persist_device_log(self, request: FraudCheckRequest, application_id: int) -> DeviceLog:
        log = DeviceLog(
            customer_id=request.customer_id,
            application_id=application_id,
            device_fingerprint=request.device_fingerprint or "",
            ip_address=request.ip_address,
        )
        return self.devices.create(log)

    @staticmethod
    def _classify_risk(score: float) -> str:
        if score <= 30:
            return "LOW"
        if score <= 70:
            return "MEDIUM"
        return "HIGH"

    @staticmethod
    def _decision_for_risk(risk_level: str) -> str:
        return {"LOW": "APPROVE", "MEDIUM": "REVIEW", "HIGH": "REJECT"}[risk_level]

    @staticmethod
    def _masked_identity(pan: str, mobile: str) -> str:
        fingerprint = hashlib.sha256(f"{pan}:{mobile}".encode("utf-8")).hexdigest()
        return fingerprint[:16]
