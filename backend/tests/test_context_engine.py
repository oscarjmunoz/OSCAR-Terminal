from app.engines.context.ContextEngine import ContextEngine


def test_context_engine_valid_result():
    result = ContextEngine.evaluate(
        liquidity={
            "timeframe": "H4",
            "side": "SSL",
            "level": 1.341,
            "taken": True,
        },
        order_block={
            "timeframe": "H1",
            "blockType": "BULLISH",
            "low": 1.3402,
            "high": 1.3412,
            "present": True,
        },
        fair_value_gap={
            "timeframe": "H1",
            "gapType": "BULLISH",
            "low": 1.3408,
            "high": 1.3414,
            "present": True,
        },
    )

    assert result["valid"] is True
    assert result["contextScore"] == 100
    assert len(result["reasons"]) == 3
    assert len(result["warnings"]) == 0
    assert result["liquidityTaken"]["valid"] is True
    assert result["orderBlock"]["valid"] is True
    assert result["fairValueGap"]["valid"] is True


def test_context_engine_invalid_when_h4_liquidity_missing():
    result = ContextEngine.evaluate(
        liquidity={
            "timeframe": "H1",
            "side": "NONE",
            "level": None,
            "taken": False,
        },
        order_block={
            "timeframe": "H1",
            "blockType": "BEARISH",
            "low": 1.3421,
            "high": 1.3431,
            "present": True,
        },
        fair_value_gap={
            "timeframe": "H1",
            "gapType": "BEARISH",
            "low": 1.3418,
            "high": 1.3426,
            "present": True,
        },
    )

    assert result["valid"] is False
    assert result["contextScore"] == 66
    assert len(result["reasons"]) == 2
    assert len(result["warnings"]) == 1
    assert result["liquidityTaken"]["valid"] is False


def test_context_engine_invalid_when_h1_confirmations_missing():
    result = ContextEngine.evaluate(
        liquidity={
            "timeframe": "H4",
            "side": "BSL",
            "level": 1.349,
            "taken": True,
        },
        order_block={
            "timeframe": "M15",
            "blockType": "NONE",
            "low": None,
            "high": None,
            "present": False,
        },
        fair_value_gap={
            "timeframe": "M5",
            "gapType": "NONE",
            "low": None,
            "high": None,
            "present": False,
        },
    )

    assert result["valid"] is False
    assert result["contextScore"] == 34
    assert len(result["reasons"]) == 1
    assert len(result["warnings"]) == 2
    assert result["orderBlock"]["valid"] is False
    assert result["fairValueGap"]["valid"] is False
