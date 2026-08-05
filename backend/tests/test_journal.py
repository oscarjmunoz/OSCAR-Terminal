import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.journal.models import JournalEntryCreate
from app.journal.models import JournalFilterCriteria
from app.journal.models import JournalOutcomeUpdate
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision
from app.journal.router import get_journal_service
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

def build_report(symbol: str = "EURUSD.pro", side: TradeSide = TradeSide.BUY) -> DecisionReport:
    context = DecisionContext(
        symbol=symbol,
        side=side,
        volume=0.10,
        sl=1.0810,
        tp=1.0910,
        price=1.0860,
    )

    bias = MarketBiasReport(bias=MarketBias.BULLISH if side == TradeSide.BUY else MarketBias.BEARISH, explanation="Bias aligned")
    score = InstitutionalScoreReport(score=78, confidence=0.82, quality_level=QualityLevel.A)
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
    confluences = [
        ConfluenceItem(
            name="Bias aligned with side",
            detected=True,
            importance=ImportanceLevel.HIGH,
            explanation="Bias aligned with execution side",
        ),
        ConfluenceItem(
            name="BOS confirmed",
            detected=True,
            importance=ImportanceLevel.HIGH,
            explanation="Break of structure confirmed",
        ),
    ]
    checklist = [
        ChecklistItem(label="Liquidity taken", checked=True, explanation="Liquidity sweep detected"),
        ChecklistItem(label="Risk valid", checked=True, explanation="RR acceptable"),
    ]
    recommendation = FinalRecommendation(recommendation=RecommendationType.BUY if side == TradeSide.BUY else RecommendationType.SELL, explanation="High confluence setup")
    risk = RiskAssessmentReport(rr_expected=2.25, risk="LOW", risk_percent=0.42, volatility=8.0, setup_quality=QualityLevel.A)

    return DecisionReport(
        context=context,
        market_bias=bias,
        institutional_score=score,
        liquidity=liquidity,
        market_structure=structure,
        institutional_zones=zones,
        confluences=confluences,
        risk_assessment=risk,
        execution_checklist=checklist,
        final_recommendation=recommendation,
        narrative="Sesgo, liquidez y estructura convergen en una decisión clara.",
    )


def build_payload(
    *,
    symbol: str = "EURUSD.pro",
    timeframe: str = "M5",
    session: str = "LONDON",
    trader_decision: TraderDecision = TraderDecision.FOLLOWED_OSCAR,
    notes: str = "Journal note",
    tags: list[str] | None = None,
    side: TradeSide = TradeSide.BUY,
) -> JournalEntryCreate:
    report = build_report(symbol=symbol, side=side)
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
        decisionReport=report,
        personalNotes=notes,
        tags=tags or ["swing", "london"],
    )


@pytest.fixture()
def journal_service():
    return JournalService()


def test_journal_entry_snapshot_preserves_decision_report(journal_service):
    payload = build_payload()

    entry = journal_service.createEntry(payload)

    assert entry.id
    assert entry.createdAt.tzinfo is not None
    assert entry.symbol == payload.symbol
    assert entry.tradeOutcome == TradeOutcome.PENDING
    assert entry.decisionSnapshot.bias.bias == payload.decisionReport.market_bias.bias
    assert entry.decisionSnapshot.score == payload.decisionReport.institutional_score.score
    assert entry.decisionSnapshot.confidence == payload.decisionReport.institutional_score.confidence
    assert entry.decisionSnapshot.liquidity.model_dump() == payload.decisionReport.liquidity.model_dump()
    assert entry.decisionSnapshot.structure.model_dump() == payload.decisionReport.market_structure.model_dump()
    assert entry.decisionSnapshot.zones.model_dump() == payload.decisionReport.institutional_zones.model_dump()
    assert entry.decisionSnapshot.recommendation.model_dump() == payload.decisionReport.final_recommendation.model_dump()
    assert entry.decisionSnapshot.narrative == payload.decisionReport.narrative


@pytest.mark.parametrize(
    "trader_decision",
    [
        TraderDecision.FOLLOWED_OSCAR,
        TraderDecision.IGNORED_OSCAR,
        TraderDecision.WAITED,
        TraderDecision.CANCELLED,
    ],
)
def test_journal_accepts_all_trader_decisions(journal_service, trader_decision):
    payload = build_payload(trader_decision=trader_decision)

    entry = journal_service.createEntry(payload)

    assert entry.traderDecision == trader_decision


