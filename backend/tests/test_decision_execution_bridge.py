from fastapi.testclient import TestClient

from app.journal.service import JournalService
from app.main import app
from app.playbook.models import PlaybookSetupConditions
from app.playbook.models import PlaybookSetupCreate
from app.playbook.router import get_playbook_service
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
from app.schemas.decision_execution_bridge import BridgeAction
from app.schemas.decision_execution_bridge import DecisionExecutionBridgeRequest
from app.schemas.decision_execution_bridge import ExecutionMode
from app.schemas.decision_execution_bridge import PaperOrderStatus
from app.schemas.decision_execution_bridge import PaperPositionStatus
from app.schemas.trade import TradeResult
from app.services.paper_execution_service import PaperExecutionService
from app.services.decision_execution_bridge import DecisionExecutionBridge
from app.services import decision_execution_bridge as bridge_module


class FakeTradeExecutor:
    def __init__(self, success: bool = True):
        self.success = success
        self.calls = []

    def executeBuy(self, decision: DecisionContext) -> TradeResult:
        self.calls.append(("BUY", decision))
        return TradeResult(success=self.success, ticket=1001 if self.success else None, price=decision.price, volume=decision.volume)

    def executeSell(self, decision: DecisionContext) -> TradeResult:
        self.calls.append(("SELL", decision))
        return TradeResult(success=self.success, ticket=1002 if self.success else None, price=decision.price, volume=decision.volume)


def build_report(
    *,
    side: TradeSide = TradeSide.BUY,
    recommendation: RecommendationType | None = None,
    rr: float = 2.5,
    score: int = 85,
    price: float | None = 1.0860,
    sl: float | None = None,
    tp: float | None = None,
    volume: float = 0.10,
) -> DecisionReport:
    if sl is None:
        sl = 1.0810 if side == TradeSide.BUY else 1.0910
    if tp is None:
        risk_distance = abs(price - sl) if price is not None else 0.0050
        if side == TradeSide.BUY:
            tp = price + (risk_distance * rr) if price is not None else 1.0985
        else:
            tp = price - (risk_distance * rr) if price is not None else 1.0735

    context = DecisionContext(
        symbol="EURUSD.pro",
        side=side,
        volume=volume,
        sl=sl,
        tp=tp,
        price=price,
    )
    final_recommendation = recommendation or (RecommendationType.BUY if side == TradeSide.BUY else RecommendationType.SELL)

    return DecisionReport(
        context=context,
        market_bias=MarketBiasReport(
            bias=MarketBias.BULLISH if side == TradeSide.BUY else MarketBias.BEARISH,
            explanation="Bias aligned",
        ),
        institutional_score=InstitutionalScoreReport(score=score, confidence=0.86, quality_level=QualityLevel.A),
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
            ConfluenceItem(name="BOS confirmed", detected=True, importance=ImportanceLevel.HIGH, explanation="BOS present"),
        ],
        risk_assessment=RiskAssessmentReport(
            rr_expected=rr,
            risk="LOW",
            risk_percent=0.5,
            volatility=8.0,
            setup_quality=QualityLevel.A,
        ),
        execution_checklist=[
            ChecklistItem(label="Liquidity taken", checked=True, explanation="Sweep detected"),
            ChecklistItem(label="Risk valid", checked=True, explanation="RR acceptable"),
        ],
        final_recommendation=FinalRecommendation(
            recommendation=final_recommendation,
            explanation="Institutional alignment confirmed",
        ),
        narrative="Sesgo, liquidez y estructura convergen en una decisión clara.",
    )


def create_playbook_service() -> PlaybookService:
    service = PlaybookService(journal_service=JournalService())
    service.createSetup(
        PlaybookSetupCreate(
            name="Bridge Playbook",
            description="Valid bridge continuation",
            category="INTRADAY",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BULLISH,
                minimumInstitutionalScore=80,
                allowedRecommendations=[RecommendationType.BUY],
            ),
        )
    )
    service.createSetup(
        PlaybookSetupCreate(
            name="Bridge Sell Playbook",
            description="Valid bridge reversal",
            category="INTRADAY",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BEARISH,
                minimumInstitutionalScore=80,
                allowedRecommendations=[RecommendationType.SELL],
            ),
        )
    )
    return service


