from dataclasses import dataclass

from app.core.DecisionNode import DecisionNode
from app.core.DecisionStatus import DecisionStatus
from app.core.DecisionStatus import can_transition
from app.core.DecisionTree import DecisionTree
from app.core.EngineResult import EngineResult
from app.core.Rule import Rule
from app.core.RuleResult import RuleResult
from app.core.Score import Score


def test_rule_creation():
    rule = Rule(
        id="CTX-001",
        code="CTX-001",
        title="H4 Liquidity",
        description="Validate H4 liquidity.",
        category="CONTEXT",
        weight=34,
        critical=True,
    )

    assert rule.id == "CTX-001"
    assert rule.weight == 34
    assert rule.critical is True


def test_rule_result_creation():
    rule = Rule("TEST-001", "TEST-001", "Test Rule", "Description", "TEST", 10, False)
    result = RuleResult(
        rule=rule,
        status=DecisionStatus.PASS,
        score=120,
        reason="Rule passed",
    )

    assert result.score == 100
    assert result.status == DecisionStatus.PASS


def test_decision_node_creation_from_engine_result():
    rule = Rule("TEST-002", "TEST-002", "Rule 2", "Description", "TEST", 10, True)
    engine_result = EngineResult(
        engine="ContextEngine",
        status=DecisionStatus.PASS,
        score=Score(88),
        executionTime=12.5,
    )
    engine_result.add_rule_result(RuleResult(rule=rule, status=DecisionStatus.PASS, score=88, reason="ok"))

    node = DecisionNode.from_engine_result(engine_result)

    assert node.engine == "ContextEngine"
    assert node.status == DecisionStatus.PASS
    assert node.duration == 12.5
    assert len(node.rules) == 1


def test_decision_tree_accumulates_nodes_and_scores():
    tree = DecisionTree()

    node_a = DecisionNode(
        engine="ContextEngine",
        status=DecisionStatus.PASS,
        score=Score(90),
        rules=[],
        duration=5.0,
    )

    node_b = DecisionNode(
        engine="MSSEngine",
        status=DecisionStatus.WARNING,
        score=Score(70),
        rules=[],
        duration=6.0,
    )

    tree.add_node(node_a)
    tree.add_node(node_b)
    tree.set_next_step("IEZEngine")

    assert tree.currentStep == "MSSEngine"
    assert tree.nextStep == "IEZEngine"
    assert tree.overallScore.value == 80
    assert "MSSEngine" in tree.blockedBy
    assert len(tree.timeline) == 2


def test_engine_result_inheritance():
    @dataclass(slots=True)
    class ContextEngineResult(EngineResult):
        context_valid: bool = False

    result = ContextEngineResult(
        engine="ContextEngine",
        status=DecisionStatus.READY,
        score=Score(65),
        context_valid=True,
    )

    assert isinstance(result, EngineResult)
    assert result.context_valid is True


def test_status_transitions():
    assert can_transition(DecisionStatus.WAIT, DecisionStatus.READY) is True
    assert can_transition(DecisionStatus.READY, DecisionStatus.PASS) is True
    assert can_transition(DecisionStatus.FAIL, DecisionStatus.PASS) is False
    assert can_transition(DecisionStatus.PASS, DecisionStatus.FAIL) is False
    assert can_transition(DecisionStatus.WARNING, DecisionStatus.WAIT) is True
