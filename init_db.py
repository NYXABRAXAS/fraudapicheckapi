from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.base import Base
from app.models.application import Application
from app.models.device_log import DeviceLog
from app.models.fraud_history import FraudHistory
from app.models.user import User


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=db.get_bind())
    seed_default_user(db)


def seed_default_user(db: Session) -> None:
    user = db.query(User).filter(User.username == "admin").first()
    if user:
        return
    admin = User(
        username="admin",
        full_name="Platform Admin",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        role="admin",
    )
    db.add(admin)
    db.commit()
