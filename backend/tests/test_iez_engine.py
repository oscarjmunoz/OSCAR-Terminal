from app.core.DecisionStatus import DecisionStatus
from app.core.DecisionTree import DecisionTree
from app.core.EngineResult import EngineResult
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

    assert isinstance(result, EngineResult)
    assert result.valid is True
    assert result.status == DecisionStatus.PASS
    assert [rule.rule.id for rule in result.passedRules] == [
        "IEZ-001",
        "IEZ-002",
        "IEZ-003",
        "IEZ-004",
        "IEZ-005",
        "IEZ-006",
        "IEZ-007",
    ]
    assert result.failedRules == []
    assert result.iezScore == 100
    assert result.entryPriority == "HIGH"
    assert result.qualityScore == 100


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

    assert result.valid is False
    assert result.status == DecisionStatus.FAIL
    failed = {rule.rule.id for rule in result.failedRules}
    assert "IEZ-003" in failed
    assert "IEZ-004" in failed
    assert "IEZ-006" in failed
    assert "IEZ-007" in failed
    assert result.entryPriority in {"LOW", "NONE"}


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

    assert "IEZ-005" in {rule.rule.id for rule in bullish_misaligned.failedRules}
    assert "IEZ-005" in {rule.rule.id for rule in bearish_misaligned.failedRules}


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

    assert result.valid is False
    failed = {rule.rule.id for rule in result.failedRules}
    assert "IEZ-001" in failed
    assert "IEZ-005" in failed


def test_iez_engine_run_returns_decision_node_and_integrates_with_tree():
    tree = DecisionTree()

    node = IEZEngine.run(
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
        },
        tree=tree,
    )

    assert node.engine == "IEZEngine"
    assert node.status == DecisionStatus.PASS
    assert len(node.rules) == 7
    assert len(tree.nodes) == 1
    assert tree.currentStep == "IEZEngine"
    assert tree.nextStep == "EntryEngine"
