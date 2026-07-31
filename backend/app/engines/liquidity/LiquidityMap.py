from __future__ import annotations

from typing import Literal
from typing import TypedDict


class LiquidityLevel(TypedDict):
    name: Literal["PDH", "PDL", "PWH", "PWL", "H4_SWING_HIGH", "H4_SWING_LOW"]
    side: Literal["BSL", "SSL"]
    level: float
    distance: float
    taken: bool


class LiquidityTakenSummary(TypedDict):
    buySideTaken: list[str]
    sellSideTaken: list[str]


class LiquidityMap(TypedDict):
    pdh: LiquidityLevel
    pdl: LiquidityLevel
    pwh: LiquidityLevel
    pwl: LiquidityLevel
    h4SwingHigh: LiquidityLevel
    h4SwingLow: LiquidityLevel
    liquidityTaken: LiquidityTakenSummary
    nearestBuySideLiquidity: LiquidityLevel
    nearestSellSideLiquidity: LiquidityLevel
