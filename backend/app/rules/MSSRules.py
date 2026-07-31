from __future__ import annotations

from app.core.Rule import Rule


MSS_RULES: list[Rule] = [
    Rule("MSS-001", "MSS-001", "Break Confirmed", "Direction and broken level must be present.", "MSS", 17, True),
    Rule("MSS-002", "MSS-002", "Liquidity Sweep", "Liquidity sweep must be confirmed.", "MSS", 17, True),
    Rule("MSS-003", "MSS-003", "Displacement", "Displacement must be confirmed.", "MSS", 16, True),
    Rule("MSS-004", "MSS-004", "FVG Created", "FVG must exist after shift.", "MSS", 16, True),
    Rule("MSS-005", "MSS-005", "Bias Aligned", "Bias must align with MSS direction.", "MSS", 17, True),
    Rule("MSS-006", "MSS-006", "Sweep Direction", "Sweep side must align with direction.", "MSS", 17, True),
]

MSS_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in MSS_RULES}
