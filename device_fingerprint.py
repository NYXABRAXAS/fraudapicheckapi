from app.core.config import get_settings
from app.services.rules.base import FraudRule, RuleContext, RuleResult


class DeviceFingerprintRule(FraudRule):
    rule_name = "device_fingerprint"

    def evaluate(self, context: RuleContext) -> RuleResult:
        fingerprint = context.request.device_fingerprint
        if not fingerprint:
            return RuleResult(
                rule=self.rule_name,
                triggered=False,
                score=0,
                reason="Device fingerprint not provided; placeholder logic skipped",
                metadata={},
            )

        settings = get_settings()
        device_repo = context.repositories["devices"]
        count = device_repo.count_recent_by_fingerprint(
            fingerprint=fingerprint,
            window_minutes=settings.velocity_window_minutes,
            now=context.request.timestamp,
        )
        triggered = count >= 1
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason="Device fingerprint reused across recent applications" if triggered else "Device activity appears normal",
            metadata={"recent_device_hits": count},
        )
