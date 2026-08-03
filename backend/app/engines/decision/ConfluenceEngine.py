from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.engines.context.ContextResult import ContextResult
from app.engines.mss.MSSResult import MSSResult
from app.engines.premium_discount.PremiumDiscountResult import PremiumDiscountResult
from app.engines.structure.MarketStructureResult import MarketStructureResult


class ConfluenceResult(TypedDict):
    valid: bool
    direction: Literal["BULLISH", "BEARISH", "NONE"]
    inInstitutionalZone: bool
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]


class ConfluenceEngine:
    """Deterministic confluence engine used by the institutional pipeline."""

    @staticmethod
    def evaluate(
        structure: MarketStructureResult,
        mss: MSSResult,
        context: ContextResult,
        premium_discount: PremiumDiscountResult,
    ) -> ConfluenceResult:
        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        direction = ConfluenceEngine._resolve_direction(
            structure_direction=structure["breakDirection"],
            mss_direction=mss["direction"],
        )

        conf_001 = structure["valid"] and mss["valid"]
        ConfluenceEngine._register_rule(
            "CONF-001",
            conf_001,
            "Structure and MSS validations are available.",
            "Structure or MSS validation failed.",
            passed_rules,
            failed_rules,
            reasons,
            warnings,
        )

        conf_002 = context["orderBlock"]["valid"] and context["fairValueGap"]["valid"]
        ConfluenceEngine._register_rule(
            "CONF-002",
            conf_002,
            "Order block and fair value gap confirmations are valid.",
            "Order block or fair value gap confirmation is missing.",
            passed_rules,
            failed_rules,
            reasons,
            warnings,
        )

        in_institutional_zone = premium_discount["zone"] in {"PREMIUM", "DISCOUNT", "EQUILIBRIUM"}
        conf_003 = in_institutional_zone
        ConfluenceEngine._register_rule(
            "CONF-003",
            conf_003,
            "Price is in an institutional zone.",
            "Price is not in a valid institutional zone.",
            passed_rules,
            failed_rules,
            reasons,
            warnings,
        )

        conf_004 = direction != "NONE"
        ConfluenceEngine._register_rule(
            "CONF-004",
            conf_004,
            "Directional confluence is resolved.",
            "Directional confluence is unresolved.",
            passed_rules,
            failed_rules,
            reasons,
            warnings,
        )

        return {
            "valid": len(failed_rules) == 0,
            "direction": direction,
            "inInstitutionalZone": in_institutional_zone,
            "passedRules": passed_rules,
            "failedRules": failed_rules,
            "reasons": reasons,
            "warnings": warnings,
        }

    @staticmethod
    def _resolve_direction(
        structure_direction: Literal["BULLISH", "BEARISH", "NONE"],
        mss_direction: Literal["BULLISH", "BEARISH", "NONE"],
    ) -> Literal["BULLISH", "BEARISH", "NONE"]:
        if structure_direction == mss_direction:
            return structure_direction

        if mss_direction in {"BULLISH", "BEARISH"}:
            return mss_direction

        if structure_direction in {"BULLISH", "BEARISH"}:
            return structure_direction

        return "NONE"

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
