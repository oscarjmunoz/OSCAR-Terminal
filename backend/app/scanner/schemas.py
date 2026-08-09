from datetime import datetime

from pydantic import BaseModel

from app.scanner.models import OpportunityStage


class OpportunitySnapshotSchema(BaseModel):
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


class OpportunityListResponse(BaseModel):
    opportunities: list[OpportunitySnapshotSchema]
