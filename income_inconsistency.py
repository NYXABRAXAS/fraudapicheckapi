from app.services.rules.base import FraudRule, RuleContext, RuleResult


class IncomeInconsistencyRule(FraudRule):
    rule_name = "income_inconsistency"

    def evaluate(self, context: RuleContext) -> RuleResult:
        income_threshold = float(self.rule_config.get("income_threshold", 2500000))
        name_risk = sum(char.isdigit() for char in context.request.name)
        triggered = context.request.income > income_threshold or name_risk > 0
        return RuleResult(
            rule=self.rule_name,
            triggered=triggered,
            score=self.weight if triggered else 0,
            reason=(
                "Declared income is inconsistent with applicant profile heuristics"
                if triggered
                else "Income signals appear consistent"
            ),
            metadata={"income_threshold": income_threshold, "declared_income": context.request.income},
        )
