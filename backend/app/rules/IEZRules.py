from __future__ import annotations

from app.core.Rule import Rule


IEZ_RULES: list[Rule] = [
    Rule("IEZ-001", "IEZ-001", "Direction Defined", "Direction must be bullish or bearish.", "IEZ", 15, True),
    Rule("IEZ-002", "IEZ-002", "Zone Boundaries", "Entry zone boundaries must exist.", "IEZ", 14, True),
    Rule("IEZ-003", "IEZ-003", "Zone Coherence", "Entry zone high must be above low.", "IEZ", 14, True),
    Rule("IEZ-004", "IEZ-004", "Price In Zone", "Current price must be inside zone.", "IEZ", 14, True),
    Rule("IEZ-005", "IEZ-005", "Directional Location", "Direction must align with premium/discount location.", "IEZ", 14, True),
    Rule("IEZ-006", "IEZ-006", "Confluence", "FVG and OB confluence must be present.", "IEZ", 14, True),
    Rule("IEZ-007", "IEZ-007", "Context Alignment", "Liquidity, MSS, and timeframe alignment must be present.", "IEZ", 15, True),
]

IEZ_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in IEZ_RULES}
