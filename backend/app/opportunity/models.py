from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OpportunityStage(str, Enum):
    CONTEXT_BUILDING = "CONTEXT_BUILDING"
    WAITING_LIQUIDITY = "WAITING_LIQUIDITY"
    WAITING_SWEEP = "WAITING_SWEEP"
    WAITING_MSS = "WAITING_MSS"
    WAITING_DISPLACEMENT = "WAITING_DISPLACEMENT"
    WAITING_ENTRY_ZONE = "WAITING_ENTRY_ZONE"
    EXECUTION_WINDOW = "EXECUTION_WINDOW"
    TRADE_ACTIVE = "TRADE_ACTIVE"


class RecommendedAction(str, Enum):
    IGNORE = "IGNORE"
    MONITOR = "MONITOR"
    WATCH = "WATCH"
    PREPARE = "PREPARE"
    READY = "READY"
    ACTIVE = "ACTIVE"


class EstimatedEta(str, Enum):
    NOW = "NOW"
    LESS_THAN_15_MIN = "<15_MIN"
    MIN_15_30 = "15_30_MIN"
    MIN_30_60 = "30_60_MIN"
    GREATER_THAN_60 = ">60_MIN"
    UNKNOWN = "UNKNOWN"


class OpportunityPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    IGNORE = "IGNORE"


@dataclass(slots=True)
class OpportunityResult:
    symbol: str
    timeframe: str
    bias: str
    structure: str
    liquidity_target: str
    current_stage: OpportunityStage
    opportunity_score: float
    institutional_score: float
    execution_quality: float
    priority: OpportunityPriority
    estimated_eta: EstimatedEta
    decision_summary: str
    recommended_action: RecommendedAction
    last_update: datetime


@dataclass(slots=True)
class MarketSummary:
    total_assets: int
    ignored: int
    watching: int
    preparing: int
    ready: int
    active: int
    last_scan: datetime | None
