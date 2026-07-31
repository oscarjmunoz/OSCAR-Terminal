from __future__ import annotations

from typing import Literal
from typing import TypedDict


class InstitutionalEntryZone(TypedDict):
    valid: bool
    direction: Literal["BULLISH", "BEARISH", "NONE"]
    entryZoneLow: float | None
    entryZoneHigh: float | None
    currentPrice: float
    inZone: bool
    discountForLong: bool
    premiumForShort: bool
    fvgConfluence: bool
    obConfluence: bool
    liquidityContextAligned: bool
    mssAligned: bool
    timeframeAligned: bool
    iezScore: int
    entryPriority: Literal["HIGH", "MEDIUM", "LOW", "NONE"]
    qualityScore: int
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]
