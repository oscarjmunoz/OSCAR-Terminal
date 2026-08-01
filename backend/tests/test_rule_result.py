from app.core.DecisionStatus import DecisionStatus
from app.core.Rule import Rule
from app.core.RuleResult import RuleResult


def test_rule_result_creation() -> None:
    rule = Rule(
        id="CORE-002",
        code="CORE-002",
        title="Resultado base",
        description="Regla para crear RuleResult.",
        category="CORE",
        weight=15,
        critical=False,
    )

    result = RuleResult(
        rule=rule,
        status=DecisionStatus.READY,
        score=80,
        reason="Pendiente de confirmacion.",
        warning="",
    )

    assert result.rule == rule
    assert result.status == DecisionStatus.READY
    assert result.score == 80
    assert result.reason == "Pendiente de confirmacion."
    assert result.warning == ""


def test_rule_result_assigns_status_and_clamps_score() -> None:
    rule = Rule(
        id="CORE-003",
        code="CORE-003",
        title="Clamp score",
        description="Score debe mantenerse en rango 0..100.",
        category="CORE",
        weight=5,
        critical=False,
    )

    high_score = RuleResult(rule=rule, status=DecisionStatus.PASS, score=300)
    low_score = RuleResult(rule=rule, status=DecisionStatus.FAIL, score=-20)

    assert high_score.status == DecisionStatus.PASS
    assert low_score.status == DecisionStatus.FAIL
    assert high_score.score == 100
    assert low_score.score == 0