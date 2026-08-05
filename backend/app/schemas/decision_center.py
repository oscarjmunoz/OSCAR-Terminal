from enum import Enum

from pydantic import BaseModel

from app.schemas.decision import DecisionContext


class MarketBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class QualityLevel(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    NO_TRADE = "NO TRADE"


class RecommendationType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"
    NO_TRADE = "NO TRADE"


class ImportanceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MarketBiasReport(BaseModel):
    bias: MarketBias
    explanation: str


class InstitutionalScoreReport(BaseModel):
    score: int
    confidence: float
    quality_level: QualityLevel


class LiquidityReport(BaseModel):
    buy_liquidity: int
    sell_liquidity: int
    liquidity_taken: int
    pending_liquidity: int
    explanation: str


class MarketStructureReport(BaseModel):
    trend: str
    bos: bool
    choch: bool
    mss: bool
    explanation: str


class ZoneStatus(BaseModel):
    active: bool
    explanation: str


class InstitutionalZonesReport(BaseModel):
    order_block: ZoneStatus
    breaker: ZoneStatus
    mitigation: ZoneStatus
    fvg: ZoneStatus
    premium: ZoneStatus
    discount: ZoneStatus


class ConfluenceItem(BaseModel):
    name: str
    detected: bool
    importance: ImportanceLevel
    explanation: str


class RiskAssessmentReport(BaseModel):
    rr_expected: float
    risk: str
    risk_percent: float
    volatility: float
    setup_quality: QualityLevel


class ChecklistItem(BaseModel):
    label: str
    checked: bool
    explanation: str


class FinalRecommendation(BaseModel):
    recommendation: RecommendationType
    explanation: str


class DecisionReport(BaseModel):
    context: DecisionContext
    market_bias: MarketBiasReport
    institutional_score: InstitutionalScoreReport
    liquidity: LiquidityReport
    market_structure: MarketStructureReport
    institutional_zones: InstitutionalZonesReport
    confluences: list[ConfluenceItem]
    risk_assessment: RiskAssessmentReport
    execution_checklist: list[ChecklistItem]
    final_recommendation: FinalRecommendation
    narrative: str
