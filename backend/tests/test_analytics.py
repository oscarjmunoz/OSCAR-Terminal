import pytest
from fastapi.testclient import TestClient

from app.analytics.service import AnalyticsService
from app.journal.models import JournalEntryCreate
from app.journal.models import JournalOutcomeUpdate
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision
from app.journal.router import get_journal_service
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


def build_report(
    *,
    symbol: str,
    side: TradeSide,
    recommendation: RecommendationType,
    confluences: list[str],
) -> DecisionReport:
    context = DecisionContext(
        symbol=symbol,
        side=side,
        volume=0.10,
        sl=1.0810,
        tp=1.0910,
        price=1.0860,
    )
    bias = MarketBiasReport(
        bias=MarketBias.BULLISH if side == TradeSide.BUY else MarketBias.BEARISH,
        explanation="Bias aligned",
    )
    score = InstitutionalScoreReport(score=82, confidence=0.86, quality_level=QualityLevel.A)
    liquidity = LiquidityReport(
        buy_liquidity=1200,
        sell_liquidity=900,
        liquidity_taken=300,
        pending_liquidity=150,
        explanation="Liquidity favors continuation",
    )
    structure = MarketStructureReport(
        trend="BULLISH" if side == TradeSide.BUY else "BEARISH",
        bos=True,
        choch=False,
        mss=True,
        explanation="Structure confirmed",
    )
    zones = InstitutionalZonesReport(
        order_block=ZoneStatus(active=True, explanation="Order block active"),
        breaker=ZoneStatus(active=False, explanation="Breaker inactive"),
        mitigation=ZoneStatus(active=True, explanation="Mitigation active"),
        fvg=ZoneStatus(active=True, explanation="FVG active"),
        premium=ZoneStatus(active=side == TradeSide.SELL, explanation="Premium zone"),
        discount=ZoneStatus(active=side == TradeSide.BUY, explanation="Discount zone"),
    )
    report_confluences = [
        ConfluenceItem(name=name, detected=True, importance=ImportanceLevel.HIGH, explanation=f"{name} detected")
        for name in confluences
    ]
    checklist = [
        ChecklistItem(label="Liquidity taken", checked=True, explanation="Liquidity sweep detected"),
        ChecklistItem(label="Risk valid", checked=True, explanation="RR acceptable"),
    ]
    risk = RiskAssessmentReport(rr_expected=2.25, risk="LOW", risk_percent=0.42, volatility=8.0, setup_quality=QualityLevel.A)

    return DecisionReport(
        context=context,
        market_bias=bias,
        institutional_score=score,
        liquidity=liquidity,
        market_structure=structure,
        institutional_zones=zones,
        confluences=report_confluences,
        risk_assessment=risk,
        execution_checklist=checklist,
        final_recommendation=FinalRecommendation(recommendation=recommendation, explanation="Deterministic recommendation"),
        narrative="Snapshot reused by downstream modules.",
    )


def build_entry(
    *,
    symbol: str,
    timeframe: str,
    session: str,
    side: TradeSide,
    recommendation: RecommendationType,
    trader_decision: TraderDecision,
    confluences: list[str],
) -> JournalEntryCreate:
    return JournalEntryCreate(
        symbol=symbol,
        timeframe=timeframe,
        session=session,
        entryPrice=1.0860,
        stopLoss=1.0810,
        takeProfit=1.0910,
        positionSize=0.10,
        riskPercent=0.42,
        expectedRR=2.25,
        traderDecision=trader_decision,
        decisionReport=build_report(
            symbol=symbol,
            side=side,
            recommendation=recommendation,
            confluences=confluences,
        ),
        personalNotes="Analytics fixture",
        tags=[session.lower(), timeframe.lower()],
    )


