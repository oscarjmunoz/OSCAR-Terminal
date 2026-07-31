from __future__ import annotations

from app.core.Rule import Rule


LIQUIDITY_RULES: list[Rule] = [
    Rule("LIQ-001", "LIQ-001", "PD Levels", "Validate PDH and PDL levels.", "LIQUIDITY", 25, True),
    Rule("LIQ-002", "LIQ-002", "PW Levels", "Validate PWH and PWL levels.", "LIQUIDITY", 25, True),
    Rule("LIQ-003", "LIQ-003", "H4 Swings", "Validate H4 swing high/low detection.", "LIQUIDITY", 25, True),
    Rule("LIQ-004", "LIQ-004", "Nearest Liquidity", "Validate nearest BSL/SSL mapping.", "LIQUIDITY", 25, False),
]

LIQUIDITY_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in LIQUIDITY_RULES}
