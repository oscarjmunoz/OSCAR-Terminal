from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OpportunityStage(str, Enum):
    BUILDING_CONTEXT = "BUILDING_CONTEXT"
    WAITING_LIQUIDITY = "WAITING_LIQUIDITY"
    WAITING_SWEEP = "WAITING_SWEEP"
    WAITING_MSS = "WAITING_MSS"
    WAITING_DISPLACEMENT = "WAITING_DISPLACEMENT"
    ENTRY_READY = "ENTRY_READY"
    TRADE_ACTIVE = "TRADE_ACTIVE"


@dataclass(slots=True)
class OpportunitySnapshot:
    symbol: str
    timeframe: str
    bias: str
    structure: str
    liquidity_target: str
    stage: OpportunityStage
    institutional_score: float
    execution_quality: float
    last_update: datetime
    health: str
    decision_summary: str
