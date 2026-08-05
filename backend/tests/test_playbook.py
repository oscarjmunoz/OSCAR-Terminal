import pytest
from fastapi.testclient import TestClient

from app.journal.models import JournalOutcomeUpdate
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision
from app.journal.router import get_journal_service
from app.journal.service import JournalService
from app.main import app
from app.playbook.models import PlaybookEvaluationRequest
from app.playbook.models import PlaybookInstitutionalZonesCondition
from app.playbook.models import PlaybookLiquidityCondition
from app.playbook.models import PlaybookSetupConditions
from app.playbook.models import PlaybookSetupCreate
from app.playbook.models import PlaybookSetupUpdate
from app.playbook.models import PlaybookStructureCondition
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
    symbol: str = "EURUSD.pro",
    side: TradeSide = TradeSide.BUY,
    score: int = 80,
    confidence: float = 0.85,
    recommendation: RecommendationType | None = None,
    order_block: bool = True,
    fvg: bool = True,
    confluence_name: str = "Bias aligned",
) -> DecisionReport:
    context = DecisionContext(
        symbol=symbol,
        side=side,
        volume=0.10,
        sl=1.0810,
        tp=1.0910,
        price=1.0860,
    )
    bias = MarketBiasReport(bias=MarketBias.BULLISH if side == TradeSide.BUY else MarketBias.BEARISH, explanation="Bias aligned")
    score_report = InstitutionalScoreReport(score=score, confidence=confidence, quality_level=QualityLevel.A)
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
        order_block=ZoneStatus(active=order_block, explanation="Order block active"),
        breaker=ZoneStatus(active=False, explanation="Breaker inactive"),
        mitigation=ZoneStatus(active=True, explanation="Mitigation active"),
        fvg=ZoneStatus(active=fvg, explanation="FVG active"),
        premium=ZoneStatus(active=side == TradeSide.SELL, explanation="Premium zone"),
        discount=ZoneStatus(active=side == TradeSide.BUY, explanation="Discount zone"),
    )
    confluences = [
        ConfluenceItem(name=confluence_name, detected=True, importance=ImportanceLevel.HIGH, explanation="Confluence present"),
        ConfluenceItem(name="BOS confirmed", detected=True, importance=ImportanceLevel.HIGH, explanation="Structure confluence"),
    ]
    checklist = [
        ChecklistItem(label="Liquidity taken", checked=True, explanation="Liquidity sweep detected"),
        ChecklistItem(label="Risk valid", checked=True, explanation="RR acceptable"),
    ]
    recommendation = recommendation or (RecommendationType.BUY if side == TradeSide.BUY else RecommendationType.SELL)
    risk = RiskAssessmentReport(rr_expected=2.25, risk="LOW", risk_percent=0.42, volatility=8.0, setup_quality=QualityLevel.A)

    return DecisionReport(
        context=context,
        market_bias=bias,
        institutional_score=score_report,
        liquidity=liquidity,
        market_structure=structure,
        institutional_zones=zones,
        confluences=confluences,
        risk_assessment=risk,
        execution_checklist=checklist,
        final_recommendation=FinalRecommendation(recommendation=recommendation, explanation="High confluence setup"),
        narrative="Sesgo, liquidez y estructura convergen en una decisión clara.",
    )


def build_payload(*, symbol: str = "EURUSD.pro", side: TradeSide = TradeSide.BUY, notes: str = "Journal note"):
    report = build_report(symbol=symbol, side=side)
    from app.journal.models import JournalEntryCreate

    return JournalEntryCreate(
        symbol=symbol,
        timeframe="M5",
        session="LONDON",
        entryPrice=1.0860,
        stopLoss=1.0810,
        takeProfit=1.0910,
        positionSize=0.10,
        riskPercent=0.42,
        expectedRR=2.25,
        traderDecision=TraderDecision.FOLLOWED_OSCAR,
        decisionReport=report,
        personalNotes=notes,
        tags=["swing", "london"],
    )


@pytest.fixture()
def journal_service():
    return JournalService()


@pytest.fixture()
def playbook_service(journal_service):
    return PlaybookService(journal_service=journal_service)


def setup_payload() -> PlaybookSetupCreate:
    return PlaybookSetupCreate(
        name="London Long Continuation",
        description="Bullish continuation after liquidity sweep",
        category="INTRADAY",
        enabled=True,
        conditions=PlaybookSetupConditions(
            bias=MarketBias.BULLISH,
            minimumInstitutionalScore=75,
            minimumConfidence=0.80,
            liquidity=PlaybookLiquidityCondition(minLiquidityTaken=200),
            structure=PlaybookStructureCondition(bos=True, mss=True),
            institutionalZones=PlaybookInstitutionalZonesCondition(orderBlock=True, fvg=True, discount=True),
            requiredConfluences=["Bias aligned", "BOS confirmed"],
            allowedRecommendations=[RecommendationType.BUY],
        ),
    )


