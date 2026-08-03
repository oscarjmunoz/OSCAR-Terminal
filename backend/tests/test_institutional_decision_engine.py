from app.core.DecisionStatus import DecisionStatus
from app.core.DecisionTree import DecisionTree
from app.core.EngineResult import EngineResult
from app.engines.decision.InstitutionalDecisionEngine import InstitutionalDecisionEngine


def _base_input() -> dict:
    return {
        "liquidity": {
            "pdh": {"name": "PDH", "side": "BSL", "level": 1.3500, "distance": 0.009, "taken": False},
            "pdl": {"name": "PDL", "side": "SSL", "level": 1.3400, "distance": 0.001, "taken": False},
            "pwh": {"name": "PWH", "side": "BSL", "level": 1.3520, "distance": 0.011, "taken": False},
            "pwl": {"name": "PWL", "side": "SSL", "level": 1.3380, "distance": 0.003, "taken": False},
            "h4SwingHigh": {"name": "H4_SWING_HIGH", "side": "BSL", "level": 1.3550, "distance": 0.014, "taken": False},
            "h4SwingLow": {"name": "H4_SWING_LOW", "side": "SSL", "level": 1.3360, "distance": 0.005, "taken": False},
            "liquidityTaken": {"buySideTaken": [], "sellSideTaken": []},
            "nearestBuySideLiquidity": {"name": "PDH", "side": "BSL", "level": 1.3500, "distance": 0.009, "taken": False},
            "nearestSellSideLiquidity": {"name": "PDL", "side": "SSL", "level": 1.3400, "distance": 0.001, "taken": False},
        },
        "context": {
            "valid": True,
            "contextScore": 100,
            "reasons": ["CTX-OK"],
            "warnings": [],
            "liquidityTaken": {
                "timeframe": "H4",
                "valid": True,
                "side": "SSL",
                "level": 1.341,
            },
            "orderBlock": {
                "timeframe": "H1",
                "valid": True,
                "blockType": "BULLISH",
                "low": 1.34,
                "high": 1.342,
            },
            "fairValueGap": {
                "timeframe": "H1",
                "valid": True,
                "gapType": "BULLISH",
                "low": 1.3405,
                "high": 1.3415,
            },
        },
        "premiumDiscount": {
            "valid": True,
            "zone": "DISCOUNT",
            "currentPrice": 1.341,
            "rangeHigh": 1.35,
            "rangeLow": 1.34,
            "equilibrium": 1.345,
            "distanceToEquilibrium": 0.004,
            "inPremium": False,
            "inDiscount": True,
            "inEquilibrium": False,
            "biasAligned": True,
            "passedRules": ["PD-001"],
            "failedRules": [],
            "reasons": [],
            "warnings": [],
        },
        "mss": {
            "valid": True,
            "direction": "BULLISH",
            "brokenStructureLevel": 1.343,
            "liquiditySweep": True,
            "displacement": True,
            "fvgCreated": True,
            "biasAligned": True,
            "passedRules": ["MSS-001"],
            "failedRules": [],
            "reasons": [],
            "warnings": [],
        },
        "confluence": {
            "valid": True,
            "direction": "BULLISH",
            "inInstitutionalZone": True,
            "passedRules": ["CONF-001"],
            "failedRules": [],
            "reasons": [],
            "warnings": [],
        },
        "score": {
            "valid": True,
            "institutionalScore": 86,
            "confidence": 86,
            "passedRules": ["SCR-001"],
            "failedRules": [],
            "reasons": [],
            "warnings": [],
        },
    }


def test_institutional_decision_engine_all_rules_pass_valid_long_state():
    result = InstitutionalDecisionEngine.evaluate(_base_input())

    assert isinstance(result, EngineResult)
    assert result.valid is True
    assert result.status == DecisionStatus.PASS
    assert result.decisionState == "VALID_LONG"
    assert result.direction == "BULLISH"
    assert result.institutionalScore == 86
    assert result.confidence == 86
    assert result.failedAt == "Decision"
    assert result.criticalFailure == ""
    assert result.blockedBy == []
    assert len(result.passedRules) == 8
    assert len(result.failedRules) == 0
    assert result.engineSequence == [
        "Liquidity",
        "Context",
        "PremiumDiscount",
        "MSS",
        "Confluence",
        "Score",
        "Decision",
    ]


def test_institutional_decision_engine_fails_on_direction_mismatch():
    payload = _base_input()
    payload["confluence"]["direction"] = "BEARISH"

    result = InstitutionalDecisionEngine.evaluate(payload)

    assert result.valid is False
    assert result.status == DecisionStatus.FAIL
    assert result.decisionState == "INVALID"
    assert result.failedAt == "Decision"
    assert result.criticalFailure == "DIRECTION_MISMATCH"
    failed_ids = {rule.rule.id for rule in result.failedRules}
    assert "IDE-006" in failed_ids
    assert "IDE-006" in (result.blockedBy or [])


def test_institutional_decision_engine_warns_on_non_critical_location_rule_only():
    payload = _base_input()
    payload["premiumDiscount"]["zone"] = "PREMIUM"

    result = InstitutionalDecisionEngine.evaluate(payload)

    assert result.valid is False
    assert result.status == DecisionStatus.WARNING
    assert result.failedAt == "NONE"
    assert result.criticalFailure == ""
    failed_ids = {rule.rule.id for rule in result.failedRules}
    assert failed_ids == {"IDE-007"}


def test_institutional_decision_engine_run_integrates_with_tree():
    tree = DecisionTree()

    node = InstitutionalDecisionEngine.run(_base_input(), tree=tree)

    assert node.engine == "InstitutionalDecisionEngine"
    assert node.status == DecisionStatus.PASS
    assert len(tree.nodes) == 1
    assert tree.currentStep == "InstitutionalDecisionEngine"
    assert tree.nextStep == "ExecutionEngine"


def test_institutional_decision_engine_stops_at_first_critical_failure():
    payload = _base_input()
    payload["context"]["valid"] = False

    result = InstitutionalDecisionEngine.evaluate(payload)

    assert result.valid is False
    assert result.status == DecisionStatus.FAIL
    assert result.failedAt == "Context"
    assert result.criticalFailure == "CONTEXT_NOT_VALID"
    failed_ids = [rule.rule.id for rule in result.failedRules]
    assert failed_ids == ["IDE-001"]
