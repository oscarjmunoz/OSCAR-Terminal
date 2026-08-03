from app.engines.decision.ExecutionRecommendationEngine import ExecutionRecommendationEngine
from app.engines.decision.NarrativeEngine import NarrativeEngine
from app.engines.decision.PipelineModels import DecisionResult
from app.engines.decision.PipelineModels import ExecutionRecommendation
from app.engines.decision.PipelineModels import LiquidityResult
from app.engines.decision.PipelineModels import RiskResult


def _risk(valid: bool) -> RiskResult:
    return RiskResult(
        valid=valid,
        riskScore=90 if valid else 20,
        riskPercent=0.5 if valid else 2.5,
        rr=2.0 if valid else 1.0,
        exposurePercent=1.0 if valid else 5.0,
        sessionAllowed=valid,
        passedRules=("RISK-001",),
        failedRules=tuple() if valid else ("RISK-001",),
        reasons=("ok",) if valid else tuple(),
        warnings=tuple() if valid else ("bad",),
    )


def _decision(valid: bool, direction: str, score: int, confidence: int) -> DecisionResult:
    return DecisionResult(
        valid=valid,
        direction=direction,
        institutionalScore=score,
        confidence=confidence,
        state="VALID_LONG" if direction == "BULLISH" and valid else "INVALID",
        reasons=("ok",),
        warnings=tuple(),
    )


def _liquidity() -> LiquidityResult:
    return LiquidityResult(
        valid=True,
        sweepSide="SSL",
        data={
            "pdh": {"name": "PDH", "side": "BSL", "level": 1.35, "distance": 0.01, "taken": False},
            "pdl": {"name": "PDL", "side": "SSL", "level": 1.34, "distance": 0.01, "taken": False},
            "pwh": {"name": "PWH", "side": "BSL", "level": 1.36, "distance": 0.02, "taken": False},
            "pwl": {"name": "PWL", "side": "SSL", "level": 1.33, "distance": 0.02, "taken": False},
            "h4SwingHigh": {"name": "H4_SWING_HIGH", "side": "BSL", "level": 1.355, "distance": 0.015, "taken": False},
            "h4SwingLow": {"name": "H4_SWING_LOW", "side": "SSL", "level": 1.335, "distance": 0.015, "taken": False},
            "liquidityTaken": {"buySideTaken": [], "sellSideTaken": ["PDL"]},
            "nearestBuySideLiquidity": {"name": "PDH", "side": "BSL", "level": 1.35, "distance": 0.01, "taken": False},
            "nearestSellSideLiquidity": {"name": "PDL", "side": "SSL", "level": 1.34, "distance": 0.01, "taken": False},
        },
        reasons=("ok",),
        warnings=tuple(),
    )


def test_execution_recommendation_buy_when_valid_and_high_quality():
    recommendation = ExecutionRecommendationEngine.evaluate(
        decision=_decision(True, "BULLISH", 85, 80),
        risk=_risk(True),
        warnings=tuple(),
    )

    assert recommendation.action == "BUY"


def test_execution_recommendation_no_trade_when_risk_fails():
    recommendation = ExecutionRecommendationEngine.evaluate(
        decision=_decision(True, "BULLISH", 90, 90),
        risk=_risk(False),
        warnings=tuple(),
    )

    assert recommendation.action == "NO_TRADE"


def test_narrative_engine_produces_deterministic_story():
    recommendation = ExecutionRecommendation(action="BUY", explanation="All clear")
    decision = _decision(True, "BULLISH", 88, 83)

    narrative = NarrativeEngine.build(
        liquidity=_liquidity(),
        structure={
            "valid": True,
            "trend": "BULLISH",
            "breakDirection": "BULLISH",
            "swingHigh": 1.35,
            "swingLow": 1.34,
            "bos": True,
            "choch": False,
            "mss": True,
            "liquiditySweep": True,
            "displacement": True,
            "timeframeAligned": True,
            "swingImportance": "MAJOR",
            "passedRules": ["STR-001"],
            "failedRules": [],
            "reasons": ["ok"],
            "warnings": [],
        },
        context={
            "valid": True,
            "contextScore": 100,
            "reasons": ["ok"],
            "warnings": [],
            "liquidityTaken": {"timeframe": "H4", "valid": True, "side": "SSL", "level": 1.341},
            "orderBlock": {"timeframe": "H1", "valid": True, "blockType": "BULLISH", "low": 1.34, "high": 1.342},
            "fairValueGap": {"timeframe": "H1", "valid": True, "gapType": "BULLISH", "low": 1.3405, "high": 1.3415},
        },
        risk=_risk(True),
        decision=decision,
        recommendation=recommendation,
    )

    assert "Sell-side liquidity sweep detected." in narrative
    assert "Bullish BOS confirmed." in narrative
    assert "Recommendation BUY." in narrative
