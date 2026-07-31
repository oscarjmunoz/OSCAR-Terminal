from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from app.core.DecisionStatus import DecisionStatus
from app.core.RuleResult import RuleResult
from app.core.Score import Score


@dataclass(slots=True)
class EngineResult:
    engine: str
    status: DecisionStatus
    score: Score
    passedRules: list[RuleResult] = field(default_factory=list)
    failedRules: list[RuleResult] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    executionTime: float = 0.0

    def add_rule_result(self, result: RuleResult) -> None:
        if result.status in {DecisionStatus.PASS, DecisionStatus.READY}:
            self.passedRules.append(result)
        else:
            self.failedRules.append(result)

        if result.reason:
            self.reasons.append(result.reason)

        if result.warning:
            self.warnings.append(result.warning)
