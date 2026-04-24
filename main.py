from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.fraud import router as fraud_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.middleware.rate_limiter import RateLimitMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    db = SessionLocal()
    try:
        try:
            init_db(db)
        except Exception as exc:
            logger.warning("Database initialization skipped during startup: %s", exc)
    finally:
        db.close()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(fraud_router)
