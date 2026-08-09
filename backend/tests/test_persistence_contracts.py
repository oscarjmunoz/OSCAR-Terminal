from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.journal.models import JournalDecisionSnapshot, JournalEntry, JournalEntryCreate, TraderDecision
from app.journal.repository import SqlAlchemyJournalRepository
from app.scanner.models import OpportunitySnapshot, OpportunityStage
from app.scanner.repository import SqlAlchemyScannerRepository
from app.schemas.decision import DecisionContext, TradeSide
from app.schemas.decision_center import (
    ChecklistItem,
    ConfluenceItem,
    DecisionReport,
    FinalRecommendation,
    ImportanceLevel,
    InstitutionalScoreReport,
    InstitutionalZonesReport,
    LiquidityReport,
    MarketBias,
    MarketBiasReport,
    MarketStructureReport,
    QualityLevel,
    RecommendationType,
    RiskAssessmentReport,
    ZoneStatus,
)


def _build_decision_report() -> DecisionReport:
    context = DecisionContext(symbol="EURUSD", side=TradeSide.BUY, volume=0.01, sl=1.0800, tp=1.0900, price=1.0850)
    return DecisionReport(
        context=context,
        market_bias=MarketBiasReport(bias=MarketBias.BULLISH, explanation="Bias is bullish"),
        institutional_score=InstitutionalScoreReport(score=82, confidence=0.84, quality_level=QualityLevel.A),
        liquidity=LiquidityReport(buy_liquidity=1200, sell_liquidity=800, liquidity_taken=200, pending_liquidity=150, explanation="Liquidity favors continuation"),
        market_structure=MarketStructureReport(trend="BULLISH", bos=True, choch=False, mss=True, explanation="Structure supports the move"),
        institutional_zones=InstitutionalZonesReport(
            order_block=ZoneStatus(active=True, explanation="Order block active"),
            breaker=ZoneStatus(active=False, explanation="Breaker inactive"),
            mitigation=ZoneStatus(active=True, explanation="Mitigation active"),
            fvg=ZoneStatus(active=True, explanation="FVG active"),
            premium=ZoneStatus(active=False, explanation="Premium zone"),
            discount=ZoneStatus(active=True, explanation="Discount zone"),
        ),
        confluences=[ConfluenceItem(name="Bias", detected=True, importance=ImportanceLevel.HIGH, explanation="Bias aligns")],
        risk_assessment=RiskAssessmentReport(rr_expected=2.5, risk="LOW", risk_percent=0.4, volatility=5.5, setup_quality=QualityLevel.A),
        execution_checklist=[ChecklistItem(label="Risk", checked=True, explanation="Risk in range")],
        final_recommendation=FinalRecommendation(recommendation=RecommendationType.BUY, explanation="High conviction"),
        narrative="Bullish continuation setup",
    )


def _build_payload() -> JournalEntryCreate:
    return JournalEntryCreate(
        symbol="EURUSD",
        timeframe="M5",
        session="LONDON",
        entryPrice=1.0850,
        stopLoss=1.0800,
        takeProfit=1.0900,
        positionSize=0.01,
        riskPercent=0.4,
        expectedRR=2.5,
        traderDecision=TraderDecision.FOLLOWED_OSCAR,
        decisionReport=_build_decision_report(),
        personalNotes="Persisted entry",
        tags=["persistence", "test"],
    )


def test_sqlalchemy_scanner_repository_round_trips_snapshots():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    repository = SqlAlchemyScannerRepository(session_factory=session_factory)

    snapshot = OpportunitySnapshot(
        symbol="EURUSD",
        timeframe="M5",
        bias="BULLISH",
        structure="BULLISH|BOS=1|CHOCH=1|MSS=1",
        liquidity_target="BUY_SIDE_LIQUIDITY",
        stage=OpportunityStage.ENTRY_READY,
        institutional_score=84.0,
        execution_quality=78.0,
        last_update=None,
        health="GREEN",
        decision_summary="Ready to enter",
    )

    stored = repository.upsert(snapshot)
    fetched = repository.get("EURUSD", "M5")
    listed = repository.list()

    assert stored.symbol == "EURUSD"
    assert fetched is not None
    assert fetched.stage == OpportunityStage.ENTRY_READY
    assert listed[0].decision_summary == "Ready to enter"


def test_sqlalchemy_journal_repository_round_trips_entries():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    repository = SqlAlchemyJournalRepository(session_factory=session_factory)

    payload = _build_payload()
    entry = repository.add(
        JournalEntry(
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            session=payload.session,
            entryPrice=payload.entryPrice,
            stopLoss=payload.stopLoss,
            takeProfit=payload.takeProfit,
            positionSize=payload.positionSize,
            riskPercent=payload.riskPercent,
            expectedRR=payload.expectedRR,
            decisionSnapshot=JournalDecisionSnapshot.from_report(payload.decisionReport),
            traderDecision=payload.traderDecision,
            personalNotes=payload.personalNotes,
            tags=list(payload.tags),
        )
    )
    fetched = repository.get(entry.id)
    listed = repository.list()

    assert fetched is not None
    assert fetched.symbol == "EURUSD"
    assert fetched.decisionSnapshot.narrative == "Bullish continuation setup"
    assert listed[0].tags == ["persistence", "test"]
