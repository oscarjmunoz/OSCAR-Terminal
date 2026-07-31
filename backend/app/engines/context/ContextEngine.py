from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.engines.context.ContextResult import ContextFairValueGap
from app.engines.context.ContextResult import ContextLiquidityTaken
from app.engines.context.ContextResult import ContextOrderBlock
from app.engines.context.ContextResult import ContextResult


class ContextEngineInputLiquidity(TypedDict):
    timeframe: str
    side: Literal["BSL", "SSL", "NONE"]
    level: float | None
    taken: bool


class ContextEngineInputOrderBlock(TypedDict):
    timeframe: str
    blockType: Literal["BULLISH", "BEARISH", "NONE"]
    low: float | None
    high: float | None
    present: bool


class ContextEngineInputFairValueGap(TypedDict):
    timeframe: str
    gapType: Literal["BULLISH", "BEARISH", "NONE"]
    low: float | None
    high: float | None
    present: bool


class ContextEngine:

    @staticmethod
    def evaluate(
        liquidity: ContextEngineInputLiquidity,
        order_block: ContextEngineInputOrderBlock,
        fair_value_gap: ContextEngineInputFairValueGap,
    ) -> ContextResult:
        liquidity_valid = liquidity["timeframe"] == "H4" and liquidity["taken"]
        order_block_valid = order_block["timeframe"] == "H1" and order_block["present"]
        fair_value_gap_valid = fair_value_gap["timeframe"] == "H1" and fair_value_gap["present"]

        reasons: list[str] = []
        warnings: list[str] = []

        if liquidity_valid:
            reasons.append("H4 liquidity sweep validated.")
        else:
            warnings.append("H4 liquidity sweep is missing or invalid timeframe.")

        if order_block_valid:
            reasons.append("H1 order block validated.")
        else:
            warnings.append("H1 order block is missing or invalid timeframe.")

        if fair_value_gap_valid:
            reasons.append("H1 fair value gap validated.")
        else:
            warnings.append("H1 fair value gap is missing or invalid timeframe.")

        context_score = 0

        if liquidity_valid:
            context_score += 34
        if order_block_valid:
            context_score += 33
        if fair_value_gap_valid:
            context_score += 33

        normalized_liquidity: ContextLiquidityTaken = {
            "timeframe": "H4",
            "valid": liquidity_valid,
            "side": liquidity["side"],
            "level": liquidity["level"],
        }

        normalized_order_block: ContextOrderBlock = {
            "timeframe": "H1",
            "valid": order_block_valid,
            "blockType": order_block["blockType"],
            "low": order_block["low"],
            "high": order_block["high"],
        }

        normalized_fair_value_gap: ContextFairValueGap = {
            "timeframe": "H1",
            "valid": fair_value_gap_valid,
            "gapType": fair_value_gap["gapType"],
            "low": fair_value_gap["low"],
            "high": fair_value_gap["high"],
        }

        return {
            "valid": liquidity_valid and order_block_valid and fair_value_gap_valid,
            "contextScore": context_score,
            "reasons": reasons,
            "warnings": warnings,
            "liquidityTaken": normalized_liquidity,
            "orderBlock": normalized_order_block,
            "fairValueGap": normalized_fair_value_gap,
        }
