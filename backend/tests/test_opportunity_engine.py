from datetime import datetime, timezone

from app.opportunity.engine import OpportunityEngine
from app.opportunity.models import EstimatedEta
from app.opportunity.models import OpportunityStage
from app.opportunity.models import RecommendedAction
from app.scanner.models import OpportunityStage as ScannerStage
from app.scanner.schemas import OpportunitySnapshotSchema


def _snapshot(
    *,
    symbol: str = "EURUSD",
    stage: ScannerStage = ScannerStage.ENTRY_READY,
    health: str = "GREEN",
    bias: str = "BULLISH",
    structure: str = "BULLISH|BOS=1|CHOCH=1|MSS=1",
    institutional_score: float = 80.0,
    execution_quality: float = 70.0,
):
    return OpportunitySnapshotSchema(
        symbol=symbol,
        timeframe="M5",
        bias=bias,
        structure=structure,
        liquidity_target="BUY_SIDE_LIQUIDITY",
        stage=stage,
        institutional_score=institutional_score,
        execution_quality=execution_quality,
        last_update=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        health=health,
        decision_summary="Institutional context aligned with structure and liquidity for trader review.",
    )


def test_engine_maps_stage_and_action_without_trade_signal_words():
    engine = OpportunityEngine()
    result = engine.evaluate(_snapshot())

    assert result.current_stage == OpportunityStage.EXECUTION_WINDOW
    assert result.recommended_action in {
        RecommendedAction.IGNORE,
        RecommendedAction.MONITOR,
        RecommendedAction.WATCH,
        RecommendedAction.PREPARE,
        RecommendedAction.READY,
        RecommendedAction.ACTIVE,
    }
    assert result.recommended_action.value not in {"BUY", "SELL", "LONG", "SHORT"}


def test_engine_ignores_red_health_or_low_score():
    engine = OpportunityEngine()

    result = engine.evaluate(
        _snapshot(
            stage=ScannerStage.BUILDING_CONTEXT,
            health="RED",
            bias="UNKNOWN",
            structure="UNKNOWN",
            institutional_score=5.0,
            execution_quality=5.0,
        )
    )

    assert result.recommended_action == RecommendedAction.IGNORE
    assert result.opportunity_score < 35
    assert result.estimated_eta == EstimatedEta.UNKNOWN


def test_engine_eta_mapping_for_waiting_states():
    engine = OpportunityEngine()

    displacement = engine.evaluate(_snapshot(stage=ScannerStage.WAITING_DISPLACEMENT))
    mss = engine.evaluate(_snapshot(stage=ScannerStage.WAITING_MSS))
    sweep = engine.evaluate(_snapshot(stage=ScannerStage.WAITING_SWEEP))

    assert displacement.estimated_eta == EstimatedEta.MIN_15_30
    assert mss.estimated_eta == EstimatedEta.MIN_30_60
    assert sweep.estimated_eta == EstimatedEta.GREATER_THAN_60


def test_scores_are_independent_dimensions():
    engine = OpportunityEngine()

    rich = engine.evaluate(_snapshot())
    weak = engine.evaluate(
        _snapshot(
            stage=ScannerStage.WAITING_LIQUIDITY,
            health="YELLOW",
            bias="UNKNOWN",
            structure="BULLISH|BOS=0|CHOCH=0|MSS=0",
            institutional_score=10.0,
            execution_quality=15.0,
        )
    )

    assert rich.opportunity_score > weak.opportunity_score
    assert rich.institutional_score > weak.institutional_score
    assert rich.execution_quality > weak.execution_quality
