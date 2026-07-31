from __future__ import annotations

from typing import Literal
from typing import TypedDict


class TradePlanInstrument(TypedDict):
    symbol: str
    market: str
    timeframe: str
    session: str


class TradePlanContext(TypedDict):
    bias: str
    trend: str
    phase: str
    narrative: str


class TradePlanConfirmation(TypedDict):
    trigger: str
    timeframe: str
    timestamp: str
    confluence: list[str]


class TradePlanEntry(TypedDict):
    orderType: Literal["MARKET", "LIMIT", "STOP"]
    price: float
    window: str


class TradePlanTargets(TypedDict):
    tp1: float
    tp2: float
    runner: str


class TradePlanRisk(TypedDict):
    stopLoss: float
    rr: str
    riskPercent: float


class TradePlanManagement(TypedDict):
    breakEven: str
    partialExit: str
    trailingRule: str


class TradePlanQuality(TypedDict):
    score: int
    grade: str


class TradePlanStatus(TypedDict):
    state: Literal["DRAFT", "READY", "ACTIVE", "INVALIDATED", "CLOSED"]
    updatedAt: str


class TradePlanChecklist(TypedDict):
    liquidityMapped: bool
    structureConfirmed: bool
    imbalanceAligned: bool
    riskValidated: bool
    sessionValidated: bool


class TradePlanInvalidation(TypedDict):
    price: float
    condition: str
    reason: str


class TradePlan(TypedDict):
    instrument: TradePlanInstrument
    context: TradePlanContext
    confirmation: TradePlanConfirmation
    entry: TradePlanEntry
    targets: TradePlanTargets
    risk: TradePlanRisk
    management: TradePlanManagement
    quality: TradePlanQuality
    status: TradePlanStatus
    checklist: TradePlanChecklist
    reasons: list[str]
    warnings: list[str]
    invalidation: TradePlanInvalidation
