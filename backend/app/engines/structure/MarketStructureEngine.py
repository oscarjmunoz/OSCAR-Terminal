from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.engines.structure.MarketStructureResult import MarketStructureResult


class MarketStructureInput(TypedDict):
    trend: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"]
    breakDirection: Literal["BULLISH", "BEARISH", "NONE"]
    swingHigh: float | None
    swingLow: float | None
    bos: bool
    choch: bool
    liquiditySweep: bool
    displacement: bool
    timeframeAligned: bool
    swingImportance: Literal["MAJOR", "MINOR", "INTERNAL"]


class MarketStructureEngine:

    @staticmethod
    def evaluate(data: MarketStructureInput) -> MarketStructureResult:
        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        str_001 = data["trend"] != "UNKNOWN"
        MarketStructureEngine._register_rule(
            rule_id="STR-001",
            condition=str_001,
            pass_message="Trend context is available.",
            fail_message="Trend context is unknown.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_002 = data["swingHigh"] is not None and data["swingLow"] is not None
        MarketStructureEngine._register_rule(
            rule_id="STR-002",
            condition=str_002,
            pass_message="Swing high and swing low are present.",
            fail_message="Swing high or swing low is missing.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_003 = data["swingImportance"] in {"MAJOR", "MINOR", "INTERNAL"}
        MarketStructureEngine._register_rule(
            rule_id="STR-003",
            condition=str_003,
            pass_message="Swing importance classification is valid.",
            fail_message="Swing importance classification is invalid.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_004 = str_002 and data["swingHigh"] > data["swingLow"]
        MarketStructureEngine._register_rule(
            rule_id="STR-004",
            condition=str_004,
            pass_message="Swing range is structurally coherent.",
            fail_message="Swing range is not coherent (high must be above low).",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_005 = data["bos"] or data["choch"]
        MarketStructureEngine._register_rule(
            rule_id="STR-005",
            condition=str_005,
            pass_message="At least one structural break event is confirmed.",
            fail_message="No BOS or CHOCH event is confirmed.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_006 = MarketStructureEngine._is_break_direction_coherent(
            trend=data["trend"],
            break_direction=data["breakDirection"],
        )
        MarketStructureEngine._register_rule(
            rule_id="STR-006",
            condition=str_006,
            pass_message="Break direction is coherent with trend context.",
            fail_message="Break direction is not coherent with trend context.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_007 = data["liquiditySweep"] and data["displacement"]
        MarketStructureEngine._register_rule(
            rule_id="STR-007",
            condition=str_007,
            pass_message="Liquidity sweep and displacement are confirmed.",
            fail_message="Liquidity sweep or displacement is missing.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        str_008 = data["timeframeAligned"]
        MarketStructureEngine._register_rule(
            rule_id="STR-008",
            condition=str_008,
            pass_message="Timeframe alignment is confirmed.",
            fail_message="Timeframe alignment is not confirmed.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        return {
            "valid": len(failed_rules) == 0,
            "trend": data["trend"],
            "breakDirection": data["breakDirection"],
            "swingHigh": data["swingHigh"],
            "swingLow": data["swingLow"],
            "bos": data["bos"],
            "choch": data["choch"],
            "mss": data["choch"] and data["displacement"],
            "liquiditySweep": data["liquiditySweep"],
            "displacement": data["displacement"],
            "timeframeAligned": data["timeframeAligned"],
            "swingImportance": data["swingImportance"],
            "passedRules": passed_rules,
            "failedRules": failed_rules,
            "reasons": reasons,
            "warnings": warnings,
        }

    @staticmethod
    def _register_rule(
        rule_id: str,
        condition: bool,
        pass_message: str,
        fail_message: str,
        passed_rules: list[str],
        failed_rules: list[str],
        reasons: list[str],
        warnings: list[str],
    ) -> None:
        if condition:
            passed_rules.append(rule_id)
            reasons.append(f"{rule_id}: {pass_message}")
            return

        failed_rules.append(rule_id)
        warnings.append(f"{rule_id}: {fail_message}")

    @staticmethod
    def _is_break_direction_coherent(
        trend: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"],
        break_direction: Literal["BULLISH", "BEARISH", "NONE"],
    ) -> bool:
        if trend == "BULLISH":
            return break_direction == "BULLISH"

        if trend == "BEARISH":
            return break_direction == "BEARISH"

        if trend == "RANGE":
            return break_direction in {"BULLISH", "BEARISH"}

        return False
