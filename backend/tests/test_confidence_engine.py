from app.engines.context.ContextEngine import ContextEngine
from app.engines.decision.ConfidenceEngine import ConfidenceEngine
from app.engines.decision.ConfluenceEngine import ConfluenceEngine
from app.engines.decision.RiskEngine import RiskEngine
from app.engines.mss.MSSEngine import MSSEngine
from app.engines.premium_discount.PremiumDiscountEngine import PremiumDiscountEngine
from app.engines.structure.MarketStructureEngine import MarketStructureEngine


def _deps() -> dict:
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
        order_block={"timeframe": "H1", "blockType": "BULLISH", "low": 1.3402, "high": 1.3412, "present": True},
        fair_value_gap={"timeframe": "H1", "gapType": "BULLISH", "low": 1.3408, "high": 1.3414, "present": True},
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
            "rr": 2.0,
            "exposurePercent": 1.2,
            "stopAligned": True,
            "session": "LONDON",
        }
    )
    confluence = ConfluenceEngine.evaluate(
        structure=structure,
        mss=mss,
        context=context,
        premium_discount=premium_discount,
    )
    return {
        "structure": structure,
        "mss": mss,
        "context": context,
        "premium_discount": premium_discount,
        "risk": risk,
        "confluence": confluence,
    }


def test_confidence_engine_returns_high_confidence_when_aligned():
    dep = _deps()

    confidence = ConfidenceEngine.evaluate(
        bias="BULLISH",
        structure=dep["structure"],
        mss=dep["mss"],
        context=dep["context"],
        premium_discount=dep["premium_discount"],
        confluence=dep["confluence"],
        risk=dep["risk"],
        warnings=tuple(),
    )

    assert confidence >= 75


def test_confidence_engine_drops_with_contradictions():
    dep = _deps()

    confidence = ConfidenceEngine.evaluate(
        bias="BEARISH",
        structure=dep["structure"],
        mss=dep["mss"],
        context=dep["context"],
        premium_discount=dep["premium_discount"],
        confluence=dep["confluence"],
        risk=dep["risk"],
        warnings=("Contradiction: structure and bias.", "Contradiction: liquidity and bias."),
    )

    assert confidence < 80
