from __future__ import annotations

from app.core.Rule import Rule


STRUCTURE_RULES: list[Rule] = [
    Rule("STR-001", "STR-001", "Trend Known", "Trend must be known.", "STRUCTURE", 12, True),
    Rule("STR-002", "STR-002", "Swings Present", "Swing high and low must exist.", "STRUCTURE", 12, True),
    Rule("STR-003", "STR-003", "Swing Importance", "Swing importance must be classified.", "STRUCTURE", 12, False),
    Rule("STR-004", "STR-004", "Range Coherence", "Swing high must be above swing low.", "STRUCTURE", 12, True),
    Rule("STR-005", "STR-005", "Break Event", "BOS or CHOCH must exist.", "STRUCTURE", 13, True),
    Rule("STR-006", "STR-006", "Direction Coherence", "Break direction must match trend.", "STRUCTURE", 13, True),
    Rule("STR-007", "STR-007", "Sweep + Displacement", "Sweep and displacement must confirm.", "STRUCTURE", 13, True),
    Rule("STR-008", "STR-008", "Timeframe Alignment", "Timeframes must be aligned.", "STRUCTURE", 13, True),
]

STRUCTURE_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in STRUCTURE_RULES}
