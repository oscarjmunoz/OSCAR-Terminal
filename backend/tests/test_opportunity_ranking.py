from datetime import datetime, timezone

from app.opportunity.models import EstimatedEta
from app.opportunity.models import OpportunityPriority
from app.opportunity.models import OpportunityResult
from app.opportunity.models import OpportunityStage
from app.opportunity.models import RecommendedAction
from app.opportunity.ranking import OpportunityRanking
from app.opportunity.service import OpportunityService


class FakeScannerService:
    def __init__(self, snapshots):
        self._snapshots = snapshots

    def list_opportunities(self):
        return self._snapshots

    def refresh_opportunities(self):
        return self._snapshots


class FakeEngine:
    def __init__(self, results):
        self._results = results

    def evaluate_many(self, _snapshots):
        return self._results


def _result(
    symbol: str,
    priority: OpportunityPriority,
    action: RecommendedAction,
    opp: float,
    inst: float,
    exe: float,
):
    return OpportunityResult(
        symbol=symbol,
        timeframe="M5",
        bias="BULLISH",
        structure="BULLISH|BOS=1|CHOCH=1|MSS=1",
        liquidity_target="BUY_SIDE_LIQUIDITY",
        current_stage=OpportunityStage.EXECUTION_WINDOW,
        opportunity_score=opp,
        institutional_score=inst,
        execution_quality=exe,
        priority=priority,
        estimated_eta=EstimatedEta.NOW,
        decision_summary=f"Summary {symbol}",
        recommended_action=action,
        last_update=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
    )


def test_ranking_excludes_ignore_and_sorts_by_requested_order():
    ranking = OpportunityRanking()

    queue = ranking.build_queue(
        [
            _result("EURUSD", OpportunityPriority.HIGH, RecommendedAction.READY, 80, 70, 75),
            _result("USDJPY", OpportunityPriority.CRITICAL, RecommendedAction.ACTIVE, 60, 60, 60),
            _result("XAUUSD", OpportunityPriority.IGNORE, RecommendedAction.IGNORE, 99, 99, 99),
            _result("GBPUSD", OpportunityPriority.HIGH, RecommendedAction.READY, 82, 71, 70),
        ]
    )

    assert [item.symbol for item in queue] == ["USDJPY", "GBPUSD", "EURUSD"]
    assert all(item.recommended_action != RecommendedAction.IGNORE for item in queue)


def test_service_builds_queue_and_market_summary():
    results = [
        _result("EURUSD", OpportunityPriority.HIGH, RecommendedAction.READY, 80, 70, 75),
        _result("USDJPY", OpportunityPriority.MEDIUM, RecommendedAction.WATCH, 65, 60, 55),
        _result("XAUUSD", OpportunityPriority.LOW, RecommendedAction.PREPARE, 55, 54, 53),
        _result("NAS100", OpportunityPriority.IGNORE, RecommendedAction.IGNORE, 20, 20, 20),
        _result("US30", OpportunityPriority.CRITICAL, RecommendedAction.ACTIVE, 85, 84, 83),
    ]

    service = OpportunityService(
        scanner_service=FakeScannerService(snapshots=[object()]),
        engine=FakeEngine(results=results),
        ranking=OpportunityRanking(),
    )

    response = service.get_queue()

    assert response.market_summary.total_assets == 5
    assert response.market_summary.ignored == 1
    assert response.market_summary.watching == 1
    assert response.market_summary.preparing == 1
    assert response.market_summary.ready == 1
    assert response.market_summary.active == 1
    assert len(response.opportunity_queue) == 4
