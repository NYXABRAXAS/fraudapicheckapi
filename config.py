from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fraud Detection API"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/frauddb"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    rate_limit_per_minute: int = 60
    velocity_window_minutes: int = 15
    velocity_threshold: int = 3
    rules_config_path: str = "app/core/rules.json"
    enable_kafka: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_fraud_decisions: str = "fraud.decisions"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def rules_path(self) -> Path:
        return Path(self.rules_config_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()