def build_bridge(*, dispatch_enabled: bool = False, trade_success: bool = True, playbook_service: PlaybookService | None = None):
    return DecisionExecutionBridge(
        playbook_service=playbook_service or create_playbook_service(),
        journal_service=JournalService(),
        trade_executor=FakeTradeExecutor(success=trade_success),
        dispatch_enabled=dispatch_enabled,
    )


def test_buy_decision_prepares_execution():
    bridge = build_bridge()

    result = bridge.execute(DecisionExecutionBridgeRequest(decisionReport=build_report(side=TradeSide.BUY)))

    assert result.finalAction == BridgeAction.PREPARE
    assert result.executionPreparation.result is not None
    assert result.executionPreparation.result.side.value == "BUY"


def test_sell_decision_prepares_execution():
    bridge = build_bridge()

    result = bridge.execute(DecisionExecutionBridgeRequest(decisionReport=build_report(side=TradeSide.SELL)))

    assert result.finalAction == BridgeAction.PREPARE
    assert result.executionPreparation.result is not None
    assert result.executionPreparation.result.side.value == "SELL"


def test_wait_decision_requires_review():
    bridge = build_bridge()

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY, recommendation=RecommendationType.WAIT)
        )
    )

    assert result.finalAction == BridgeAction.REVIEW
    assert any("WAIT" in reason for reason in result.safetyGate.reasons)


def test_no_trade_decision_is_blocked():
    bridge = build_bridge()

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY, recommendation=RecommendationType.NO_TRADE)
        )
    )

    assert result.finalAction == BridgeAction.BLOCK
    assert any("NO_TRADE" in reason for reason in result.safetyGate.reasons)


def test_insufficient_rr_is_blocked():
    bridge = build_bridge()

    result = bridge.execute(DecisionExecutionBridgeRequest(decisionReport=build_report(rr=1.5)))

    assert result.finalAction == BridgeAction.BLOCK
    assert any("below minimum" in reason for reason in result.safetyGate.reasons)


def test_failed_execution_validation_is_blocked(monkeypatch):
    original_prepare = bridge_module.ExecutionService.prepare

    def fake_prepare(_request):
        result = original_prepare(_request)
        return result.model_copy(
            update={
                "validation_results": [
                    item.model_copy(update={"status": "FAIL", "message": "Validation failed"})
                    for item in result.validation_results
                ],
                "execution_status": bridge_module.ExecutionStatus.REVIEW,
            }
        )

    monkeypatch.setattr(bridge_module.ExecutionService, "prepare", staticmethod(fake_prepare))
    bridge = build_bridge()

    result = bridge.execute(DecisionExecutionBridgeRequest(decisionReport=build_report()))

    assert result.finalAction == BridgeAction.BLOCK
    assert "Execution validation contains failures" in result.safetyGate.reasons


def test_missing_required_execution_data_requires_review():
    bridge = build_bridge()

    result = bridge.execute(DecisionExecutionBridgeRequest(decisionReport=build_report(price=None)))

    assert result.finalAction == BridgeAction.REVIEW
    assert "price" in result.executionPreparation.missingRequiredFields


def test_playbook_mismatch_requires_review():
    playbook_service = PlaybookService(journal_service=JournalService())
    playbook_service.createSetup(
        PlaybookSetupCreate(
            name="Sell Only",
            description="Requires bearish continuation",
            category="INTRADAY",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BEARISH,
                minimumInstitutionalScore=80,
                allowedRecommendations=[RecommendationType.SELL],
            ),
        )
    )
    bridge = build_bridge(playbook_service=playbook_service)

    result = bridge.execute(DecisionExecutionBridgeRequest(decisionReport=build_report(side=TradeSide.BUY, score=85)))

    assert result.finalAction == BridgeAction.REVIEW
    assert any("playbook" in reason.lower() for reason in result.safetyGate.reasons)


