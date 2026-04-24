from app.services.rules.base import FraudRule, RuleContext, RuleResult


class DuplicatePanRule(FraudRule):
    rule_name = "duplicate_pan"

    def evaluate(self, context: RuleContext) -> RuleResult:
        applications_repo = context.repositories["applications"]
        count = applications_repo.count_by_pan(context.request.pan)
        triggered = count > 0
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason="PAN already used in previous applications" if triggered else "No PAN duplication found",
            metadata={"existing_applications": count},
        )
