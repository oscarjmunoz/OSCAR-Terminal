from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.DecisionStatus import DecisionStatus
from app.core.EngineResult import EngineResult
from app.core.Score import Score


DecisionDirection = Literal["BULLISH", "BEARISH", "NONE"]
InstitutionalDecisionState = Literal["VALID_LONG", "VALID_SHORT", "INVALID"]


@dataclass(slots=True)
class InstitutionalDecisionResult(EngineResult):
    valid: bool = False
    decisionState: InstitutionalDecisionState = "INVALID"
    direction: DecisionDirection = "NONE"
    institutionalScore: int = 0
    confidence: int = 0
    blockedBy: list[str] | None = None
    failedAt: Literal["Context", "Liquidity", "PremiumDiscount", "MSS", "Confluence", "Score", "Decision", "NONE"] = "NONE"
    criticalFailure: str = ""
    engineSequence: list[str] | None = None
    summary: str = ""

    @staticmethod
    def bootstrap(direction: DecisionDirection) -> "InstitutionalDecisionResult":
        return InstitutionalDecisionResult(
            engine="InstitutionalDecisionEngine",
            status=DecisionStatus.WAIT,
            score=Score(0),
            direction=direction,
            decisionState="INVALID",
            blockedBy=[],
            engineSequence=[],
        )
