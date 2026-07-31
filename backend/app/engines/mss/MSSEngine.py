from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.engines.mss.MSSResult import MSSResult


class MSSInput(TypedDict):
    direction: Literal["BULLISH", "BEARISH", "NONE"]
    brokenStructureLevel: float | None
    liquiditySweep: bool
    displacement: bool
    fvgCreated: bool
    biasAligned: bool
    sweepSide: Literal["BSL", "SSL", "NONE"]


class MSSEngine:

    @staticmethod
    def evaluate(data: MSSInput) -> MSSResult:
        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        mss_001 = data["direction"] != "NONE" and data["brokenStructureLevel"] is not None
        MSSEngine._register_rule(
            rule_id="MSS-001",
            condition=mss_001,
            pass_message="Market structure shift break is confirmed.",
            fail_message="Missing direction or broken structure level.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        mss_002 = data["liquiditySweep"]
        MSSEngine._register_rule(
            rule_id="MSS-002",
            condition=mss_002,
            pass_message="Liquidity sweep is confirmed.",
            fail_message="Liquidity sweep is not confirmed.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        mss_003 = data["displacement"]
        MSSEngine._register_rule(
            rule_id="MSS-003",
            condition=mss_003,
            pass_message="Displacement candle behavior is confirmed.",
            fail_message="Displacement candle behavior is missing.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        mss_004 = data["fvgCreated"]
        MSSEngine._register_rule(
            rule_id="MSS-004",
            condition=mss_004,
            pass_message="A fair value gap was created after shift.",
            fail_message="No fair value gap was created after shift.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        mss_005 = data["biasAligned"]
        MSSEngine._register_rule(
            rule_id="MSS-005",
            condition=mss_005,
            pass_message="Directional bias is aligned with MSS.",
            fail_message="Directional bias is not aligned with MSS.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        mss_006 = MSSEngine._is_sweep_direction_aligned(
            direction=data["direction"],
            sweep_side=data["sweepSide"],
        )
        MSSEngine._register_rule(
            rule_id="MSS-006",
            condition=mss_006,
            pass_message="Sweep side is coherent with MSS direction.",
            fail_message="Sweep side is not coherent with MSS direction.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        return {
            "valid": len(failed_rules) == 0,
            "direction": data["direction"],
            "brokenStructureLevel": data["brokenStructureLevel"],
            "liquiditySweep": data["liquiditySweep"],
            "displacement": data["displacement"],
            "fvgCreated": data["fvgCreated"],
            "biasAligned": data["biasAligned"],
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
    def _is_sweep_direction_aligned(
        direction: Literal["BULLISH", "BEARISH", "NONE"],
        sweep_side: Literal["BSL", "SSL", "NONE"],
    ) -> bool:
        if direction == "BULLISH":
            return sweep_side == "SSL"

        if direction == "BEARISH":
            return sweep_side == "BSL"

        return False
