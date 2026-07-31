from __future__ import annotations

from app.core.Rule import Rule


ENTRY_RULES: list[Rule] = [
    Rule("ENT-001", "ENT-001", "Zone Availability", "Institutional entry zone must be available.", "ENTRY", 34, True),
    Rule("ENT-002", "ENT-002", "Trigger Valid", "Execution trigger must be validated.", "ENTRY", 33, True),
    Rule("ENT-003", "ENT-003", "Timing Window", "Execution timing window must be open.", "ENTRY", 33, False),
]

ENTRY_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in ENTRY_RULES}