def test_playbook_crud(playbook_service):
    created = playbook_service.createSetup(setup_payload())
    assert created.id
    assert created.enabled is True

    fetched = playbook_service.getSetup(created.id)
    assert fetched.id == created.id

    updated = playbook_service.updateSetup(created.id, PlaybookSetupUpdate(description="Updated description", enabled=False))
    assert updated.description == "Updated description"
    assert updated.enabled is False
    assert updated.updatedAt >= created.updatedAt

    deleted = playbook_service.deleteSetup(created.id)
    assert deleted.id == created.id

    with pytest.raises(KeyError):
        playbook_service.getSetup(created.id)


def test_match_engine_and_percentage(playbook_service):
    setup = playbook_service.createSetup(setup_payload())
    report = build_report()

    match = playbook_service.evaluateSetup(setup.id, report)

    assert match.matched is True
    assert match.matchPercentage == 100
    assert "Bias == BULLISH" in match.matchedConditions
    assert match.missingConditions == []


def test_match_percentage_with_missing_conditions(playbook_service):
    setup = playbook_service.createSetup(
        PlaybookSetupCreate(
            name="Strict Buy Setup",
            description="Requires strong filters",
            category="SWING",
            conditions=PlaybookSetupConditions(
                bias=MarketBias.BULLISH,
                minimumInstitutionalScore=90,
                minimumConfidence=0.90,
                allowedRecommendations=[RecommendationType.BUY],
            ),
        )
    )
    report = build_report(score=82, confidence=0.82)

    match = playbook_service.evaluateSetup(setup.id, report)

    assert match.matched is False
    assert 0 < match.matchPercentage < 100
    assert any("Institutional score" in item for item in match.missingConditions)
    assert any("Confidence" in item for item in match.missingConditions)


def test_historical_statistics_from_journal(playbook_service, journal_service):
    playbook_service.createSetup(setup_payload())

    first = journal_service.createEntry(build_payload(symbol="EURUSD.pro", side=TradeSide.BUY))
    second = journal_service.createEntry(build_payload(symbol="GBPUSD.pro", side=TradeSide.BUY))
    third = journal_service.createEntry(build_payload(symbol="AUDUSD.pro", side=TradeSide.BUY))
    fourth = journal_service.createEntry(build_payload(symbol="NZDUSD.pro", side=TradeSide.BUY))

    journal_service.updateOutcome(first.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.WIN, realizedRR=2.4, durationMinutes=180))
    journal_service.updateOutcome(second.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.LOSS, realizedRR=-1.0, durationMinutes=210))
    journal_service.updateOutcome(third.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.BREAK_EVEN, realizedRR=0.0, durationMinutes=90))
    journal_service.updateOutcome(fourth.id, JournalOutcomeUpdate(tradeOutcome=TradeOutcome.CANCELLED, durationMinutes=30))

    stats = playbook_service.getStatistics()
    assert len(stats) == 1
    assert stats[0].totalTrades == 4
    assert stats[0].wins == 1
    assert stats[0].losses == 1
    assert stats[0].breakEven == 1
    assert stats[0].cancelled == 1
    assert stats[0].winRate == 25.0
    assert stats[0].averageRR == 0.47
    assert stats[0].averageDuration == 127.5


def test_journal_integration_uses_snapshot_matching(playbook_service, journal_service):
    setup = playbook_service.createSetup(setup_payload())
    journal_service.createEntry(build_payload(symbol="EURUSD.pro", side=TradeSide.BUY))
    journal_service.createEntry(build_payload(symbol="USDCHF.pro", side=TradeSide.BUY))

    stats = playbook_service.getStatistics()
    assert stats[0].totalTrades == 2

    report = build_report()
    matches = playbook_service.evaluateAll(report)
    assert len(matches) == 1
    assert matches[0].setupId == setup.id


def test_decision_report_integration_via_api():
    journal_service = JournalService()
    playbook_service = PlaybookService(journal_service=journal_service)
    app.dependency_overrides[get_journal_service] = lambda: journal_service
    app.dependency_overrides[get_playbook_service] = lambda: playbook_service

    try:
        client = TestClient(app)
        create_response = client.post("/api/v1/playbook", json=setup_payload().model_dump(mode="json"))
        assert create_response.status_code == 200
        setup_id = create_response.json()["id"]

        evaluate_response = client.post(
            "/api/v1/playbook/evaluate",
            json=PlaybookEvaluationRequest(decisionReport=build_report()).model_dump(mode="json"),
        )
        assert evaluate_response.status_code == 200
        assert evaluate_response.json()[0]["setupId"] == setup_id

        stats_response = client.get("/api/v1/playbook/statistics")
        assert stats_response.status_code == 200
        assert stats_response.json()[0]["setupId"] == setup_id
    finally:
        app.dependency_overrides.clear()
