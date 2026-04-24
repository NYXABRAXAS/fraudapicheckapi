from app.core.config import get_settings
from app.services.rules.base import FraudRule, RuleContext, RuleResult


class IpAnomalyRule(FraudRule):
    rule_name = "ip_anomaly"

    def evaluate(self, context: RuleContext) -> RuleResult:
        settings = get_settings()
        applications_repo = context.repositories["applications"]
        max_distinct_customers = int(self.rule_config.get("max_distinct_customers", 3))
        distinct_customers = applications_repo.count_distinct_customers_by_ip(
            ip_address=context.request.ip_address,
            window_minutes=settings.velocity_window_minutes,
            now=context.request.timestamp,
        )
        triggered = distinct_customers >= max_distinct_customers
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason=(
                "IP address is associated with multiple distinct recent applicants"
                if triggered
                else "IP activity appears normal"
            ),
            metadata={
                "distinct_customers": distinct_customers,
                "threshold": max_distinct_customers,
            },
        )
