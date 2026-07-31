from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.DecisionStatus import DecisionStatus
from app.core.EngineResult import EngineResult
from app.core.Score import Score


@dataclass(slots=True)
class InstitutionalEntryZone(EngineResult):
    valid: bool = False
    direction: Literal["BULLISH", "BEARISH", "NONE"] = "NONE"
    entryZoneLow: float | None = None
    entryZoneHigh: float | None = None
    currentPrice: float = 0.0
    inZone: bool = False
    discountForLong: bool = False
    premiumForShort: bool = False
    fvgConfluence: bool = False
    obConfluence: bool = False
    liquidityContextAligned: bool = False
    mssAligned: bool = False
    timeframeAligned: bool = False
    iezScore: int = 0
    entryPriority: Literal["HIGH", "MEDIUM", "LOW", "NONE"] = "NONE"
    qualityScore: int = 0

    @staticmethod
    def bootstrap(direction: Literal["BULLISH", "BEARISH", "NONE"]) -> "InstitutionalEntryZone":
        return InstitutionalEntryZone(
            engine="IEZEngine",
            status=DecisionStatus.WAIT,
            score=Score(0),
            direction=direction,
            entryPriority="NONE",
        )
