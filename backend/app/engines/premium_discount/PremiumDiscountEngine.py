from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.engines.premium_discount.PremiumDiscountResult import PremiumDiscountResult


class PremiumDiscountInput(TypedDict):
    currentPrice: float
    rangeHigh: float
    rangeLow: float
    bias: Literal["BULLISH", "BEARISH", "NEUTRAL"]


class PremiumDiscountEngine:

    @staticmethod
    def evaluate(data: PremiumDiscountInput) -> PremiumDiscountResult:
        current_price = data["currentPrice"]
        range_high = data["rangeHigh"]
        range_low = data["rangeLow"]

        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        pd_001 = range_high > range_low
        PremiumDiscountEngine._register_rule(
            rule_id="PD-001",
            condition=pd_001,
            pass_message="Dealing range is structurally valid.",
            fail_message="Range high must be greater than range low.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        equilibrium = (range_high + range_low) / 2
        pd_002 = pd_001 and range_low <= current_price <= range_high
        PremiumDiscountEngine._register_rule(
            rule_id="PD-002",
            condition=pd_002,
            pass_message="Current price is inside the dealing range.",
            fail_message="Current price is outside the dealing range.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        zone = PremiumDiscountEngine._resolve_zone(
            current_price=current_price,
            equilibrium=equilibrium,
            range_high=range_high,
            range_low=range_low,
            range_is_valid=pd_001,
        )
        pd_003 = zone in {"PREMIUM", "DISCOUNT", "EQUILIBRIUM"}
        PremiumDiscountEngine._register_rule(
            rule_id="PD-003",
            condition=pd_003,
            pass_message="Premium/Discount zone classification is available.",
            fail_message="Premium/Discount zone classification is not available.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        in_premium = zone == "PREMIUM"
        in_discount = zone == "DISCOUNT"
        in_equilibrium = zone == "EQUILIBRIUM"

        active_flags = int(in_premium) + int(in_discount) + int(in_equilibrium)
        pd_004 = active_flags == 1
        PremiumDiscountEngine._register_rule(
            rule_id="PD-004",
            condition=pd_004,
            pass_message="Zone boolean flags are mutually exclusive and coherent.",
            fail_message="Zone boolean flags are not coherent.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        bias_aligned = PremiumDiscountEngine._is_bias_aligned(
            bias=data["bias"],
            zone=zone,
        )
        pd_005 = bias_aligned
        PremiumDiscountEngine._register_rule(
            rule_id="PD-005",
            condition=pd_005,
            pass_message="Bias is aligned with premium/discount location.",
            fail_message="Bias is not aligned with premium/discount location.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        return {
            "valid": len(failed_rules) == 0,
            "zone": zone,
            "currentPrice": current_price,
            "rangeHigh": range_high,
            "rangeLow": range_low,
            "equilibrium": equilibrium,
            "distanceToEquilibrium": abs(current_price - equilibrium),
            "inPremium": in_premium,
            "inDiscount": in_discount,
            "inEquilibrium": in_equilibrium,
            "biasAligned": bias_aligned,
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
    def _resolve_zone(
        current_price: float,
        equilibrium: float,
        range_high: float,
        range_low: float,
        range_is_valid: bool,
    ) -> Literal["PREMIUM", "DISCOUNT", "EQUILIBRIUM", "UNKNOWN"]:
        if not range_is_valid:
            return "UNKNOWN"

        half_range = (range_high - range_low) / 2
        equilibrium_threshold = max(half_range * 0.1, 1e-9)

        if abs(current_price - equilibrium) <= equilibrium_threshold:
            return "EQUILIBRIUM"

        if current_price > equilibrium:
            return "PREMIUM"

        return "DISCOUNT"

    @staticmethod
    def _is_bias_aligned(
        bias: Literal["BULLISH", "BEARISH", "NEUTRAL"],
        zone: Literal["PREMIUM", "DISCOUNT", "EQUILIBRIUM", "UNKNOWN"],
    ) -> bool:
        if zone == "UNKNOWN":
            return False

        if bias == "BULLISH":
            return zone in {"DISCOUNT", "EQUILIBRIUM"}

        if bias == "BEARISH":
            return zone in {"PREMIUM", "EQUILIBRIUM"}

        return True
