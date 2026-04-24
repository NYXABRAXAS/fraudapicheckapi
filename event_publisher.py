import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self) -> None:
        self.settings = get_settings()

    def publish_fraud_decision(self, payload: dict) -> None:
        if not self.settings.enable_kafka:
            return
        logger.info(
            "Kafka publishing enabled but not wired to a client yet. Topic=%s payload_keys=%s",
            self.settings.kafka_topic_fraud_decisions,
            list(payload.keys()),
        )
