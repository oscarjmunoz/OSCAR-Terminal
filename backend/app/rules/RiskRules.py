from __future__ import annotations

from app.core.Rule import Rule


RISK_RULES: list[Rule] = [
    Rule("RISK-001", "RISK-001", "Risk Cap", "Per-trade risk cap must be respected.", "RISK", 34, True),
    Rule("RISK-002", "RISK-002", "Stop Coherence", "Stop placement must be structurally coherent.", "RISK", 33, True),
    Rule("RISK-003", "RISK-003", "Exposure Limit", "Global exposure limits must be respected.", "RISK", 33, True),
]

RISK_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in RISK_RULES}
