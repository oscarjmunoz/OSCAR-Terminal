from __future__ import annotations

from app.config.settings import settings
from app.engines.context.ContextResult import ContextResult
from app.engines.decision.PipelineModels import Bias
from app.engines.decision.PipelineModels import LiquidityResult
from app.engines.decision.PipelineModels import RiskResult
from app.engines.mss.MSSResult import MSSResult
from app.engines.structure.MarketStructureResult import MarketStructureResult


class InstitutionalValidationEngine:
    """Conflict detector that emits deterministic warnings for the institutional pipeline."""

    @staticmethod
    def evaluate(
        *,
        bias: Bias,
        liquidity: LiquidityResult,
        structure: MarketStructureResult,
        mss: MSSResult,
        context: ContextResult,
        risk: RiskResult,
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        if bias == "BULLISH" and liquidity.sweepSide == "BSL":
            warnings.append("Contradiction: bullish bias with bearish liquidity sweep side.")

        if bias == "BEARISH" and liquidity.sweepSide == "SSL":
            warnings.append("Contradiction: bearish bias with bullish liquidity sweep side.")

        if risk.riskPercent > settings.RISK_MAX_PERCENT or risk.exposurePercent > settings.RISK_MAX_EXPOSURE_PERCENT:
            warnings.append("Risk warning: configured risk limits are exceeded.")

        if not liquidity.valid:
            warnings.append("Liquidity warning: required liquidity map levels are missing.")

        if structure["breakDirection"] != "NONE" and mss["direction"] != "NONE" and structure["breakDirection"] != mss["direction"]:
            warnings.append("Contradiction: structure direction and MSS direction are not consistent.")

        if not context["valid"]:
            warnings.append("Context warning: institutional context validations are incomplete.")

        return tuple(warnings)
