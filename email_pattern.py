from app.services.rules.base import FraudRule, RuleContext, RuleResult


class EmailPatternRiskRule(FraudRule):
    rule_name = "email_pattern_risk"

    def evaluate(self, context: RuleContext) -> RuleResult:
        domain = context.request.email.split("@")[-1].lower()
        temporary_domains = set(self.rule_config.get("temporary_domains", []))
        risky_keywords = {"test", "fake", "temp", "demo"}
        local_part = context.request.email.split("@")[0].lower()
        triggered = domain in temporary_domains or any(keyword in local_part for keyword in risky_keywords)
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason="Email pattern indicates temporary or synthetic identity risk" if triggered else "Email pattern appears normal",
            metadata={"domain": domain},
        )
