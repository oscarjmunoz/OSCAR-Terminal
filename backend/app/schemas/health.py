from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    ERROR = "ERROR"


class HealthSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    overallStatus: HealthStatus
    mt5Connection: HealthStatus
    pipelineStatus: HealthStatus
    marketStatus: HealthStatus
    eventBusStatus: HealthStatus
    lastDecisionContext: datetime | None = None
    lastTickTime: datetime | None = None
    lastCandleTime: datetime | None = None
    pipelineLatency: float | None = None


class HealthStatusChanged(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    previousStatus: HealthStatus
    currentStatus: HealthStatus