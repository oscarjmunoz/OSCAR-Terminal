from __future__ import annotations

from typing import Literal
from typing import TypedDict


class MSSResult(TypedDict):
    valid: bool
    direction: Literal["BULLISH", "BEARISH", "NONE"]
    brokenStructureLevel: float | None
    liquiditySweep: bool
    displacement: bool
    fvgCreated: bool
    biasAligned: bool
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]