def seed_services() -> tuple[JournalService, PlaybookService, AnalyticsService]:
    journal_service = JournalService()
    playbook_service = PlaybookService(journal_service=journal_service)

    playbook_service.createSetup(
        PlaybookSetupCreate(
            name="Bullish Continuation",
            description="Buy-only setup",
            category="INTRADAY",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BULLISH,
                allowedRecommendations=[RecommendationType.BUY],
            ),
        )
    )
    playbook_service.createSetup(
        PlaybookSetupCreate(
            name="Bearish Reversal",
            description="Sell-only setup",
            category="REVERSAL",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BEARISH,
                allowedRecommendations=[RecommendationType.SELL],
            ),
        )
    )

    first = journal_service.createEntry(
        build_entry(
            symbol="EURUSD.pro",
            timeframe="M5",
            session="LONDON",
            side=TradeSide.BUY,
            recommendation=RecommendationType.BUY,
            trader_decision=TraderDecision.FOLLOWED_OSCAR,
            confluences=["Bias aligned", "London sweep"],
        )
    )
    second = journal_service.createEntry(
        build_entry(
            symbol="GBPUSD.pro",
            timeframe="M15",
            session="NEW_YORK",
            side=TradeSide.SELL,
            recommendation=RecommendationType.SELL,
            trader_decision=TraderDecision.FOLLOWED_OSCAR,
            confluences=["NY reversal", "Breaker touch"],
        )
    )
    third = journal_service.createEntry(
        build_entry(
            symbol="USDJPY.pro",
            timeframe="H1",
            session="ASIA",
            side=TradeSide.BUY,
            recommendation=RecommendationType.WAIT,
            trader_decision=TraderDecision.WAITED,
            confluences=["Asian range"],
        )
    )
    fourth = journal_service.createEntry(
        build_entry(
            symbol="XAUUSD.pro",
            timeframe="H4",
            session="LONDON",
            side=TradeSide.SELL,
            recommendation=RecommendationType.NO_TRADE,
            trader_decision=TraderDecision.CANCELLED,
            confluences=["High impact news"],
        )
    )
    fifth = journal_service.createEntry(
        build_entry(
            symbol="AUDUSD.pro",
            timeframe="D1",
            session="NEW_YORK",
            side=TradeSide.BUY,
            recommendation=RecommendationType.BUY,
            trader_decision=TraderDecision.IGNORED_OSCAR,
            confluences=["Bias aligned", "Daily discount"],
        )
    )

    journal_service.updateOutcome(first.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.WIN, realizedRR=2.5, durationMinutes=120))
    journal_service.updateOutcome(second.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.LOSS, realizedRR=-1.0, durationMinutes=90))
    journal_service.updateOutcome(third.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.BREAK_EVEN, realizedRR=0.0, durationMinutes=45))
    journal_service.updateOutcome(fourth.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.CANCELLED, durationMinutes=15))
    journal_service.updateOutcome(fifth.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.WIN, realizedRR=1.9, durationMinutes=1440))

    analytics_service = AnalyticsService(journal_service=journal_service, playbook_service=playbook_service)
    return journal_service, playbook_service, analytics_service


@pytest.fixture()
def analytics_services():
    return seed_services()


def test_summary_session_timeframe_symbol_and_risk(analytics_services):
    _, _, analytics_service = analytics_services

    summary = analytics_service.getSummary()
    assert summary.totalTrades == 5
    assert summary.wins == 2
    assert summary.losses == 1
    assert summary.breakEven == 1
    assert summary.cancelled == 1
    assert summary.winRate == 40.0
    assert summary.averageRR == 0.85
    assert summary.averageProfit == 2.2
    assert summary.averageLoss == 1.0
    assert summary.expectancy == 0.68
    assert summary.profitFactor == 4.4

    sessions = {item.session: item for item in analytics_service.getSessionStats()}
    assert sessions["ASIA"].trades == 1
    assert sessions["ASIA"].averageRR == 0.0
    assert sessions["ASIA"].averageDuration == 45.0
    assert sessions["LONDON"].trades == 2
    assert sessions["LONDON"].winRate == 50.0
    assert sessions["LONDON"].averageRR == 2.5
    assert sessions["LONDON"].averageDuration == 67.5
    assert sessions["NEW_YORK"].trades == 2
    assert sessions["NEW_YORK"].averageRR == 0.45
    assert sessions["NEW_YORK"].averageDuration == 765.0

    timeframes = {item.timeframe: item for item in analytics_service.getTimeframeStats()}
    assert timeframes["M1"].trades == 0
    assert timeframes["M5"].winRate == 100.0
    assert timeframes["M15"].averageRR == -1.0
    assert timeframes["H1"].averageRR == 0.0
    assert timeframes["H4"].trades == 1

    symbols = {item.symbol: item for item in analytics_service.getSymbolStats()}
    assert symbols["EURUSD.PRO"].trades == 1
    assert symbols["EURUSD.PRO"].winRate == 100.0
    assert symbols["XAUUSD.PRO"].averageRR == 0.0
    assert symbols["XAUUSD.PRO"].averageDuration == 15.0

    risk = analytics_service.getRiskStats()
    assert risk.averageRisk == 0.42
    assert risk.averageExpectedRR == 2.25
    assert risk.averageRealizedRR == 0.85
    assert risk.rrDelta == -1.4
    assert risk.maxDrawdown == 1.0
    assert risk.bestStreak == 1
    assert risk.worstStreak == 1


