from __future__ import annotations

from dataclasses import dataclass

from app.core.DecisionStatus import DecisionStatus
from app.core.Rule import Rule


@dataclass(slots=True)
class RuleResult:
    rule: Rule
    status: DecisionStatus
    score: int
    reason: str = ""
    warning: str = ""

    def __post_init__(self) -> None:
        self.score = max(0, min(self.score, 100))
