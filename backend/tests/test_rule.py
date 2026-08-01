from dataclasses import FrozenInstanceError

import pytest

from app.core.Rule import Rule


def test_rule_creation() -> None:
    rule = Rule(
        id="CORE-001",
        code="CORE-001",
        title="Regla base",
        description="Valida una condicion generica.",
        category="CORE",
        weight=10,
        critical=True,
    )

    assert rule.id == "CORE-001"
    assert rule.code == "CORE-001"
    assert rule.title == "Regla base"
    assert rule.description == "Valida una condicion generica."
    assert rule.category == "CORE"
    assert rule.weight == 10
    assert rule.critical is True


def test_rule_rejects_negative_weight() -> None:
    with pytest.raises(ValueError, match="Rule weight must be >= 0"):
        Rule(
            id="CORE-NEG",
            code="CORE-NEG",
            title="Regla invalida",
            description="No debe aceptar peso negativo.",
            category="CORE",
            weight=-1,
            critical=False,
        )


def test_rule_is_immutable() -> None:
    rule = Rule(
        id="CORE-IMM",
        code="CORE-IMM",
        title="Inmutable",
        description="Debe ser inmutable.",
        category="CORE",
        weight=5,
        critical=False,
    )

    with pytest.raises(FrozenInstanceError):
        rule.weight = 99