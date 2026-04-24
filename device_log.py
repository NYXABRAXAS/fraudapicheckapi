from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeviceLog(Base):
    __tablename__ = "device_logs"
    __table_args__ = (
        Index("ix_device_logs_fingerprint_created_at", "device_fingerprint", "created_at"),
        Index("ix_device_logs_customer_created_at", "customer_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    application_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
