import json
from pathlib import Path

from app.core.config import get_settings
from app.services.rules.base import FraudRule, RuleContext, RuleResult
from app.services.rules.device_fingerprint import DeviceFingerprintRule
from app.services.rules.duplicate_mobile import DuplicateMobileRule
from app.services.rules.duplicate_pan import DuplicatePanRule
from app.services.rules.email_pattern import EmailPatternRiskRule
from app.services.rules.income_inconsistency import IncomeInconsistencyRule
from app.services.rules.ip_anomaly import IpAnomalyRule
from app.services.rules.velocity import VelocityRule

RULE_REGISTRY: dict[str, type[FraudRule]] = {
    "duplicate_pan": DuplicatePanRule,
    "duplicate_mobile": DuplicateMobileRule,
    "velocity_check": VelocityRule,
    "ip_anomaly": IpAnomalyRule,
    "email_pattern_risk": EmailPatternRiskRule,
    "income_inconsistency": IncomeInconsistencyRule,
    "device_fingerprint": DeviceFingerprintRule,
}


class RuleEngine:
    def __init__(self, config_path: Path | None = None) -> None:
        self.settings = get_settings()
        self.config_path = config_path or self.settings.rules_path
        self.rule_definitions = self._load_config()
        self.rules = self._build_rules()

    def _load_config(self) -> dict:
        with self.config_path.open("r", encoding="utf-8") as file:
            return json.load(file)["rules"]

    def _build_rules(self) -> list[FraudRule]:
        rules: list[FraudRule] = []
        for name, rule_config in self.rule_definitions.items():
            if not rule_config.get("enabled", False):
                continue
            rule_class = RULE_REGISTRY[name]
            rules.append(rule_class(rule_config))
        return rules

    def evaluate(self, context: RuleContext) -> list[RuleResult]:
        return [rule.evaluate(context) for rule in self.rules]
