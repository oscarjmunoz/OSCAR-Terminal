from __future__ import annotations

from typing import TypedDict

from app.engines.liquidity.LiquidityMap import LiquidityLevel
from app.engines.liquidity.LiquidityMap import LiquidityMap
from app.engines.liquidity.LiquidityMap import LiquidityTakenSummary


class H4Candle(TypedDict):
    high: float
    low: float


class LiquidityMapInput(TypedDict):
    currentPrice: float
    pdh: float
    pdl: float
    pwh: float
    pwl: float
    h4Candles: list[H4Candle]


class LiquidityMapEngine:

    @staticmethod
    def build(data: LiquidityMapInput) -> LiquidityMap:
        current_price = data["currentPrice"]

        h4_swing_high = LiquidityMapEngine._detect_h4_swing_high(data["h4Candles"])
        h4_swing_low = LiquidityMapEngine._detect_h4_swing_low(data["h4Candles"])

        pdh = LiquidityMapEngine._build_level("PDH", "BSL", data["pdh"], current_price)
        pdl = LiquidityMapEngine._build_level("PDL", "SSL", data["pdl"], current_price)
        pwh = LiquidityMapEngine._build_level("PWH", "BSL", data["pwh"], current_price)
        pwl = LiquidityMapEngine._build_level("PWL", "SSL", data["pwl"], current_price)
        h4_high = LiquidityMapEngine._build_level("H4_SWING_HIGH", "BSL", h4_swing_high, current_price)
        h4_low = LiquidityMapEngine._build_level("H4_SWING_LOW", "SSL", h4_swing_low, current_price)

        levels = [pdh, pdl, pwh, pwl, h4_high, h4_low]

        liquidity_taken: LiquidityTakenSummary = {
            "buySideTaken": [level["name"] for level in levels if level["side"] == "BSL" and level["taken"]],
            "sellSideTaken": [level["name"] for level in levels if level["side"] == "SSL" and level["taken"]],
        }

        nearest_buy_side = LiquidityMapEngine._nearest_buy_side_liquidity(levels, current_price)
        nearest_sell_side = LiquidityMapEngine._nearest_sell_side_liquidity(levels, current_price)

        return {
            "pdh": pdh,
            "pdl": pdl,
            "pwh": pwh,
            "pwl": pwl,
            "h4SwingHigh": h4_high,
            "h4SwingLow": h4_low,
            "liquidityTaken": liquidity_taken,
            "nearestBuySideLiquidity": nearest_buy_side,
            "nearestSellSideLiquidity": nearest_sell_side,
        }

    @staticmethod
    def _build_level(name: str, side: str, level: float, current_price: float) -> LiquidityLevel:
        if side == "BSL":
            taken = current_price >= level
        else:
            taken = current_price <= level

        return {
            "name": name,
            "side": side,
            "level": level,
            "distance": abs(level - current_price),
            "taken": taken,
        }

    @staticmethod
    def _detect_h4_swing_high(candles: list[H4Candle]) -> float:
        if not candles:
            return 0.0

        if len(candles) < 5:
            return max(candle["high"] for candle in candles)

        pivot_indices: list[int] = []

        for index in range(2, len(candles) - 2):
            center = candles[index]["high"]
            left = candles[index - 1]["high"]
            left2 = candles[index - 2]["high"]
            right = candles[index + 1]["high"]
            right2 = candles[index + 2]["high"]

            if center > left and center > left2 and center > right and center > right2:
                pivot_indices.append(index)

        if not pivot_indices:
            return max(candle["high"] for candle in candles)

        return candles[pivot_indices[-1]]["high"]

    @staticmethod
    def _detect_h4_swing_low(candles: list[H4Candle]) -> float:
        if not candles:
            return 0.0

        if len(candles) < 5:
            return min(candle["low"] for candle in candles)

        pivot_indices: list[int] = []

        for index in range(2, len(candles) - 2):
            center = candles[index]["low"]
            left = candles[index - 1]["low"]
            left2 = candles[index - 2]["low"]
            right = candles[index + 1]["low"]
            right2 = candles[index + 2]["low"]

            if center < left and center < left2 and center < right and center < right2:
                pivot_indices.append(index)

        if not pivot_indices:
            return min(candle["low"] for candle in candles)

        return candles[pivot_indices[-1]]["low"]

    @staticmethod
    def _nearest_buy_side_liquidity(levels: list[LiquidityLevel], current_price: float) -> LiquidityLevel:
        bsl_candidates = [level for level in levels if level["side"] == "BSL"]
        above_current = [level for level in bsl_candidates if level["level"] >= current_price and not level["taken"]]

        if above_current:
            return min(above_current, key=lambda level: level["level"] - current_price)

        return min(bsl_candidates, key=lambda level: abs(level["level"] - current_price))

    @staticmethod
    def _nearest_sell_side_liquidity(levels: list[LiquidityLevel], current_price: float) -> LiquidityLevel:
        ssl_candidates = [level for level in levels if level["side"] == "SSL"]
        below_current = [level for level in ssl_candidates if level["level"] <= current_price and not level["taken"]]

        if below_current:
            return min(below_current, key=lambda level: current_price - level["level"])

        return min(ssl_candidates, key=lambda level: abs(level["level"] - current_price))
