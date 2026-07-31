from __future__ import annotations

from typing import Literal
from typing import TypedDict


class MarketStructureResult(TypedDict):
    valid: bool
    trend: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"]
    breakDirection: Literal["BULLISH", "BEARISH", "NONE"]
    swingHigh: float | None
    swingLow: float | None
    bos: bool
    choch: bool
    mss: bool
    liquiditySweep: bool
    displacement: bool
    timeframeAligned: bool
    swingImportance: Literal["MAJOR", "MINOR", "INTERNAL"]
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]
