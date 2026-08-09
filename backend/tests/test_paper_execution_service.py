from types import SimpleNamespace

import pytest

from app.journal.models import TradeOutcome
from app.journal.service import JournalService
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.decision_center import ChecklistItem
from app.schemas.decision_center import ConfluenceItem
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import FinalRecommendation
from app.schemas.decision_center import ImportanceLevel
from app.schemas.decision_center import InstitutionalScoreReport
from app.schemas.decision_center import InstitutionalZonesReport
from app.schemas.decision_center import LiquidityReport
from app.schemas.decision_center import MarketBias
from app.schemas.decision_center import MarketBiasReport
from app.schemas.decision_center import MarketStructureReport
from app.schemas.decision_center import QualityLevel
from app.schemas.decision_center import RecommendationType
from app.schemas.decision_center import RiskAssessmentReport
from app.schemas.decision_center import ZoneStatus
from app.schemas.decision_execution_bridge import PaperOrderStatus
from app.schemas.decision_execution_bridge import PaperPositionStatus
from app.services import paper_execution_service as paper_execution_service_module
from app.services.paper_execution_service import PaperExecutionService
from app.services.paper_execution_service import PaperPositionNotFoundError


def build_report(side: TradeSide = TradeSide.BUY) -> DecisionReport:
    return DecisionReport(
        context=DecisionContext(
            symbol="EURUSD.pro",
            side=side,
            volume=0.10,
            sl=1.0810 if side == TradeSide.BUY else 1.0920,
            tp=1.0960 if side == TradeSide.BUY else 1.0780,
            price=1.0860 if side == TradeSide.BUY else 1.0880,
        ),
        market_bias=MarketBiasReport(
            bias=MarketBias.BULLISH if side == TradeSide.BUY else MarketBias.BEARISH,
            explanation="Bias aligned",
        ),
        institutional_score=InstitutionalScoreReport(score=85, confidence=0.86, quality_level=QualityLevel.A),
        liquidity=LiquidityReport(
            buy_liquidity=1200,
            sell_liquidity=900,
            liquidity_taken=300,
            pending_liquidity=150,
            explanation="Liquidity favors continuation",
        ),
        market_structure=MarketStructureReport(
            trend="BULLISH" if side == TradeSide.BUY else "BEARISH",
            bos=True,
            choch=False,
            mss=True,
            explanation="Structure confirmed",
        ),
        institutional_zones=InstitutionalZonesReport(
            order_block=ZoneStatus(active=True, explanation="Order block active"),
            breaker=ZoneStatus(active=False, explanation="Breaker inactive"),
            mitigation=ZoneStatus(active=True, explanation="Mitigation active"),
            fvg=ZoneStatus(active=True, explanation="FVG active"),
            premium=ZoneStatus(active=side == TradeSide.SELL, explanation="Premium zone"),
            discount=ZoneStatus(active=side == TradeSide.BUY, explanation="Discount zone"),
        ),
        confluences=[
            ConfluenceItem(name="Bias aligned", detected=True, importance=ImportanceLevel.HIGH, explanation="Aligned"),
        ],
        risk_assessment=RiskAssessmentReport(
            rr_expected=2.0,
            risk="LOW",
            risk_percent=0.5,
            volatility=8.0,
            setup_quality=QualityLevel.A,
        ),
        execution_checklist=[
            ChecklistItem(label="Risk valid", checked=True, explanation="RR acceptable"),
        ],
        final_recommendation=FinalRecommendation(
            recommendation=RecommendationType.BUY if side == TradeSide.BUY else RecommendationType.SELL,
            explanation="Institutional alignment confirmed",
        ),
        narrative="Paper execution snapshot.",
    )


def test_paper_execution_service_creates_filled_order_and_open_position():
    service = PaperExecutionService()

    result = service.execute(
        decision=DecisionContext(
            symbol="EURUSD.pro",
            side=TradeSide.BUY,
            volume=0.10,
            sl=1.0810,
            tp=1.0960,
            price=1.0860,
        ),
        lot_size=0.10,
        entry_price=1.0860,
        stop_loss=1.0810,
        take_profit=1.0960,
        decision_reference_id="decision-ref-001",
    )

    assert result.order.status == PaperOrderStatus.FILLED
    assert result.position.status == PaperPositionStatus.OPEN
    assert result.position.originating_order_id == result.order.order_id


def test_paper_execution_service_fill_is_deterministic():
    service = PaperExecutionService()

    result = service.execute(
        decision=DecisionContext(
            symbol="EURUSD.pro",
            side=TradeSide.SELL,
            volume=0.20,
            sl=1.0920,
            tp=1.0780,
            price=1.0880,
        ),
        lot_size=0.20,
        entry_price=1.0880,
        stop_loss=1.0920,
        take_profit=1.0780,
    )

    assert result.order_status_flow == [
        PaperOrderStatus.PREPARED,
        PaperOrderStatus.SUBMITTED,
        PaperOrderStatus.FILLED,
    ]
    assert result.deterministic_fill_price == 1.0880
    assert result.position.entry_price == 1.0880


