from __future__ import annotations

from app.config.settings import settings
from app.engines.context.ContextResult import ContextResult
from app.engines.decision.ConfluenceEngine import ConfluenceResult
from app.engines.decision.PipelineModels import Bias
from app.engines.decision.PipelineModels import RiskResult
from app.engines.mss.MSSResult import MSSResult
from app.engines.premium_discount.PremiumDiscountResult import PremiumDiscountResult
from app.engines.structure.MarketStructureResult import MarketStructureResult


class ConfidenceEngine:
    """Computes confidence independently from score with configurable weighted factors."""

    @staticmethod
    def evaluate(
        *,
        bias: Bias,
        structure: MarketStructureResult,
        mss: MSSResult,
        context: ContextResult,
        premium_discount: PremiumDiscountResult,
        confluence: ConfluenceResult,
        risk: RiskResult,
        warnings: tuple[str, ...],
    ) -> int:
        confluence_factor = ConfidenceEngine._confluence_factor(structure, mss, confluence, risk)
        contradiction_factor = ConfidenceEngine._contradiction_factor(warnings)
        context_quality_factor = context["contextScore"]
        consistency_factor = ConfidenceEngine._consistency_factor(bias, structure, mss, premium_discount)

        weights_sum = (
            settings.CONFIDENCE_WEIGHT_CONFLUENCE
            + settings.CONFIDENCE_WEIGHT_CONTRADICTION
            + settings.CONFIDENCE_WEIGHT_CONTEXT_QUALITY
            + settings.CONFIDENCE_WEIGHT_ENGINE_CONSISTENCY
        )

        weighted = (
            confluence_factor * settings.CONFIDENCE_WEIGHT_CONFLUENCE
            + contradiction_factor * settings.CONFIDENCE_WEIGHT_CONTRADICTION
            + context_quality_factor * settings.CONFIDENCE_WEIGHT_CONTEXT_QUALITY
            + consistency_factor * settings.CONFIDENCE_WEIGHT_ENGINE_CONSISTENCY
        )

        return max(0, min(100, int(round(weighted / max(1, weights_sum)))))

    @staticmethod
    def _confluence_factor(
        structure: MarketStructureResult,
        mss: MSSResult,
        confluence: ConfluenceResult,
        risk: RiskResult,
    ) -> int:
        checks = [
            structure["valid"],
            mss["valid"],
            confluence["valid"],
            confluence["inInstitutionalZone"],
            risk.valid,
        ]
        return int(round(100 * (sum(bool(item) for item in checks) / len(checks))))

    @staticmethod
    def _contradiction_factor(warnings: tuple[str, ...]) -> int:
        contradiction_hits = sum(1 for warning in warnings if "contradict" in warning.lower())
        if contradiction_hits == 0:
            return 100
        penalty = min(90, contradiction_hits * 45)
        return max(0, 100 - penalty)

    @staticmethod
    def _consistency_factor(
        bias: Bias,
        structure: MarketStructureResult,
        mss: MSSResult,
        premium_discount: PremiumDiscountResult,
    ) -> int:
        checks = [
            structure["breakDirection"] == mss["direction"] and structure["breakDirection"] != "NONE",
            premium_discount["biasAligned"],
            (bias == "NEUTRAL") or (structure["breakDirection"] == bias),
            structure["timeframeAligned"],
        ]
        return int(round(100 * (sum(bool(item) for item in checks) / len(checks))))
