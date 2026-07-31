from __future__ import annotations

from typing import Literal
from typing import TypedDict


class PremiumDiscountResult(TypedDict):
    valid: bool
    zone: Literal["PREMIUM", "DISCOUNT", "EQUILIBRIUM", "UNKNOWN"]
    currentPrice: float
    rangeHigh: float
    rangeLow: float
    equilibrium: float
    distanceToEquilibrium: float
    inPremium: bool
    inDiscount: bool
    inEquilibrium: bool
    biasAligned: bool
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]
