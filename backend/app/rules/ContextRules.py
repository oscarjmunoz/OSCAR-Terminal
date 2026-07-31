from __future__ import annotations

from app.core.Rule import Rule


CONTEXT_RULES: list[Rule] = [
    Rule("CTX-001", "CTX-001", "H4 Liquidity", "Validate H4 liquidity condition.", "CONTEXT", 34, True),
    Rule("CTX-002", "CTX-002", "H1 Order Block", "Validate H1 order block condition.", "CONTEXT", 33, True),
    Rule("CTX-003", "CTX-003", "H1 Fair Value Gap", "Validate H1 fair value gap condition.", "CONTEXT", 33, True),
]

CONTEXT_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in CONTEXT_RULES}
