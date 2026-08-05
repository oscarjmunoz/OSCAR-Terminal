from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict


class OperationalStatus(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class OperationalReadinessItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    label: str
    status: OperationalStatus
    detail: str
    observedAt: datetime | None = None


class OperationalReadinessSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    timeframe: str
    generatedAt: datetime
    overallStatus: OperationalStatus
    items: list[OperationalReadinessItem]


class OperationalSettingsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    defaultSymbol: str
    defaultTimeframe: str
    availableSymbols: list[str]
    availableTimeframes: list[str]
