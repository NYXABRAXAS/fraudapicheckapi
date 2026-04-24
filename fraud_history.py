from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FraudHistory(Base):
    __tablename__ = "fraud_history"
    __table_args__ = (
        Index("ix_fraud_history_customer_created_at", "customer_id", "created_at"),
        Index("ix_fraud_history_risk_level_created_at", "risk_level", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    fraud_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    flags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    explanation: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    evaluated_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
