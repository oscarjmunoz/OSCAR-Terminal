from dataclasses import FrozenInstanceError

import pytest

from app.engines.decision.InstitutionalPipeline import InstitutionalPipeline


def _pipeline_input() -> dict:
    return {
        "market": {
            "symbol": "EURUSD",
            "timeframe": "M15",
            "bias": "BULLISH",
            "session": "LONDON",
            "currentPrice": 1.3420,
        },
        "liquidity": {
            "currentPrice": 1.3420,
            "pdh": 1.3500,
            "pdl": 1.3400,
            "pwh": 1.3520,
            "pwl": 1.3380,
            "h4Candles": [
                {"high": 1.3430, "low": 1.3390},
                {"high": 1.3440, "low": 1.3380},
                {"high": 1.3490, "low": 1.3370},
                {"high": 1.3460, "low": 1.3368},
                {"high": 1.3455, "low": 1.3381},
                {"high": 1.3470, "low": 1.3372},
                {"high": 1.3462, "low": 1.3379},
            ],
        },
        "structure": {
            "trend": "BULLISH",
            "breakDirection": "BULLISH",
            "swingHigh": 1.3500,
            "swingLow": 1.3400,
            "bos": True,
            "choch": False,
            "liquiditySweep": True,
            "displacement": True,
            "timeframeAligned": True,
            "swingImportance": "MAJOR",
        },
        "context": {
            "liquidity": {
                "timeframe": "H4",
                "side": "SSL",
                "level": 1.3410,
                "taken": True,
            },
            "orderBlock": {
                "timeframe": "H1",
                "blockType": "BULLISH",
                "low": 1.3402,
                "high": 1.3410,
                "present": True,
            },
            "fairValueGap": {
                "timeframe": "H1",
                "gapType": "BULLISH",
                "low": 1.3408,
                "high": 1.3414,
                "present": True,
            },
        },
        "premiumDiscount": {
            "currentPrice": 1.3420,
            "rangeHigh": 1.3500,
            "rangeLow": 1.3400,
            "bias": "BULLISH",
        },
        "mss": {
            "direction": "BULLISH",
            "brokenStructureLevel": 1.3430,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "sweepSide": "SSL",
        },
        "risk": {
            "riskPercent": 0.5,
            "rr": 2.0,
            "exposurePercent": 1.5,
            "stopAligned": True,
            "session": "LONDON",
        },
    }


def test_institutional_pipeline_happy_path_returns_buy_context():
    result = InstitutionalPipeline.evaluate(_pipeline_input())

    assert result.market == "EURUSD"
    assert result.timeframe == "M15"
    assert result.institutionalScore >= 70
    assert result.confidence >= 65
    assert result.executionRecommendation.action == "BUY"
    assert "Recommendation BUY." in result.narrative


def test_decision_context_is_immutable():
    result = InstitutionalPipeline.evaluate(_pipeline_input())

    with pytest.raises(FrozenInstanceError):
        result.market = "GBPUSD"


def test_pipeline_generates_warnings_for_conflicting_bias_and_liquidity():
    payload = _pipeline_input()
    payload["market"]["bias"] = "BEARISH"
    payload["liquidity"]["currentPrice"] = 1.3390

    result = InstitutionalPipeline.evaluate(payload)

    assert any("Contradiction" in warning for warning in result.warnings)


def test_pipeline_returns_no_trade_when_risk_is_invalid():
    payload = _pipeline_input()
    payload["risk"]["riskPercent"] = 2.5

    result = InstitutionalPipeline.evaluate(payload)

    assert result.executionRecommendation.action == "NO_TRADE"
    assert "Risk" in result.executionRecommendation.explanation
