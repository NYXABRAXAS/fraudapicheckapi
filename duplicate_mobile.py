from app.services.rules.base import FraudRule, RuleContext, RuleResult


class DuplicateMobileRule(FraudRule):
    rule_name = "duplicate_mobile"

    def evaluate(self, context: RuleContext) -> RuleResult:
        applications_repo = context.repositories["applications"]
        count = applications_repo.count_by_mobile(context.request.mobile)
        triggered = count > 0
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason="Mobile number linked with existing application(s)" if triggered else "No mobile duplication found",
            metadata={"existing_applications": count},
        )
