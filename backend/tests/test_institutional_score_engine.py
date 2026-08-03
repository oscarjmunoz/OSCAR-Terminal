from app.engines.context.ContextEngine import ContextEngine
from app.engines.decision.InstitutionalScoreEngine import InstitutionalScoreEngine
from app.engines.decision.RiskEngine import RiskEngine
from app.engines.mss.MSSEngine import MSSEngine
from app.engines.premium_discount.PremiumDiscountEngine import PremiumDiscountEngine
from app.engines.structure.MarketStructureEngine import MarketStructureEngine


def _score_dependencies() -> dict:
    structure = MarketStructureEngine.evaluate(
        {
            "trend": "BULLISH",
            "breakDirection": "BULLISH",
            "swingHigh": 1.35,
            "swingLow": 1.34,
            "bos": True,
            "choch": False,
            "liquiditySweep": True,
            "displacement": True,
            "timeframeAligned": True,
            "swingImportance": "MAJOR",
        }
    )

    mss = MSSEngine.evaluate(
        {
            "direction": "BULLISH",
            "brokenStructureLevel": 1.343,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "sweepSide": "SSL",
        }
    )

    context = ContextEngine.evaluate(
        liquidity={"timeframe": "H4", "side": "SSL", "level": 1.341, "taken": True},
        order_block={"timeframe": "H1", "blockType": "BULLISH", "low": 1.3405, "high": 1.3413, "present": True},
        fair_value_gap={"timeframe": "H1", "gapType": "BULLISH", "low": 1.3407, "high": 1.3414, "present": True},
    )

    premium_discount = PremiumDiscountEngine.evaluate(
        {
            "currentPrice": 1.3415,
            "rangeHigh": 1.35,
            "rangeLow": 1.34,
            "bias": "BULLISH",
        }
    )

    risk = RiskEngine.evaluate(
        {
            "riskPercent": 0.5,
            "rr": 2.2,
            "exposurePercent": 1.0,
            "stopAligned": True,
            "session": "LONDON",
        }
    )

    return {
        "structure": structure,
        "mss": mss,
        "context": context,
        "premium_discount": premium_discount,
        "risk": risk,
    }


def test_institutional_score_engine_returns_high_score_when_components_align():
    dep = _score_dependencies()

    result = InstitutionalScoreEngine.evaluate(
        bias="BULLISH",
        session="LONDON",
        liquidity_valid=True,
        structure=dep["structure"],
        mss=dep["mss"],
        context=dep["context"],
        premium_discount=dep["premium_discount"],
        risk=dep["risk"],
        confidence=90,
    )

    assert result["valid"] is True
    assert result["institutionalScore"] >= 80
    assert "SCR-001" in result["passedRules"]
    assert result["confidence"] == 90


def test_institutional_score_engine_penalizes_misalignment():
    dep = _score_dependencies()

    result = InstitutionalScoreEngine.evaluate(
        bias="BEARISH",
        session="OFF_HOURS",
        liquidity_valid=False,
        structure=dep["structure"],
        mss=dep["mss"],
        context=dep["context"],
        premium_discount=dep["premium_discount"],
        risk=dep["risk"],
        confidence=35,
    )

    assert result["institutionalScore"] < 70
    assert result["valid"] is False
    assert len(result["failedRules"]) > 0
