from datetime import datetime, timedelta, timezone

from app.schemas.fraud import FraudCheckRequest
from app.services.rules.duplicate_pan import DuplicatePanRule
from app.services.rules.email_pattern import EmailPatternRiskRule
from app.services.rules.velocity import VelocityRule
from app.services.rules.base import RuleContext


class StubApplicationsRepo:
    def count_by_pan(self, pan: str) -> int:
        return 2 if pan == "ABCDE1234F" else 0

    def count_recent_by_mobile(self, mobile: str, window_minutes: int, now: datetime) -> int:
        return 4


def build_request() -> FraudCheckRequest:
    return FraudCheckRequest(
        customer_id="CUST-1",
        name="Rahul Sharma",
        pan="ABCDE1234F",
        mobile="9999999999",
        email="risk@mailinator.com",
        ip_address="10.10.10.10",
        income=125000,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=1),
    )


def test_duplicate_pan_rule_triggers() -> None:
    context = RuleContext(
        request=build_request(),
        repositories={"applications": StubApplicationsRepo(), "devices": object()},
        cache=None,
        config={},
    )
    result = DuplicatePanRule({"weight": 30}).evaluate(context)
    assert result.triggered is True
    assert result.score == 30


def test_email_pattern_rule_triggers_for_temp_domain() -> None:
    context = RuleContext(
        request=build_request(),
        repositories={"applications": StubApplicationsRepo(), "devices": object()},
        cache=None,
        config={},
    )
    result = EmailPatternRiskRule(
        {"weight": 10, "temporary_domains": ["mailinator.com"]}
    ).evaluate(context)
    assert result.triggered is True
    assert result.metadata["domain"] == "mailinator.com"


def test_velocity_rule_triggers() -> None:
    context = RuleContext(
        request=build_request(),
        repositories={"applications": StubApplicationsRepo(), "devices": object()},
        cache=None,
        config={},
    )
    result = VelocityRule({"weight": 20}).evaluate(context)
    assert result.triggered is True
    assert result.score == 20
