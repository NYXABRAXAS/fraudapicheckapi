from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.fraud import FraudCheckRequest


@dataclass
class RuleContext:
    request: FraudCheckRequest
    repositories: dict[str, Any]
    cache: Any
    config: dict[str, Any]


@dataclass
class RuleResult:
    rule: str
    triggered: bool
    score: float
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


class FraudRule:
    rule_name: str = ""

    def __init__(self, rule_config: dict[str, Any]) -> None:
        self.rule_config = rule_config
        self.weight = float(rule_config.get("weight", 0))

    def evaluate(self, context: RuleContext) -> RuleResult:
        raise NotImplementedError
