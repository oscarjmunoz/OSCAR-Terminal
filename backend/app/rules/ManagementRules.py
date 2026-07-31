from __future__ import annotations

from app.core.Rule import Rule


MANAGEMENT_RULES: list[Rule] = [
    Rule("MANAGEMENT-001", "MANAGEMENT-001", "Break Even Plan", "Break-even rule must be defined.", "MANAGEMENT", 34, True),
    Rule("MANAGEMENT-002", "MANAGEMENT-002", "Partial Exit Plan", "Partial exit rule must be defined.", "MANAGEMENT", 33, True),
    Rule("MANAGEMENT-003", "MANAGEMENT-003", "Runner Plan", "Runner management rule must be defined.", "MANAGEMENT", 33, False),
]

MANAGEMENT_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in MANAGEMENT_RULES}