def test_playbook_recommendation_and_confluence_stats(analytics_services):
    _, _, analytics_service = analytics_services

    playbook = {item.setupName: item for item in analytics_service.getPlaybookStats()}
    assert playbook["Bullish Continuation"].totalTrades == 2
    assert playbook["Bullish Continuation"].winRate == 100.0
    assert playbook["Bullish Continuation"].averageRR == 2.2
    assert playbook["Bullish Continuation"].expectancy == 2.2
    assert playbook["Bearish Reversal"].totalTrades == 1
    assert playbook["Bearish Reversal"].expectancy == -1.0

    recommendations = {item.recommendation: item for item in analytics_service.getRecommendationStats()}
    assert recommendations["FOLLOWED_OSCAR"].trades == 2
    assert recommendations["FOLLOWED_OSCAR"].winRate == 50.0
    assert recommendations["FOLLOWED_OSCAR"].averageRR == 0.75
    assert recommendations["FOLLOWED_OSCAR"].profitFactor == 2.5
    assert recommendations["IGNORED_OSCAR"].trades == 1
    assert recommendations["WAITED"].averageRR == 0.0
    assert recommendations["CANCELLED"].profitFactor == 0.0

    confluences = analytics_service.getConfluenceStats()
    assert confluences.winningTrades[0].name == "Bias aligned"
    assert confluences.winningTrades[0].frequency == 2
    assert {item.name for item in confluences.winningTrades} == {"Bias aligned", "London sweep", "Daily discount"}


def test_analytics_api_endpoints(analytics_services):
    journal_service, playbook_service, _ = analytics_services
    app.dependency_overrides[get_journal_service] = lambda: journal_service
    app.dependency_overrides[get_playbook_service] = lambda: playbook_service

    try:
        client = TestClient(app)

        summary = client.get("/api/v1/analytics/summary")
        assert summary.status_code == 200
        assert summary.json()["totalTrades"] == 5

        sessions = client.get("/api/v1/analytics/sessions")
        assert sessions.status_code == 200
        assert len(sessions.json()) == 3

        timeframes = client.get("/api/v1/analytics/timeframes")
        assert timeframes.status_code == 200
        assert len(timeframes.json()) == 5

        symbols = client.get("/api/v1/analytics/symbols")
        assert symbols.status_code == 200
        assert {item["symbol"] for item in symbols.json()} == {
            "EURUSD.PRO",
            "GBPUSD.PRO",
            "USDJPY.PRO",
            "XAUUSD.PRO",
            "AUDUSD.PRO",
        }

        playbook = client.get("/api/v1/analytics/playbook")
        assert playbook.status_code == 200
        assert {item["setupName"] for item in playbook.json()} == {"Bullish Continuation", "Bearish Reversal"}

        recommendations = client.get("/api/v1/analytics/recommendations")
        assert recommendations.status_code == 200
        assert {item["recommendation"] for item in recommendations.json()} == {
            "FOLLOWED_OSCAR",
            "IGNORED_OSCAR",
            "WAITED",
            "CANCELLED",
        }

        confluences = client.get("/api/v1/analytics/confluences")
        assert confluences.status_code == 200
        assert confluences.json()["winningTrades"][0]["name"] == "Bias aligned"

        risk = client.get("/api/v1/analytics/risk")
        assert risk.status_code == 200
        assert risk.json()["maxDrawdown"] == 1.0

        legacy_summary = client.get("/api/v1/analytics/performance")
        assert legacy_summary.status_code == 200

        legacy_setups = client.get("/api/v1/analytics/setups")
        assert legacy_setups.status_code == 200

        legacy_behaviour = client.get("/api/v1/analytics/behaviour")
        assert legacy_behaviour.status_code == 200
    finally:
        app.dependency_overrides.clear()