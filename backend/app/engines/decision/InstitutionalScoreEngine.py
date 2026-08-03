from __future__ import annotations

from typing import Literal
from typing import TypedDict

from app.config.settings import settings
from app.engines.context.ContextResult import ContextResult
from app.engines.decision.PipelineModels import Bias
from app.engines.decision.PipelineModels import RiskResult
from app.engines.mss.MSSResult import MSSResult
from app.engines.premium_discount.PremiumDiscountResult import PremiumDiscountResult
from app.engines.structure.MarketStructureResult import MarketStructureResult


class ScoreResult(TypedDict):
    valid: bool
    institutionalScore: int
    confidence: int
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]


class InstitutionalScoreEngine:
    """Weighted institutional score calculator with configurable components."""

    @staticmethod
    def evaluate(
        *,
        bias: Bias,
        session: str,
        liquidity_valid: bool,
        structure: MarketStructureResult,
        mss: MSSResult,
        context: ContextResult,
        premium_discount: PremiumDiscountResult,
        risk: RiskResult,
        confidence: int,
    ) -> ScoreResult:
        components = {
            "liquidity": 100 if liquidity_valid else 0,
            "structure": 100 if structure["valid"] and mss["valid"] else 0,
            "bias": 100 if InstitutionalScoreEngine._is_bias_coherent(bias, structure["breakDirection"], premium_discount["biasAligned"]) else 0,
            "order_blocks": 100 if context["orderBlock"]["valid"] else 0,
            "fvg": 100 if context["fairValueGap"]["valid"] and mss["fvgCreated"] else 0,
            "risk": risk.riskScore,
            "session": 100 if risk.sessionAllowed and session != "OFF_HOURS" else 0,
        }

        weights = {
            "liquidity": settings.SCORE_WEIGHT_LIQUIDITY,
            "structure": settings.SCORE_WEIGHT_STRUCTURE,
            "bias": settings.SCORE_WEIGHT_BIAS,
            "order_blocks": settings.SCORE_WEIGHT_ORDER_BLOCKS,
            "fvg": settings.SCORE_WEIGHT_FVG,
            "risk": settings.SCORE_WEIGHT_RISK,
            "session": settings.SCORE_WEIGHT_SESSION,
        }

        weighted_total = 0.0
        total_weight = 0
        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        rule_map = {
            "liquidity": "SCR-001",
            "structure": "SCR-002",
            "bias": "SCR-003",
            "order_blocks": "SCR-004",
            "fvg": "SCR-005",
            "risk": "SCR-006",
            "session": "SCR-007",
        }

        for component_name, component_value in components.items():
            weight = weights[component_name]
            weighted_total += component_value * weight
            total_weight += weight

            rule_id = rule_map[component_name]
            if component_value >= 60:
                passed_rules.append(rule_id)
                reasons.append(f"{rule_id}: {component_name} component is valid ({component_value}).")
            else:
                failed_rules.append(rule_id)
                warnings.append(f"{rule_id}: {component_name} component is weak ({component_value}).")

        normalized_score = int(round(weighted_total / max(1, total_weight)))

        return {
            "valid": normalized_score >= settings.DECISION_MIN_SCORE,
            "institutionalScore": max(0, min(100, normalized_score)),
            "confidence": confidence,
            "passedRules": passed_rules,
            "failedRules": failed_rules,
            "reasons": reasons,
            "warnings": warnings,
        }

    @staticmethod
    def _is_bias_coherent(
        bias: Bias,
        break_direction: Literal["BULLISH", "BEARISH", "NONE"],
        premium_bias_aligned: bool,
    ) -> bool:
        if not premium_bias_aligned:
            return False

        if bias == "NEUTRAL":
            return break_direction in {"BULLISH", "BEARISH"}

        if bias == "BULLISH":
            return break_direction == "BULLISH"

        return break_direction == "BEARISH"
