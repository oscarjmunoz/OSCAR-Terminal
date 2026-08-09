from __future__ import annotations

from app.opportunity.engine import OpportunityEngine
from app.opportunity.models import MarketSummary
from app.opportunity.models import OpportunityResult
from app.opportunity.models import RecommendedAction
from app.opportunity.ranking import OpportunityRanking
from app.opportunity.schemas import MarketSummarySchema
from app.opportunity.schemas import OpportunityQueueResponse
from app.opportunity.schemas import OpportunityResultSchema
from app.scanner.service import ScannerService


class OpportunityService:

    def __init__(
        self,
        scanner_service: ScannerService,
        engine: OpportunityEngine | None = None,
        ranking: OpportunityRanking | None = None,
    ):
        self._scanner_service = scanner_service
        self._engine = engine or OpportunityEngine()
        self._ranking = ranking or OpportunityRanking()

    def get_queue(self) -> OpportunityQueueResponse:
        snapshots = self._scanner_service.list_opportunities()

        if not snapshots:
            snapshots = self._scanner_service.refresh_opportunities()

        results = self._engine.evaluate_many(snapshots)
        queue = self._ranking.build_queue(results)

        summary = self._market_summary(results)

        return OpportunityQueueResponse(
            market_summary=MarketSummarySchema(
                total_assets=summary.total_assets,
                ignored=summary.ignored,
                watching=summary.watching,
                preparing=summary.preparing,
                ready=summary.ready,
                active=summary.active,
                last_scan=summary.last_scan,
            ),
            opportunity_queue=[
                OpportunityResultSchema(
                    symbol=item.symbol,
                    timeframe=item.timeframe,
                    bias=item.bias,
                    structure=item.structure,
                    liquidity_target=item.liquidity_target,
                    current_stage=item.current_stage,
                    opportunity_score=item.opportunity_score,
                    institutional_score=item.institutional_score,
                    execution_quality=item.execution_quality,
                    priority=item.priority,
                    estimated_eta=item.estimated_eta,
                    decision_summary=item.decision_summary,
                    recommended_action=item.recommended_action,
                    last_update=item.last_update,
                )
                for item in queue
            ],
        )

    @staticmethod
    def _market_summary(results: list[OpportunityResult]) -> MarketSummary:
        total_assets = len(results)
        ignored = sum(1 for item in results if item.recommended_action == RecommendedAction.IGNORE)
        watching = sum(
            1
            for item in results
            if item.recommended_action in {RecommendedAction.MONITOR, RecommendedAction.WATCH}
        )
        preparing = sum(1 for item in results if item.recommended_action == RecommendedAction.PREPARE)
        ready = sum(1 for item in results if item.recommended_action == RecommendedAction.READY)
        active = sum(1 for item in results if item.recommended_action == RecommendedAction.ACTIVE)

        last_scan = max((item.last_update for item in results), default=None)

        return MarketSummary(
            total_assets=total_assets,
            ignored=ignored,
            watching=watching,
            preparing=preparing,
            ready=ready,
            active=active,
            last_scan=last_scan,
        )
