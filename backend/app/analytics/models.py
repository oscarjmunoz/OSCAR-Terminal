from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AnalyticsSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    totalTrades: int
    wins: int
    losses: int
    breakEven: int
    cancelled: int
    winRate: float
    averageRR: float
    averageProfit: float
    averageLoss: float
    expectancy: float
    profitFactor: float


class SessionStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session: str
    trades: int
    winRate: float
    averageRR: float
    averageDuration: float


class TimeframeStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timeframe: str
    trades: int
    winRate: float
    averageRR: float
    averageDuration: float


class SymbolStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    trades: int
    winRate: float
    averageRR: float
    averageDuration: float


class PlaybookStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    setupId: str
    setupName: str
    totalTrades: int
    winRate: float
    averageRR: float
    expectancy: float


class RecommendationStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation: str
    trades: int
    winRate: float
    averageRR: float
    profitFactor: float


class ConfluenceFrequency(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    frequency: int


class ConfluenceStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    winningTrades: list[ConfluenceFrequency] = Field(default_factory=list)


class RiskStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    averageRisk: float
    averageExpectedRR: float
    averageRealizedRR: float
    rrDelta: float
    maxDrawdown: float
    bestStreak: int
    worstStreak: int