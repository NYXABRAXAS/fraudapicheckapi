from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.device_log import DeviceLog


class DeviceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, log: DeviceLog) -> DeviceLog:
        self.db.add(log)
        self.db.flush()
        return log

    def count_recent_by_fingerprint(self, fingerprint: str, window_minutes: int, now: datetime) -> int:
        window_start = now - timedelta(minutes=window_minutes)
        return (
            self.db.query(func.count(DeviceLog.id))
            .filter(
                DeviceLog.device_fingerprint == fingerprint,
                DeviceLog.created_at >= window_start,
            )
            .scalar()
            or 0
        )
