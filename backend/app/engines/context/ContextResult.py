from __future__ import annotations

from typing import Literal
from typing import TypedDict


class ContextLiquidityTaken(TypedDict):
    timeframe: Literal["H4"]
    valid: bool
    side: Literal["BSL", "SSL", "NONE"]
    level: float | None


class ContextOrderBlock(TypedDict):
    timeframe: Literal["H1"]
    valid: bool
    blockType: Literal["BULLISH", "BEARISH", "NONE"]
    low: float | None
    high: float | None


class ContextFairValueGap(TypedDict):
    timeframe: Literal["H1"]
    valid: bool
    gapType: Literal["BULLISH", "BEARISH", "NONE"]
    low: float | None
    high: float | None


class ContextResult(TypedDict):
    valid: bool
    contextScore: int
    reasons: list[str]
    warnings: list[str]
    liquidityTaken: ContextLiquidityTaken
    orderBlock: ContextOrderBlock
    fairValueGap: ContextFairValueGap
