from __future__ import annotations

from app.core.Rule import Rule
from app.rules.ContextRules import CONTEXT_RULES_BY_ID
from app.rules.EntryRules import ENTRY_RULES_BY_ID
from app.rules.IEZRules import IEZ_RULES_BY_ID
from app.rules.LiquidityRules import LIQUIDITY_RULES_BY_ID
from app.rules.ManagementRules import MANAGEMENT_RULES_BY_ID
from app.rules.MSSRules import MSS_RULES_BY_ID
from app.rules.PremiumDiscountRules import PREMIUM_DISCOUNT_RULES_BY_ID
from app.rules.RiskRules import RISK_RULES_BY_ID
from app.rules.StructureRules import STRUCTURE_RULES_BY_ID


RULE_REGISTRY: dict[str, Rule] = {
    **CONTEXT_RULES_BY_ID,
    **LIQUIDITY_RULES_BY_ID,
    **STRUCTURE_RULES_BY_ID,
    **PREMIUM_DISCOUNT_RULES_BY_ID,
    **MSS_RULES_BY_ID,
    **IEZ_RULES_BY_ID,
    **ENTRY_RULES_BY_ID,
    **RISK_RULES_BY_ID,
    **MANAGEMENT_RULES_BY_ID,
}


def get_rule(rule_id: str) -> Rule:
    if rule_id not in RULE_REGISTRY:
        raise KeyError(f"Rule not found in registry: {rule_id}")

    return RULE_REGISTRY[rule_id]
