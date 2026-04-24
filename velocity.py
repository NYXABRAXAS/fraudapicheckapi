from app.core.config import get_settings
from app.services.rules.base import FraudRule, RuleContext, RuleResult


class VelocityRule(FraudRule):
    rule_name = "velocity_check"

    def evaluate(self, context: RuleContext) -> RuleResult:
        settings = get_settings()
        applications_repo = context.repositories["applications"]
        recent_count = applications_repo.count_recent_by_mobile(
            mobile=context.request.mobile,
            window_minutes=settings.velocity_window_minutes,
            now=context.request.timestamp,
        )
        effective_count = recent_count + 1
        triggered = effective_count >= settings.velocity_threshold
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason=(
                f"Application velocity threshold breached in {settings.velocity_window_minutes} minute window"
                if triggered
                else "Application velocity within allowed range"
            ),
            metadata={
                "recent_applications": effective_count,
                "threshold": settings.velocity_threshold,
            },
        )
