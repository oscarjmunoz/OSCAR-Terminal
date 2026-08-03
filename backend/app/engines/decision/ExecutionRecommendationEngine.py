from __future__ import annotations

from app.config.settings import settings
from app.engines.decision.PipelineModels import DecisionResult
from app.engines.decision.PipelineModels import ExecutionRecommendation
from app.engines.decision.PipelineModels import RiskResult


class ExecutionRecommendationEngine:
    """Maps decision outputs into executable deterministic trade recommendations."""

    @staticmethod
    def evaluate(
        *,
        decision: DecisionResult,
        risk: RiskResult,
        warnings: tuple[str, ...],
    ) -> ExecutionRecommendation:
        has_contradiction = any("contradiction" in warning.lower() for warning in warnings)

        if not risk.valid:
            return ExecutionRecommendation(
                action="NO_TRADE",
                explanation="Risk constraints are not satisfied.",
            )

        if has_contradiction:
            return ExecutionRecommendation(
                action="NO_TRADE",
                explanation="Conflicting institutional signals detected.",
            )

        if decision.valid and decision.institutionalScore >= settings.DECISION_MIN_SCORE and decision.confidence >= settings.DECISION_MIN_CONFIDENCE:
            if decision.direction == "BULLISH":
                return ExecutionRecommendation(
                    action="BUY",
                    explanation="Bullish institutional setup is valid with sufficient score and confidence.",
                )
            if decision.direction == "BEARISH":
                return ExecutionRecommendation(
                    action="SELL",
                    explanation="Bearish institutional setup is valid with sufficient score and confidence.",
                )

        if decision.institutionalScore < settings.DECISION_MIN_SCORE or decision.confidence < settings.DECISION_MIN_CONFIDENCE:
            return ExecutionRecommendation(
                action="WAIT",
                explanation="Setup exists but score or confidence is below threshold.",
            )

        return ExecutionRecommendation(
            action="NO_TRADE",
            explanation="Institutional decision is invalid.",
        )
