from __future__ import annotations

from app.engines.context.ContextEngine import ContextEngine
from app.engines.decision.ConfidenceEngine import ConfidenceEngine
from app.engines.decision.ConfluenceEngine import ConfluenceEngine
from app.engines.decision.ExecutionRecommendationEngine import ExecutionRecommendationEngine
from app.engines.decision.InstitutionalDecisionEngine import InstitutionalDecisionEngine
from app.engines.decision.InstitutionalScoreEngine import InstitutionalScoreEngine
from app.engines.decision.InstitutionalValidationEngine import InstitutionalValidationEngine
from app.engines.decision.NarrativeEngine import NarrativeEngine
from app.engines.decision.PipelineModels import DecisionContext
from app.engines.decision.PipelineModels import DecisionResult
from app.engines.decision.PipelineModels import InstitutionalPipelineInput
from app.engines.decision.PipelineModels import LiquidityResult
from app.engines.decision.PipelineModels import StructureResult
from app.engines.decision.RiskEngine import RiskEngine
from app.engines.liquidity.LiquidityMap import LiquidityMap
from app.engines.liquidity.LiquidityMapEngine import LiquidityMapEngine
from app.engines.mss.MSSResult import MSSResult
from app.engines.mss.MSSEngine import MSSEngine
from app.engines.premium_discount.PremiumDiscountEngine import PremiumDiscountEngine
from app.engines.structure.MarketStructureResult import MarketStructureResult
from app.engines.structure.MarketStructureEngine import MarketStructureEngine


class InstitutionalPipeline:
    """Pure orchestrator for institutional decision flow.

    Flow:
    Market Data -> Liquidity -> Structure -> Context -> Risk -> Decision -> Recommendation
    """

    @staticmethod
    def evaluate(data: InstitutionalPipelineInput) -> DecisionContext:
        liquidity_map = LiquidityMapEngine.build(data["liquidity"])
        liquidity_result = InstitutionalPipeline._build_liquidity_result(liquidity_map)

        structure_result_raw = MarketStructureEngine.evaluate(data["structure"])
        mss_result = MSSEngine.evaluate(data["mss"])
        structure_result = InstitutionalPipeline._build_structure_result(structure_result_raw, mss_result)

        context_result = ContextEngine.evaluate(
            liquidity=data["context"]["liquidity"],
            order_block=data["context"]["orderBlock"],
            fair_value_gap=data["context"]["fairValueGap"],
        )

        premium_discount_result = PremiumDiscountEngine.evaluate(data["premiumDiscount"])
        risk_result = RiskEngine.evaluate(data["risk"])

        validation_warnings = InstitutionalValidationEngine.evaluate(
            bias=data["market"]["bias"],
            liquidity=liquidity_result,
            structure=structure_result_raw,
            mss=mss_result,
            context=context_result,
            risk=risk_result,
        )

        confluence_result = ConfluenceEngine.evaluate(
            structure=structure_result_raw,
            mss=mss_result,
            context=context_result,
            premium_discount=premium_discount_result,
        )

        confidence = ConfidenceEngine.evaluate(
            bias=data["market"]["bias"],
            structure=structure_result_raw,
            mss=mss_result,
            context=context_result,
            premium_discount=premium_discount_result,
            confluence=confluence_result,
            risk=risk_result,
            warnings=validation_warnings,
        )

        score_result = InstitutionalScoreEngine.evaluate(
            bias=data["market"]["bias"],
            session=data["market"]["session"],
            liquidity_valid=liquidity_result.valid,
            structure=structure_result_raw,
            mss=mss_result,
            context=context_result,
            premium_discount=premium_discount_result,
            risk=risk_result,
            confidence=confidence,
        )

        decision_engine_result = InstitutionalDecisionEngine.evaluate(
            {
                "context": context_result,
                "liquidity": liquidity_map,
                "premiumDiscount": premium_discount_result,
                "mss": mss_result,
                "confluence": confluence_result,
                "score": score_result,
            }
        )

        decision_result = DecisionResult(
            valid=decision_engine_result.valid,
            direction=decision_engine_result.direction,
            institutionalScore=decision_engine_result.institutionalScore,
            confidence=decision_engine_result.confidence,
            state=decision_engine_result.decisionState,
            reasons=tuple(decision_engine_result.reasons),
            warnings=tuple(decision_engine_result.warnings),
        )

        warnings = tuple(
            dict.fromkeys(
                [
                    *validation_warnings,
                    *context_result["warnings"],
                    *structure_result_raw["warnings"],
                    *mss_result["warnings"],
                    *premium_discount_result["warnings"],
                    *risk_result.warnings,
                    *decision_result.warnings,
                ]
            )
        )

        recommendation = ExecutionRecommendationEngine.evaluate(
            decision=decision_result,
            risk=risk_result,
            warnings=warnings,
        )

        narrative = NarrativeEngine.build(
            liquidity=liquidity_result,
            structure=structure_result_raw,
            context=context_result,
            risk=risk_result,
            decision=decision_result,
            recommendation=recommendation,
        )

        return DecisionContext(
            market=data["market"]["symbol"],
            timeframe=data["market"]["timeframe"],
            bias=data["market"]["bias"],
            liquidity=liquidity_result,
            structure=structure_result,
            risk=risk_result,
            institutionalScore=decision_result.institutionalScore,
            confidence=decision_result.confidence,
            narrative=narrative,
            warnings=warnings,
            executionRecommendation=recommendation,
        )

    @staticmethod
    def _build_liquidity_result(liquidity_map: LiquidityMap) -> LiquidityResult:
        required_keys = {
            "pdh",
            "pdl",
            "pwh",
            "pwl",
            "h4SwingHigh",
            "h4SwingLow",
            "nearestBuySideLiquidity",
            "nearestSellSideLiquidity",
        }
        valid = required_keys.issubset(set(liquidity_map.keys()))

        buy_side_taken = liquidity_map["liquidityTaken"]["buySideTaken"]
        sell_side_taken = liquidity_map["liquidityTaken"]["sellSideTaken"]

        sweep_side = "NONE"
        if len(sell_side_taken) > 0 and len(buy_side_taken) == 0:
            sweep_side = "SSL"
        elif len(buy_side_taken) > 0 and len(sell_side_taken) == 0:
            sweep_side = "BSL"

        reasons = ["Liquidity map built successfully."] if valid else []
        warnings = [] if valid else ["Missing required liquidity levels."]

        return LiquidityResult(
            valid=valid,
            sweepSide=sweep_side,
            data=liquidity_map,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )

    @staticmethod
    def _build_structure_result(structure_result: MarketStructureResult, mss_result: MSSResult) -> StructureResult:
        direction = mss_result["direction"] if mss_result["direction"] != "NONE" else structure_result["breakDirection"]
        return StructureResult(
            valid=bool(structure_result["valid"] and mss_result["valid"]),
            direction=direction,
            trend=structure_result["trend"],
            marketStructure=structure_result,
            mss=mss_result,
            reasons=tuple([*structure_result["reasons"], *mss_result["reasons"]]),
            warnings=tuple([*structure_result["warnings"], *mss_result["warnings"]]),
        )
