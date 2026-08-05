from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import FinalRecommendation
from app.schemas.decision_center import InstitutionalZonesReport
from app.schemas.decision_center import LiquidityReport
from app.schemas.decision_center import MarketBiasReport
from app.schemas.decision_center import MarketStructureReport
from app.schemas.decision_center import ChecklistItem
from app.schemas.decision_center import ConfluenceItem
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import FinalRecommendation


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TraderDecision(str, Enum):
    FOLLOWED_OSCAR = "FOLLOWED_OSCAR"
    IGNORED_OSCAR = "IGNORED_OSCAR"
    WAITED = "WAITED"
    CANCELLED = "CANCELLED"


class TradeOutcome(str, Enum):
    PENDING = "PENDING"
    WIN = "WIN"
    LOSS = "LOSS"
    BREAK_EVEN = "BREAK_EVEN"
    CANCELLED = "CANCELLED"


class JournalDecisionSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bias: MarketBiasReport
    score: int
    confidence: float
    liquidity: LiquidityReport
    structure: MarketStructureReport
    zones: InstitutionalZonesReport
    confluences: list[ConfluenceItem] = Field(default_factory=list)
    checklist: list[ChecklistItem] = Field(default_factory=list)
    recommendation: FinalRecommendation
    narrative: str

    @classmethod
    def from_report(cls, report: DecisionReport) -> JournalDecisionSnapshot:
        return cls(
            bias=report.market_bias,
            score=report.institutional_score.score,
            confidence=report.institutional_score.confidence,
            liquidity=report.liquidity,
            structure=report.market_structure,
            zones=report.institutional_zones,
            confluences=list(report.confluences),
            checklist=list(report.execution_checklist),
            recommendation=report.final_recommendation,
            narrative=report.narrative,
        )


class JournalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()))
    createdAt: datetime = Field(default_factory=_utc_now)
    symbol: str
    timeframe: str
    session: str
    entryPrice: float
    stopLoss: float
    takeProfit: float
    positionSize: float
    riskPercent: float
    expectedRR: float
    decisionSnapshot: JournalDecisionSnapshot
    traderDecision: TraderDecision
    tradeOutcome: TradeOutcome = TradeOutcome.PENDING
    profitLoss: float | None = None
    realizedRR: float | None = None
    durationMinutes: int | None = None
    closeReason: str | None = None
    personalNotes: str = ""
    tags: list[str] = Field(default_factory=list)


class JournalEntryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    timeframe: str
    session: str
    entryPrice: float
    stopLoss: float
    takeProfit: float
    positionSize: float
    riskPercent: float
    expectedRR: float
    traderDecision: TraderDecision
    decisionReport: DecisionReport
    personalNotes: str = ""
    tags: list[str] = Field(default_factory=list)


class JournalOutcomeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    traderDecision: TraderDecision | None = None
    tradeOutcome: TradeOutcome | None = None
    profitLoss: float | None = None
    realizedRR: float | None = None
    durationMinutes: int | None = None
    closeReason: str | None = None
    personalNotes: str | None = None
    tags: list[str] | None = None


class JournalFilterCriteria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str | None = None
    timeframe: str | None = None
    session: str | None = None
    traderDecision: TraderDecision | None = None
    tradeOutcome: TradeOutcome | None = None
    tag: str | None = None
    createdAfter: datetime | None = None
    createdBefore: datetime | None = None
    minExpectedRR: float | None = None
    maxExpectedRR: float | None = None
