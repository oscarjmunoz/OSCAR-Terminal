from __future__ import annotations

from app.opportunity.models import OpportunityPriority
from app.opportunity.models import OpportunityResult
from app.opportunity.models import RecommendedAction

PRIORITY_ORDER: dict[OpportunityPriority, int] = {
    OpportunityPriority.CRITICAL: 4,
    OpportunityPriority.HIGH: 3,
    OpportunityPriority.MEDIUM: 2,
    OpportunityPriority.LOW: 1,
    OpportunityPriority.IGNORE: 0,
}


class OpportunityRanking:

    @staticmethod
    def build_queue(results: list[OpportunityResult]) -> list[OpportunityResult]:
        filtered = [item for item in results if item.recommended_action != RecommendedAction.IGNORE]

        return sorted(
            filtered,
            key=lambda item: (
                PRIORITY_ORDER[item.priority],
                item.opportunity_score,
                item.institutional_score,
                item.execution_quality,
            ),
            reverse=True,
        )