def test_dispatch_is_not_invoked_when_safety_gate_disabled():
    bridge = build_bridge(dispatch_enabled=False)

    result = bridge.execute(
        DecisionExecutionBridgeRequest(decisionReport=build_report(), dispatch=True)
    )

    assert result.finalAction == BridgeAction.PREPARE
    assert result.executionBoundary.executionMode == ExecutionMode.LIVE
    assert result.executionBoundary.attempted is False
    assert result.executionBoundary.status.value == "DISABLED"


def test_dispatch_invokes_trade_executor_only_when_gate_passes():
    bridge = build_bridge(dispatch_enabled=True)

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(),
            dispatch=True,
            timeframe="M5",
            session="LONDON",
        )
    )

    assert result.finalAction == BridgeAction.DISPATCH
    assert result.executionBoundary.attempted is True
    assert result.executionBoundary.tradeResult is not None
    assert result.executionBoundary.journalEntry is not None


def test_journal_entry_is_only_created_after_successful_dispatch():
    bridge = build_bridge(dispatch_enabled=True, trade_success=False)

    result = bridge.execute(
        DecisionExecutionBridgeRequest(decisionReport=build_report(), dispatch=True)
    )

    assert result.executionBoundary.attempted is True
    assert result.executionBoundary.journalEntry is None


def test_paper_mode_produces_paper_order_and_open_position():
    bridge = build_bridge(dispatch_enabled=True)

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.executionBoundary.executionMode == ExecutionMode.PAPER
    assert result.executionBoundary.attempted is True
    assert result.executionBoundary.paperExecution is not None
    assert result.executionBoundary.paperExecution.order.status == PaperOrderStatus.FILLED
    assert result.executionBoundary.paperExecution.position.status == PaperPositionStatus.OPEN
    assert result.executionBoundary.tradeResult is None


def test_paper_mode_creates_journal_entry_and_links_position():
    journal_service = JournalService()
    paper_execution_service = PaperExecutionService()
    bridge = DecisionExecutionBridge(
        playbook_service=create_playbook_service(),
        journal_service=journal_service,
        trade_executor=FakeTradeExecutor(success=True),
        paper_execution_service=paper_execution_service,
        dispatch_enabled=True,
    )

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
            timeframe="M5",
            session="LONDON",
            notes="confirmed paper",
            tags=["paper", "hd-016b"],
        )
    )

    assert result.executionBoundary.paperExecution is not None
    journal_entry_id = result.executionBoundary.paperExecution.position.journal_entry_id
    assert journal_entry_id is not None
    assert journal_service.getEntry(journal_entry_id).tradeOutcome.value == "PENDING"


def test_unconfirmed_paper_mode_creates_no_position_in_shared_service():
    paper_execution_service = PaperExecutionService()
    bridge = DecisionExecutionBridge(
        playbook_service=create_playbook_service(),
        journal_service=JournalService(),
        trade_executor=FakeTradeExecutor(success=True),
        paper_execution_service=paper_execution_service,
        dispatch_enabled=True,
    )

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
            confirmed=False,
        )
    )

    assert result.executionBoundary.attempted is False
    assert paper_execution_service.state.positions == {}


def test_blocked_paper_mode_creates_no_position_in_shared_service():
    paper_execution_service = PaperExecutionService()
    bridge = DecisionExecutionBridge(
        playbook_service=create_playbook_service(),
        journal_service=JournalService(),
        trade_executor=FakeTradeExecutor(success=True),
        paper_execution_service=paper_execution_service,
        dispatch_enabled=True,
    )

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY, recommendation=RecommendationType.NO_TRADE),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.executionBoundary.attempted is False
    assert paper_execution_service.state.positions == {}


def test_paper_order_transitions_prepared_submitted_filled():
    bridge = build_bridge(dispatch_enabled=True)

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.SELL),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.executionBoundary.paperExecution is not None
    assert result.executionBoundary.paperExecution.order_status_flow == [
        PaperOrderStatus.PREPARED,
        PaperOrderStatus.SUBMITTED,
        PaperOrderStatus.FILLED,
    ]


def test_paper_fill_price_is_deterministic_from_preparation_entry():
    report = build_report(side=TradeSide.BUY, price=1.0862)
    bridge = build_bridge(dispatch_enabled=True)

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=report,
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.executionBoundary.paperExecution is not None
    assert result.executionPreparation.result is not None
    assert (
        result.executionBoundary.paperExecution.deterministic_fill_price
        == result.executionPreparation.result.entry
    )


