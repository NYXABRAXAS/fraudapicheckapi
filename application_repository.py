from datetime import datetime, timedelta

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.models.application import Application


class ApplicationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, application: Application) -> Application:
        self.db.add(application)
        self.db.flush()
        return application

    def count_by_pan(self, pan: str) -> int:
        return self.db.query(func.count(Application.id)).filter(Application.pan == pan).scalar() or 0

    def count_by_mobile(self, mobile: str) -> int:
        return (
            self.db.query(func.count(Application.id)).filter(Application.mobile == mobile).scalar() or 0
        )

    def count_recent_by_mobile(self, mobile: str, window_minutes: int, now: datetime) -> int:
        window_start = now - timedelta(minutes=window_minutes)
        return (
            self.db.query(func.count(Application.id))
            .filter(Application.mobile == mobile, Application.created_at >= window_start)
            .scalar()
            or 0
        )

    def count_distinct_customers_by_ip(self, ip_address: str, window_minutes: int, now: datetime) -> int:
        window_start = now - timedelta(minutes=window_minutes)
        return (
            self.db.query(func.count(distinct(Application.customer_id)))
            .filter(Application.ip_address == ip_address, Application.created_at >= window_start)
            .scalar()
            or 0
        )
