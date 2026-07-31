from app.engines.structure.MarketStructureEngine import MarketStructureEngine


def test_market_structure_engine_all_rules_pass():
    result = MarketStructureEngine.evaluate(
        {
            "trend": "BULLISH",
            "breakDirection": "BULLISH",
            "swingHigh": 1.3520,
            "swingLow": 1.3440,
            "bos": True,
            "choch": False,
            "liquiditySweep": True,
            "displacement": True,
            "timeframeAligned": True,
            "swingImportance": "MAJOR",
        }
    )

    assert result["valid"] is True
    assert result["passedRules"] == [
        "STR-001",
        "STR-002",
        "STR-003",
        "STR-004",
        "STR-005",
        "STR-006",
        "STR-007",
        "STR-008",
    ]
    assert result["failedRules"] == []
    assert result["mss"] is False


def test_market_structure_engine_fails_when_structure_is_missing():
    result = MarketStructureEngine.evaluate(
        {
            "trend": "BEARISH",
            "breakDirection": "BEARISH",
            "swingHigh": None,
            "swingLow": 1.3400,
            "bos": False,
            "choch": False,
            "liquiditySweep": False,
            "displacement": False,
            "timeframeAligned": True,
            "swingImportance": "MINOR",
        }
    )

    assert result["valid"] is False
    assert "STR-002" in result["failedRules"]
    assert "STR-004" in result["failedRules"]
    assert "STR-005" in result["failedRules"]
    assert "STR-007" in result["failedRules"]


def test_market_structure_engine_fails_when_direction_is_not_coherent():
    result = MarketStructureEngine.evaluate(
        {
            "trend": "BULLISH",
            "breakDirection": "BEARISH",
            "swingHigh": 1.3530,
            "swingLow": 1.3450,
            "bos": True,
            "choch": True,
            "liquiditySweep": True,
            "displacement": True,
            "timeframeAligned": True,
            "swingImportance": "INTERNAL",
        }
    )

    assert result["valid"] is False
    assert "STR-006" in result["failedRules"]
    assert result["mss"] is True


def test_market_structure_engine_fails_when_timeframe_is_not_aligned():
    result = MarketStructureEngine.evaluate(
        {
            "trend": "RANGE",
            "breakDirection": "BULLISH",
            "swingHigh": 1.3500,
            "swingLow": 1.3460,
            "bos": False,
            "choch": True,
            "liquiditySweep": True,
            "displacement": True,
            "timeframeAligned": False,
            "swingImportance": "MINOR",
        }
    )

    assert result["valid"] is False
    assert "STR-008" in result["failedRules"]
