from __future__ import annotations

from datetime import datetime
from datetime import timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.journal.models import TradeOutcome
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import MarketBias
from app.schemas.decision_center import RecommendationType


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PlaybookLiquidityCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minBuyLiquidity: int | None = None
    minSellLiquidity: int | None = None
    minLiquidityTaken: int | None = None
    minPendingLiquidity: int | None = None


class PlaybookStructureCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trend: str | None = None
    bos: bool | None = None
    choch: bool | None = None
    mss: bool | None = None


class PlaybookInstitutionalZonesCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orderBlock: bool | None = None
    breaker: bool | None = None
    mitigation: bool | None = None
    fvg: bool | None = None
    premium: bool | None = None
    discount: bool | None = None


class PlaybookSetupConditions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bias: MarketBias | None = None
    minimumInstitutionalScore: int | None = None
    minimumConfidence: float | None = None
    liquidity: PlaybookLiquidityCondition = Field(default_factory=PlaybookLiquidityCondition)
    structure: PlaybookStructureCondition = Field(default_factory=PlaybookStructureCondition)
    institutionalZones: PlaybookInstitutionalZonesCondition = Field(default_factory=PlaybookInstitutionalZonesCondition)
    requiredConfluences: list[str] = Field(default_factory=list)
    allowedRecommendations: list[RecommendationType] = Field(default_factory=list)


class PlaybookSetupConditionsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bias: MarketBias | None = None
    minimumInstitutionalScore: int | None = None
    minimumConfidence: float | None = None
    liquidity: PlaybookLiquidityCondition | None = None
    structure: PlaybookStructureCondition | None = None
    institutionalZones: PlaybookInstitutionalZonesCondition | None = None
    requiredConfluences: list[str] | None = None
    allowedRecommendations: list[RecommendationType] | None = None


class PlaybookSetup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    category: str
    enabled: bool = True
    conditions: PlaybookSetupConditions = Field(default_factory=PlaybookSetupConditions)
    createdAt: datetime = Field(default_factory=_utc_now)
    updatedAt: datetime = Field(default_factory=_utc_now)


class PlaybookSetupCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    category: str
    enabled: bool = True
    conditions: PlaybookSetupConditions = Field(default_factory=PlaybookSetupConditions)


class PlaybookSetupUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    category: str | None = None
    enabled: bool | None = None
    conditions: PlaybookSetupConditionsUpdate | None = None


class PlaybookEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisionReport: DecisionReport
    setupId: str | None = None


class PlaybookMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    setupId: str
    setupName: str
    matched: bool
    matchPercentage: int
    matchedConditions: list[str]
    missingConditions: list[str]
    explanation: str


class PlaybookSetupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    setupId: str
    setupName: str
    totalTrades: int
    wins: int
    losses: int
    breakEven: int
    cancelled: int
    winRate: float
    averageRR: float
    averageDuration: float
