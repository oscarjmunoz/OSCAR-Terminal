from datetime import datetime

from pydantic import BaseModel

from app.opportunity.models import EstimatedEta
from app.opportunity.models import OpportunityPriority
from app.opportunity.models import OpportunityStage
from app.opportunity.models import RecommendedAction


class OpportunityResultSchema(BaseModel):
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


class MarketSummarySchema(BaseModel):
    total_assets: int
    ignored: int
    watching: int
    preparing: int
    ready: int
    active: int
    last_scan: datetime | None


class OpportunityQueueResponse(BaseModel):
    market_summary: MarketSummarySchema
    opportunity_queue: list[OpportunityResultSchema]
