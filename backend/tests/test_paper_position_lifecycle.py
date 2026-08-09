from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.analytics.service import AnalyticsService
from app.api.decision import get_decision_execution_bridge
from app.journal.router import get_journal_service
from app.journal.service import JournalService
from app.main import app
from app.playbook.router import get_playbook_service
from app.playbook.models import PlaybookSetupConditions
from app.playbook.models import PlaybookSetupCreate
from app.playbook.service import PlaybookService
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
from app.schemas.decision_execution_bridge import DecisionExecutionBridgeRequest
from app.schemas.decision_execution_bridge import ExecutionMode
from app.services.decision_execution_bridge import DecisionExecutionBridge
from app.services.paper_execution_service import PaperExecutionService
from app.services import paper_execution_service as paper_execution_service_module


def build_report(side: TradeSide = TradeSide.BUY) -> DecisionReport:
    entry_price = 1.0860 if side == TradeSide.BUY else 1.0880
    stop_loss = 1.0810 if side == TradeSide.BUY else 1.0920
    take_profit = 1.0960 if side == TradeSide.BUY else 1.0780
    return DecisionReport(
        context=DecisionContext(
            symbol="EURUSD.pro",
            side=side,
            volume=0.10,
            sl=stop_loss,
            tp=take_profit,
            price=entry_price,
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
        execution_checklist=[ChecklistItem(label="Risk valid", checked=True, explanation="RR acceptable")],
        final_recommendation=FinalRecommendation(
            recommendation=RecommendationType.BUY if side == TradeSide.BUY else RecommendationType.SELL,
            explanation="Institutional alignment confirmed",
        ),
        narrative="Paper lifecycle snapshot.",
    )


def build_bridge(journal_service: JournalService, paper_execution_service: PaperExecutionService) -> DecisionExecutionBridge:
    playbook_service = PlaybookService(journal_service=journal_service)
    playbook_service.createSetup(
        PlaybookSetupCreate(
            name="Paper Lifecycle Playbook",
            description="Allows deterministic paper continuation",
            category="INTRADAY",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BULLISH,
                minimumInstitutionalScore=80,
                allowedRecommendations=[RecommendationType.BUY],
            ),
        )
    )
    playbook_service.createSetup(
        PlaybookSetupCreate(
            name="Paper Lifecycle Sell Playbook",
            description="Allows deterministic paper reversal",
            category="INTRADAY",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BEARISH,
                minimumInstitutionalScore=80,
                allowedRecommendations=[RecommendationType.SELL],
            ),
        )
    )

    return DecisionExecutionBridge(
        playbook_service=playbook_service,
        journal_service=journal_service,
        paper_execution_service=paper_execution_service,
        dispatch_enabled=True,
    )


def open_paper_position(journal_service: JournalService, paper_execution_service: PaperExecutionService, side: TradeSide = TradeSide.BUY):
    bridge = build_bridge(journal_service, paper_execution_service)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=side),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
            timeframe="M5",
            session="LONDON",
        )
    )
    assert result.executionBoundary.paperExecution is not None
    return result.executionBoundary.paperExecution.position.position_id


def test_paper_position_close_updates_journal_outcome_via_api(monkeypatch):
    journal_service = JournalService()
    paper_execution_service = PaperExecutionService()
    position_id = open_paper_position(journal_service, paper_execution_service)
    monkeypatch.setattr(
        paper_execution_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0880, ask=1.0882, spread=2.0)),
    )

    app.dependency_overrides[get_journal_service] = lambda: journal_service
    from app.services.paper_execution_service import get_paper_execution_service

    app.dependency_overrides[get_paper_execution_service] = lambda: paper_execution_service

    try:
        client = TestClient(app)

        update_response = client.post(f"/api/v1/paper/positions/{position_id}/update")
        assert update_response.status_code == 200
        assert update_response.json()["mark_price"] == 1.088

        close_response = client.post(f"/api/v1/paper/positions/{position_id}/close")
        assert close_response.status_code == 200
        payload = close_response.json()
        assert payload["close_price"] == 1.088
        assert payload["realized_pnl"] == 20.0
        assert payload["realized_rr"] == 0.4
        assert payload["outcome"] == "WIN"

        journal_entry_id = payload["journal_entry_id"]
        journal_entry = journal_service.getEntry(journal_entry_id)
        assert journal_entry.tradeOutcome.value == "WIN"
        assert journal_entry.profitLoss == 20.0
        assert journal_entry.realizedRR == 0.4

        second_close = client.post(f"/api/v1/paper/positions/{position_id}/close")
        assert second_close.status_code == 200
        assert second_close.json()["already_closed"] is True
    finally:
        app.dependency_overrides.clear()


def test_close_nonexistent_paper_position_returns_404():
    journal_service = JournalService()
    paper_execution_service = PaperExecutionService()
    app.dependency_overrides[get_journal_service] = lambda: journal_service
    from app.services.paper_execution_service import get_paper_execution_service

    app.dependency_overrides[get_paper_execution_service] = lambda: paper_execution_service

    try:
        client = TestClient(app)
        response = client.post("/api/v1/paper/positions/paper-position-missing/close")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_analytics_sees_closed_paper_trade(monkeypatch):
    journal_service = JournalService()
    paper_execution_service = PaperExecutionService()
    position_id = open_paper_position(journal_service, paper_execution_service)
    monkeypatch.setattr(
        paper_execution_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0880, ask=1.0882, spread=2.0)),
    )

    close_result = paper_execution_service.close_position(position_id=position_id, journal_service=journal_service)
    analytics_service = AnalyticsService(
        journal_service=journal_service,
        playbook_service=PlaybookService(journal_service=journal_service),
    )

    summary = analytics_service.getSummary()

    assert close_result.outcome == "WIN"
    assert summary.totalTrades == 1
    assert summary.wins == 1
    assert summary.losses == 0
    assert summary.averageProfit == 20.0
    assert summary.averageRR == 0.4
    assert summary.expectancy == 20.0