def test_confirmed_paper_open_creates_journal_entry_and_links_position():
    service = PaperExecutionService()
    journal_service = JournalService()
    report = build_report(side=TradeSide.BUY)

    result = service.execute(
        decision=report.context,
        lot_size=0.10,
        entry_price=1.0860,
        stop_loss=1.0810,
        take_profit=1.0960,
        decision_report=report,
        journal_service=journal_service,
        timeframe="M5",
        session="LONDON",
        risk_percent=0.5,
        expected_rr=2.0,
        notes="Confirmed paper trade",
        tags=["hd-016b"],
    )

    assert result.position.journal_entry_id is not None
    entry = journal_service.getEntry(result.position.journal_entry_id)
    assert entry.tradeOutcome == TradeOutcome.PENDING
    assert entry.symbol == "EURUSD.pro"


def test_open_position_mark_to_market_updates_latest_mark_and_unrealized_pnl(monkeypatch):
    service = PaperExecutionService()
    opened = service.execute(
        decision=DecisionContext(
            symbol="EURUSD.pro",
            side=TradeSide.BUY,
            volume=0.10,
            sl=1.0810,
            tp=1.0960,
            price=1.0860,
        ),
        lot_size=0.10,
        entry_price=1.0860,
        stop_loss=1.0810,
        take_profit=1.0960,
    )
    monkeypatch.setattr(
        paper_execution_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0880, ask=1.0882, spread=2.0)),
    )

    updated = service.update_position(position_id=opened.position.position_id)

    assert updated.mark_price == 1.0880
    assert updated.unrealized_pnl == 20.0
    assert updated.position.last_mark_price == 1.0880
    assert updated.position.unrealized_pnl == 20.0


@pytest.mark.parametrize(
    "side,entry_price,stop_loss,bid,ask,expected_close,expected_pnl,expected_rr,expected_outcome",
    [
        (TradeSide.BUY, 1.0860, 1.0810, 1.0880, 1.0882, 1.0880, 20.0, 0.4, TradeOutcome.WIN),
        (TradeSide.SELL, 1.0880, 1.0920, 1.0858, 1.0860, 1.0860, 20.0, 0.5, TradeOutcome.WIN),
        (TradeSide.BUY, 1.0860, 1.0810, 1.0840, 1.0842, 1.0840, -20.0, -0.4, TradeOutcome.LOSS),
        (TradeSide.BUY, 1.0860, 1.0810, 1.0860, 1.0862, 1.0860, 0.0, 0.0, TradeOutcome.BREAK_EVEN),
    ],
)
def test_close_position_realizes_pnl_rr_and_outcome(
    monkeypatch,
    side,
    entry_price,
    stop_loss,
    bid,
    ask,
    expected_close,
    expected_pnl,
    expected_rr,
    expected_outcome,
):
    service = PaperExecutionService()
    journal_service = JournalService()
    report = build_report(side=side)
    opened = service.execute(
        decision=report.context.model_copy(update={"price": entry_price, "sl": stop_loss}),
        lot_size=0.10,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=report.context.tp or entry_price,
        decision_report=report,
        journal_service=journal_service,
        timeframe="M5",
        session="LONDON",
        risk_percent=0.5,
        expected_rr=2.0,
    )
    monkeypatch.setattr(
        paper_execution_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=bid, ask=ask, spread=2.0)),
    )

    closed = service.close_position(position_id=opened.position.position_id, journal_service=journal_service)

    assert closed.close_price == expected_close
    assert closed.realized_pnl == expected_pnl
    assert closed.realized_rr == expected_rr
    assert closed.outcome == expected_outcome.value
    assert closed.position.status == PaperPositionStatus.CLOSED

    journal_entry = journal_service.getEntry(opened.position.journal_entry_id)
    assert journal_entry.tradeOutcome == expected_outcome
    assert journal_entry.profitLoss == expected_pnl
    assert journal_entry.realizedRR == expected_rr


def test_close_position_is_idempotent_and_does_not_duplicate_journal_outcome(monkeypatch):
    service = PaperExecutionService()
    journal_service = JournalService()
    report = build_report(side=TradeSide.BUY)
    opened = service.execute(
        decision=report.context,
        lot_size=0.10,
        entry_price=1.0860,
        stop_loss=1.0810,
        take_profit=1.0960,
        decision_report=report,
        journal_service=journal_service,
        timeframe="M5",
        session="LONDON",
        risk_percent=0.5,
        expected_rr=2.0,
    )
    monkeypatch.setattr(
        paper_execution_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0880, ask=1.0882, spread=2.0)),
    )

    call_count = {"count": 0}
    original_update = journal_service.updateOutcome

    def spy_update(*args, **kwargs):
        call_count["count"] += 1
        return original_update(*args, **kwargs)

    monkeypatch.setattr(journal_service, "updateOutcome", spy_update)

    first = service.close_position(position_id=opened.position.position_id, journal_service=journal_service)
    second = service.close_position(position_id=opened.position.position_id, journal_service=journal_service)

    assert first.already_closed is False
    assert second.already_closed is True
    assert second.realized_pnl == first.realized_pnl
    assert call_count["count"] == 1


def test_close_nonexistent_position_raises_not_found():
    service = PaperExecutionService()

    with pytest.raises(PaperPositionNotFoundError):
        service.close_position(position_id="paper-position-missing")
