from __future__ import annotations

from app.core.Rule import Rule


PREMIUM_DISCOUNT_RULES: list[Rule] = [
    Rule("PD-001", "PD-001", "Range Valid", "Range high must be above range low.", "PREMIUM_DISCOUNT", 20, True),
    Rule("PD-002", "PD-002", "Price In Range", "Price must stay inside dealing range.", "PREMIUM_DISCOUNT", 20, True),
    Rule("PD-003", "PD-003", "Zone Classified", "Zone must be premium/discount/equilibrium.", "PREMIUM_DISCOUNT", 20, True),
    Rule("PD-004", "PD-004", "Flag Coherence", "Zone flags must be mutually exclusive.", "PREMIUM_DISCOUNT", 20, False),
    Rule("PD-005", "PD-005", "Bias Alignment", "Bias must align with zone location.", "PREMIUM_DISCOUNT", 20, True),
]

PREMIUM_DISCOUNT_RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in PREMIUM_DISCOUNT_RULES}
