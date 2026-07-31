from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from app.core.DecisionStatus import DecisionStatus
from app.core.EngineResult import EngineResult
from app.core.RuleResult import RuleResult
from app.core.Score import Score


@dataclass(slots=True)
class DecisionNode:
    engine: str
    status: DecisionStatus
    score: Score
    rules: list[RuleResult]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration: float = 0.0

    @staticmethod
    def from_engine_result(result: EngineResult) -> "DecisionNode":
        return DecisionNode(
            engine=result.engine,
            status=result.status,
            score=result.score,
            rules=[*result.passedRules, *result.failedRules],
            duration=result.executionTime,
        )
