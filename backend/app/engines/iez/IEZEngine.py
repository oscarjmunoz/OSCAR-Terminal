from __future__ import annotations

import time
from typing import Literal
from typing import TypedDict

from app.core.DecisionNode import DecisionNode
from app.core.DecisionStatus import DecisionStatus
from app.core.DecisionTree import DecisionTree
from app.core.RuleResult import RuleResult
from app.core.Score import Score
from app.engines.iez.InstitutionalEntryZone import InstitutionalEntryZone
from app.rules.RuleRegistry import get_rule


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
        start = time.perf_counter()
        result = InstitutionalEntryZone.bootstrap(direction=data["direction"])

        failed_critical = False

        iez_001 = data["direction"] != "NONE"
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-001",
            condition=iez_001,
            pass_message="Directional context for entry zone is defined.",
            fail_message="Directional context for entry zone is undefined.",
            failed_critical=failed_critical,
        )

        zone_defined = data["entryZoneLow"] is not None and data["entryZoneHigh"] is not None
        iez_002 = zone_defined
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-002",
            condition=iez_002,
            pass_message="Entry zone boundaries are defined.",
            fail_message="Entry zone boundaries are missing.",
            failed_critical=failed_critical,
        )

        iez_003 = zone_defined and data["entryZoneHigh"] > data["entryZoneLow"]
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-003",
            condition=iez_003,
            pass_message="Entry zone range is structurally valid.",
            fail_message="Entry zone range is invalid.",
            failed_critical=failed_critical,
        )

        in_zone = IEZEngine._is_price_in_zone(
            current_price=data["currentPrice"],
            low=data["entryZoneLow"],
            high=data["entryZoneHigh"],
        )
        iez_004 = in_zone
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-004",
            condition=iez_004,
            pass_message="Current price is inside institutional entry zone.",
            fail_message="Current price is outside institutional entry zone.",
            failed_critical=failed_critical,
        )

        directional_location_aligned = IEZEngine._is_directional_location_aligned(
            direction=data["direction"],
            discount_for_long=data["discountForLong"],
            premium_for_short=data["premiumForShort"],
        )
        iez_005 = directional_location_aligned
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-005",
            condition=iez_005,
            pass_message="Directional location is aligned (discount for longs / premium for shorts).",
            fail_message="Directional location is not aligned.",
            failed_critical=failed_critical,
        )

        iez_006 = data["fvgConfluence"] and data["obConfluence"]
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-006",
            condition=iez_006,
            pass_message="FVG and Order Block confluence are confirmed.",
            fail_message="FVG or Order Block confluence is missing.",
            failed_critical=failed_critical,
        )

        iez_007 = data["liquidityContextAligned"] and data["mssAligned"] and data["timeframeAligned"]
        failed_critical = IEZEngine._register_rule(
            result=result,
            rule_id="IEZ-007",
            condition=iez_007,
            pass_message="Liquidity, MSS, and timeframe alignment are confirmed.",
            fail_message="Liquidity, MSS, or timeframe alignment is missing.",
            failed_critical=failed_critical,
        )

        passed_rule_ids = [rule_result.rule.id for rule_result in result.passedRules]
        iez_score = IEZEngine._calculate_iez_score(passed_rule_ids)
        is_valid = len(result.failedRules) == 0
        entry_priority = IEZEngine._resolve_entry_priority(iez_score=iez_score, valid=is_valid)
        quality_score = IEZEngine._calculate_quality_score(
            iez_score=iez_score,
            fvg_confluence=data["fvgConfluence"],
            ob_confluence=data["obConfluence"],
            directional_location_aligned=directional_location_aligned,
        )

        result.valid = is_valid
        result.direction = data["direction"]
        result.entryZoneLow = data["entryZoneLow"]
        result.entryZoneHigh = data["entryZoneHigh"]
        result.currentPrice = data["currentPrice"]
        result.inZone = in_zone
        result.discountForLong = data["discountForLong"]
        result.premiumForShort = data["premiumForShort"]
        result.fvgConfluence = data["fvgConfluence"]
        result.obConfluence = data["obConfluence"]
        result.liquidityContextAligned = data["liquidityContextAligned"]
        result.mssAligned = data["mssAligned"]
        result.timeframeAligned = data["timeframeAligned"]
        result.iezScore = iez_score
        result.entryPriority = entry_priority
        result.qualityScore = quality_score
        result.score = Score(iez_score)
        result.status = IEZEngine._resolve_status(is_valid=is_valid, failed_critical=failed_critical)
        result.executionTime = round((time.perf_counter() - start) * 1000, 4)

        return result

    @staticmethod
    def run(data: IEZInput, tree: DecisionTree | None = None) -> DecisionNode:
        result = IEZEngine.evaluate(data)
        node = DecisionNode.from_engine_result(result)

        if tree is not None:
            tree.add_node(node)
            tree.set_next_step("EntryEngine")

        return node

    @staticmethod
    def _register_rule(
        result: InstitutionalEntryZone,
        rule_id: str,
        condition: bool,
        pass_message: str,
        fail_message: str,
        failed_critical: bool,
    ) -> bool:
        rule = get_rule(rule_id)

        if condition:
            result.add_rule_result(
                RuleResult(
                    rule=rule,
                    status=DecisionStatus.PASS,
                    score=rule.weight,
                    reason=f"{rule_id}: {pass_message}",
                )
            )
            return failed_critical

        result.add_rule_result(
            RuleResult(
                rule=rule,
                status=DecisionStatus.FAIL if rule.critical else DecisionStatus.WARNING,
                score=0,
                warning=f"{rule_id}: {fail_message}",
            )
        )
        return failed_critical or rule.critical

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
    def _resolve_status(is_valid: bool, failed_critical: bool) -> DecisionStatus:
        if is_valid:
            return DecisionStatus.PASS

        if failed_critical:
            return DecisionStatus.FAIL

        return DecisionStatus.WARNING

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