def test_paper_mode_never_calls_trade_executor():
    trade_executor = FakeTradeExecutor(success=True)
    bridge = DecisionExecutionBridge(
        playbook_service=create_playbook_service(),
        journal_service=JournalService(),
        trade_executor=trade_executor,
        dispatch_enabled=True,
    )

    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.executionBoundary.attempted is True
    assert trade_executor.calls == []


def test_paper_mode_never_calls_mt5_resolution_paths(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise AssertionError("MT5-linked resolver should not be called in PAPER mode")

    monkeypatch.setattr(bridge_module.ExecutionService, "_resolve_account_balance", staticmethod(_raise))
    monkeypatch.setattr(bridge_module.ExecutionService, "_resolve_leverage", staticmethod(_raise))
    monkeypatch.setattr(bridge_module.ExecutionService, "_resolve_symbol_info", staticmethod(_raise))

    bridge = build_bridge(dispatch_enabled=True)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.executionBoundary.attempted is True
    assert result.executionBoundary.status.value == "SUCCESS"


def test_paper_mode_without_confirmation_creates_no_order_or_position():
    bridge = build_bridge(dispatch_enabled=True)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
        )
    )

    assert result.finalAction == BridgeAction.REVIEW
    assert result.executionBoundary.attempted is False
    assert result.executionBoundary.paperExecution is None
    assert any("confirmation" in reason.lower() for reason in result.safetyGate.reasons)


def test_paper_mode_confirmation_false_creates_no_order_or_position():
    bridge = build_bridge(dispatch_enabled=True)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY),
            executionMode=ExecutionMode.PAPER,
            confirmed=False,
        )
    )

    assert result.finalAction == BridgeAction.REVIEW
    assert result.executionBoundary.attempted is False
    assert result.executionBoundary.paperExecution is None


def test_wait_decision_with_confirmation_true_in_paper_mode_is_blocked_from_execution():
    bridge = build_bridge(dispatch_enabled=True)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY, recommendation=RecommendationType.WAIT),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.finalAction in {BridgeAction.REVIEW, BridgeAction.BLOCK}
    assert result.executionBoundary.attempted is False
    assert result.executionBoundary.paperExecution is None


def test_no_trade_decision_with_confirmation_true_in_paper_mode_is_blocked():
    bridge = build_bridge(dispatch_enabled=True)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY, recommendation=RecommendationType.NO_TRADE),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.finalAction == BridgeAction.BLOCK
    assert result.executionBoundary.attempted is False
    assert result.executionBoundary.paperExecution is None


def test_invalid_preparation_with_confirmation_true_in_paper_mode_is_blocked_from_execution():
    bridge = build_bridge(dispatch_enabled=True)
    result = bridge.execute(
        DecisionExecutionBridgeRequest(
            decisionReport=build_report(side=TradeSide.BUY, price=None),
            executionMode=ExecutionMode.PAPER,
            confirmed=True,
        )
    )

    assert result.finalAction in {BridgeAction.REVIEW, BridgeAction.BLOCK}
    assert result.executionBoundary.attempted is False
    assert result.executionBoundary.paperExecution is None


def test_api_decision_execute_exposes_orchestration_result():
    playbook_service = create_playbook_service()
    bridge = DecisionExecutionBridge(
        playbook_service=playbook_service,
        journal_service=JournalService(),
        trade_executor=FakeTradeExecutor(),
        dispatch_enabled=False,
    )

    from app.api.decision import get_decision_execution_bridge

    app.dependency_overrides[get_playbook_service] = lambda: playbook_service
    app.dependency_overrides[get_decision_execution_bridge] = lambda: bridge

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/decision/execute",
            json=DecisionExecutionBridgeRequest(decisionReport=build_report()).model_dump(mode="json"),
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["decision"]["report"]["context"]["symbol"] == "EURUSD.pro"
        assert payload["playbookResult"]["permitsContinuation"] is True
        assert payload["finalAction"] == "PREPARE"
    finally:
        app.dependency_overrides.clear()