@pytest.mark.parametrize(
    "outcome,profit_loss,realized_rr,close_reason",
    [
        (TradeOutcome.WIN, 45.0, 2.4, "Target hit"),
        (TradeOutcome.LOSS, -30.0, -1.0, "Stop loss hit"),
        (TradeOutcome.BREAK_EVEN, 0.0, 0.0, "Managed exit"),
        (TradeOutcome.CANCELLED, 0.0, None, "Cancelled before execution"),
    ],
)
def test_update_outcome_supports_all_outcomes(journal_service, outcome, profit_loss, realized_rr, close_reason):
    entry = journal_service.createEntry(build_payload())

    updated = journal_service.updateOutcome(
        entry.id,
        JournalOutcomeUpdate(
            tradeOutcome=outcome,
            profitLoss=profit_loss,
            realizedRR=realized_rr,
            durationMinutes=180,
            closeReason=close_reason,
            personalNotes="Updated after close",
            tags=["updated", "reviewed"],
        ),
    )

    assert updated.tradeOutcome == outcome
    assert updated.profitLoss == profit_loss
    assert updated.realizedRR == realized_rr
    assert updated.durationMinutes == 180
    assert updated.closeReason == close_reason
    assert updated.personalNotes == "Updated after close"
    assert updated.tags == ["updated", "reviewed"]


def test_journal_search_and_filter(journal_service):
    first = journal_service.createEntry(build_payload(symbol="EURUSD.pro", session="LONDON", notes="London continuation", tags=["london", "swing"]))
    second = journal_service.createEntry(build_payload(symbol="GBPUSD.pro", session="NEW_YORK", notes="New York reversal", tags=["ny", "intraday"], side=TradeSide.SELL))

    search_results = journal_service.search("london")
    assert [entry.id for entry in search_results] == [first.id]

    filter_results = journal_service.filter(
        JournalFilterCriteria(
            symbol="GBPUSD.pro",
            timeframe="M5",
            session="NEW_YORK",
            traderDecision=TraderDecision.FOLLOWED_OSCAR,
            tag="ny",
        )
    )
    assert [entry.id for entry in filter_results] == [second.id]


def test_journal_crud(journal_service):
    entry = journal_service.createEntry(build_payload())

    fetched = journal_service.getEntry(entry.id)
    assert fetched.id == entry.id

    deleted = journal_service.deleteEntry(entry.id)
    assert deleted.id == entry.id

    with pytest.raises(KeyError):
        journal_service.getEntry(entry.id)


def test_journal_api_crud_and_query_filters():
    service = JournalService()
    app.dependency_overrides[get_journal_service] = lambda: service

    try:
        client = TestClient(app)
        payload = build_payload(symbol="USDCHF.pro", session="LONDON", notes="API journal entry", tags=["api", "journal"])

        create_response = client.post("/api/v1/journal", json=payload.model_dump(mode="json"))
        assert create_response.status_code == 200
        entry_id = create_response.json()["id"]

        list_response = client.get("/api/v1/journal", params={"q": "api journal"})
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        get_response = client.get(f"/api/v1/journal/{entry_id}")
        assert get_response.status_code == 200
        assert get_response.json()["symbol"] == "USDCHF.pro"

        patch_response = client.patch(
            f"/api/v1/journal/{entry_id}",
            json={
                "tradeOutcome": "WIN",
                "profitLoss": 38.5,
                "realizedRR": 2.1,
                "durationMinutes": 240,
                "closeReason": "Target hit",
                "personalNotes": "Closed from API",
                "tags": ["api", "closed"],
            },
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["tradeOutcome"] == "WIN"

        filtered_response = client.get("/api/v1/journal", params={"tradeOutcome": "WIN", "tag": "closed"})
        assert filtered_response.status_code == 200
        assert len(filtered_response.json()) == 1

        delete_response = client.delete(f"/api/v1/journal/{entry_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["id"] == entry_id
    finally:
        app.dependency_overrides.clear()
