from __future__ import annotations

from app.engines.context.ContextResult import ContextResult
from app.engines.decision.PipelineModels import DecisionResult
from app.engines.decision.PipelineModels import ExecutionRecommendation
from app.engines.decision.PipelineModels import LiquidityResult
from app.engines.decision.PipelineModels import RiskResult
from app.engines.structure.MarketStructureResult import MarketStructureResult


class NarrativeEngine:
    """Builds a deterministic human-readable narrative for institutional decisions."""

    @staticmethod
    def build(
        *,
        liquidity: LiquidityResult,
        structure: MarketStructureResult,
        context: ContextResult,
        risk: RiskResult,
        decision: DecisionResult,
        recommendation: ExecutionRecommendation,
    ) -> str:
        steps: list[str] = []

        if liquidity.sweepSide == "SSL":
            steps.append("Sell-side liquidity sweep detected.")
        elif liquidity.sweepSide == "BSL":
            steps.append("Buy-side liquidity sweep detected.")
        else:
            steps.append("No liquidity sweep detected.")

        if structure["bos"]:
            steps.append(f"{structure['breakDirection'].title()} BOS confirmed.")
        elif structure["choch"]:
            steps.append(f"{structure['breakDirection'].title()} CHOCH confirmed.")
        else:
            steps.append("No structural break confirmation.")

        if context["orderBlock"]["valid"] and context["fairValueGap"]["valid"]:
            steps.append("Order block and fair value gap confirmations are aligned.")
        else:
            steps.append("Institutional context is incomplete.")

        if risk.valid:
            steps.append("Risk acceptable.")
        else:
            steps.append("Risk constraints not satisfied.")

        steps.append(f"Institutional score {decision.institutionalScore}.")
        steps.append(f"Confidence {decision.confidence}.")
        steps.append(f"Recommendation {recommendation.action}.")

        return " ".join(steps)
