from app.engines.iez.IEZEngine import IEZEngine


def test_iez_engine_all_rules_pass_and_scores_are_high():
    result = IEZEngine.evaluate(
        {
            "direction": "BULLISH",
            "entryZoneLow": 1.3410,
            "entryZoneHigh": 1.3430,
            "currentPrice": 1.3420,
            "discountForLong": True,
            "premiumForShort": False,
            "fvgConfluence": True,
            "obConfluence": True,
            "liquidityContextAligned": True,
            "mssAligned": True,
            "timeframeAligned": True,
        }
    )

    assert result["valid"] is True
    assert result["passedRules"] == [
        "IEZ-001",
        "IEZ-002",
        "IEZ-003",
        "IEZ-004",
        "IEZ-005",
        "IEZ-006",
        "IEZ-007",
    ]
    assert result["failedRules"] == []
    assert result["iezScore"] == 100
    assert result["entryPriority"] == "HIGH"
    assert result["qualityScore"] == 100


def test_iez_engine_fails_when_zone_is_invalid_and_price_outside():
    result = IEZEngine.evaluate(
        {
            "direction": "BEARISH",
            "entryZoneLow": 1.3450,
            "entryZoneHigh": 1.3440,
            "currentPrice": 1.3460,
            "discountForLong": False,
            "premiumForShort": True,
            "fvgConfluence": True,
            "obConfluence": False,
            "liquidityContextAligned": True,
            "mssAligned": False,
            "timeframeAligned": True,
        }
    )

    assert result["valid"] is False
    assert "IEZ-003" in result["failedRules"]
    assert "IEZ-004" in result["failedRules"]
    assert "IEZ-006" in result["failedRules"]
    assert "IEZ-007" in result["failedRules"]
    assert result["entryPriority"] in {"LOW", "NONE"}


def test_iez_engine_directional_location_alignment_rule():
    bullish_misaligned = IEZEngine.evaluate(
        {
            "direction": "BULLISH",
            "entryZoneLow": 1.3410,
            "entryZoneHigh": 1.3430,
            "currentPrice": 1.3422,
            "discountForLong": False,
            "premiumForShort": False,
            "fvgConfluence": True,
            "obConfluence": True,
            "liquidityContextAligned": True,
            "mssAligned": True,
            "timeframeAligned": True,
        }
    )

    bearish_misaligned = IEZEngine.evaluate(
        {
            "direction": "BEARISH",
            "entryZoneLow": 1.3410,
            "entryZoneHigh": 1.3430,
            "currentPrice": 1.3422,
            "discountForLong": False,
            "premiumForShort": False,
            "fvgConfluence": True,
            "obConfluence": True,
            "liquidityContextAligned": True,
            "mssAligned": True,
            "timeframeAligned": True,
        }
    )

    assert "IEZ-005" in bullish_misaligned["failedRules"]
    assert "IEZ-005" in bearish_misaligned["failedRules"]


def test_iez_engine_none_direction_is_not_valid():
    result = IEZEngine.evaluate(
        {
            "direction": "NONE",
            "entryZoneLow": 1.3410,
            "entryZoneHigh": 1.3430,
            "currentPrice": 1.3420,
            "discountForLong": True,
            "premiumForShort": True,
            "fvgConfluence": True,
            "obConfluence": True,
            "liquidityContextAligned": True,
            "mssAligned": True,
            "timeframeAligned": True,
        }
    )

    assert result["valid"] is False
    assert "IEZ-001" in result["failedRules"]
    assert "IEZ-005" in result["failedRules"]
