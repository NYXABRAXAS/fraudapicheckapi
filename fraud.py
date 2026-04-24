from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class FraudCheckRequest(BaseModel):
    customer_id: str = Field(..., min_length=3, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    pan: str = Field(..., min_length=10, max_length=10)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: EmailStr
    ip_address: str = Field(..., min_length=7, max_length=64)
    income: float = Field(..., ge=0)
    timestamp: datetime
    device_fingerprint: str | None = Field(default=None, max_length=255)
    source_system: str = Field(default="LOS", max_length=100)

    @field_validator("pan")
    @classmethod
    def normalize_pan(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("mobile")
    @classmethod
    def normalize_mobile(cls, value: str) -> str:
        return "".join(char for char in value if char.isdigit())


class RuleExplanation(BaseModel):
    rule: str
    triggered: bool
    score: float
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class FraudCheckResponse(BaseModel):
    fraud_score: float
    risk_level: str
    flags: list[str]
    decision: str
    explanations: list[RuleExplanation]

    model_config = ConfigDict(from_attributes=True)
