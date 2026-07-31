from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.engines.iez.InstitutionalEntryZone import InstitutionalEntryZone


class IEZInput(TypedDict):
    direction: Literal["BULLISH", "BEARISH", "NONE"]
    entryZoneLow: float | None
    entryZoneHigh: float | None
    currentPrice: float
    discountForLong: bool
    premiumForShort: bool
    fvgConfluence: bool
    obConfluence: bool
    liquidityContextAligned: bool
    mssAligned: bool
    timeframeAligned: bool


class IEZEngine:

    @staticmethod
    def evaluate(data: IEZInput) -> InstitutionalEntryZone:
        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        iez_001 = data["direction"] != "NONE"
        IEZEngine._register_rule(
            rule_id="IEZ-001",
            condition=iez_001,
            pass_message="Directional context for entry zone is defined.",
            fail_message="Directional context for entry zone is undefined.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        zone_defined = data["entryZoneLow"] is not None and data["entryZoneHigh"] is not None
        iez_002 = zone_defined
        IEZEngine._register_rule(
            rule_id="IEZ-002",
            condition=iez_002,
            pass_message="Entry zone boundaries are defined.",
            fail_message="Entry zone boundaries are missing.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        iez_003 = zone_defined and data["entryZoneHigh"] > data["entryZoneLow"]
        IEZEngine._register_rule(
            rule_id="IEZ-003",
            condition=iez_003,
            pass_message="Entry zone range is structurally valid.",
            fail_message="Entry zone range is invalid.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        in_zone = IEZEngine._is_price_in_zone(
            current_price=data["currentPrice"],
            low=data["entryZoneLow"],
            high=data["entryZoneHigh"],
        )
        iez_004 = in_zone
        IEZEngine._register_rule(
            rule_id="IEZ-004",
            condition=iez_004,
            pass_message="Current price is inside institutional entry zone.",
            fail_message="Current price is outside institutional entry zone.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        directional_location_aligned = IEZEngine._is_directional_location_aligned(
            direction=data["direction"],
            discount_for_long=data["discountForLong"],
            premium_for_short=data["premiumForShort"],
        )
        iez_005 = directional_location_aligned
        IEZEngine._register_rule(
            rule_id="IEZ-005",
            condition=iez_005,
            pass_message="Directional location is aligned (discount for longs / premium for shorts).",
            fail_message="Directional location is not aligned.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        iez_006 = data["fvgConfluence"] and data["obConfluence"]
        IEZEngine._register_rule(
            rule_id="IEZ-006",
            condition=iez_006,
            pass_message="FVG and Order Block confluence are confirmed.",
            fail_message="FVG or Order Block confluence is missing.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        iez_007 = data["liquidityContextAligned"] and data["mssAligned"] and data["timeframeAligned"]
        IEZEngine._register_rule(
            rule_id="IEZ-007",
            condition=iez_007,
            pass_message="Liquidity, MSS, and timeframe alignment are confirmed.",
            fail_message="Liquidity, MSS, or timeframe alignment is missing.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        iez_score = IEZEngine._calculate_iez_score(passed_rules)
        entry_priority = IEZEngine._resolve_entry_priority(iez_score=iez_score, valid=len(failed_rules) == 0)
        quality_score = IEZEngine._calculate_quality_score(
            iez_score=iez_score,
            fvg_confluence=data["fvgConfluence"],
            ob_confluence=data["obConfluence"],
            directional_location_aligned=directional_location_aligned,
        )

        return {
            "valid": len(failed_rules) == 0,
            "direction": data["direction"],
            "entryZoneLow": data["entryZoneLow"],
            "entryZoneHigh": data["entryZoneHigh"],
            "currentPrice": data["currentPrice"],
            "inZone": in_zone,
            "discountForLong": data["discountForLong"],
            "premiumForShort": data["premiumForShort"],
            "fvgConfluence": data["fvgConfluence"],
            "obConfluence": data["obConfluence"],
            "liquidityContextAligned": data["liquidityContextAligned"],
            "mssAligned": data["mssAligned"],
            "timeframeAligned": data["timeframeAligned"],
            "iezScore": iez_score,
            "entryPriority": entry_priority,
            "qualityScore": quality_score,
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
    def _is_price_in_zone(current_price: float, low: float | None, high: float | None) -> bool:
        if low is None or high is None:
            return False

        return low <= current_price <= high

    @staticmethod
    def _is_directional_location_aligned(
        direction: Literal["BULLISH", "BEARISH", "NONE"],
        discount_for_long: bool,
        premium_for_short: bool,
    ) -> bool:
        if direction == "BULLISH":
            return discount_for_long

        if direction == "BEARISH":
            return premium_for_short

        return False

    @staticmethod
    def _calculate_iez_score(passed_rules: list[str]) -> int:
        return int(round((len(passed_rules) / 7) * 100))

    @staticmethod
    def _resolve_entry_priority(
        iez_score: int,
        valid: bool,
    ) -> Literal["HIGH", "MEDIUM", "LOW", "NONE"]:
        if not valid:
            if iez_score >= 70:
                return "LOW"
            return "NONE"

        if iez_score >= 90:
            return "HIGH"

        if iez_score >= 75:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _calculate_quality_score(
        iez_score: int,
        fvg_confluence: bool,
        ob_confluence: bool,
        directional_location_aligned: bool,
    ) -> int:
        bonus = 0

        if fvg_confluence:
            bonus += 4
        if ob_confluence:
            bonus += 4
        if directional_location_aligned:
            bonus += 2

        return min(100, iez_score + bonus)
