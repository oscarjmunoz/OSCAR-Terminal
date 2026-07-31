from app.engines.mss.MSSEngine import MSSEngine


def test_mss_engine_all_rules_pass_bullish():
    result = MSSEngine.evaluate(
        {
            "direction": "BULLISH",
            "brokenStructureLevel": 1.3442,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "sweepSide": "SSL",
        }
    )

    assert result["valid"] is True
    assert result["direction"] == "BULLISH"
    assert result["brokenStructureLevel"] == 1.3442
    assert result["passedRules"] == [
        "MSS-001",
        "MSS-002",
        "MSS-003",
        "MSS-004",
        "MSS-005",
        "MSS-006",
    ]
    assert result["failedRules"] == []
    assert len(result["reasons"]) == 6
    assert len(result["warnings"]) == 0


def test_mss_engine_fails_specific_rules():
    result = MSSEngine.evaluate(
        {
            "direction": "BULLISH",
            "brokenStructureLevel": None,
            "liquiditySweep": False,
            "displacement": True,
            "fvgCreated": False,
            "biasAligned": False,
            "sweepSide": "BSL",
        }
    )

    assert result["valid"] is False
    assert result["passedRules"] == ["MSS-003"]
    assert result["failedRules"] == ["MSS-001", "MSS-002", "MSS-004", "MSS-005", "MSS-006"]
    assert len(result["reasons"]) == 1
    assert len(result["warnings"]) == 5


def test_mss_engine_bearish_requires_bsl_sweep_for_mss_006():
    passing = MSSEngine.evaluate(
        {
            "direction": "BEARISH",
            "brokenStructureLevel": 1.3398,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "sweepSide": "BSL",
        }
    )

    failing = MSSEngine.evaluate(
        {
            "direction": "BEARISH",
            "brokenStructureLevel": 1.3398,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "sweepSide": "SSL",
        }
    )

    assert "MSS-006" in passing["passedRules"]
    assert "MSS-006" in failing["failedRules"]
    assert passing["valid"] is True
    assert failing["valid"] is False


def test_mss_engine_none_direction_never_passes_mss_001_and_mss_006():
    result = MSSEngine.evaluate(
        {
            "direction": "NONE",
            "brokenStructureLevel": 1.3401,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "sweepSide": "NONE",
        }
    )

    assert "MSS-001" in result["failedRules"]
    assert "MSS-006" in result["failedRules"]
    assert result["valid"] is False
