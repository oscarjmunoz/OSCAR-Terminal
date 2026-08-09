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


class MultiTimeframeBiasState(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNAVAILABLE = "UNAVAILABLE"


class MultiTimeframeDataAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class MultiTimeframeStructureConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNAVAILABLE = "UNAVAILABLE"


class MultiTimeframeContextConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNAVAILABLE = "UNAVAILABLE"


class MultiTimeframeAlignment(str, Enum):
    ALIGNED_BULLISH = "ALIGNED_BULLISH"
    ALIGNED_BEARISH = "ALIGNED_BEARISH"
    MIXED = "MIXED"
    CONFLICT = "CONFLICT"
    UNAVAILABLE = "UNAVAILABLE"


class MultiTimeframeBiasItem(BaseModel):
    timeframe: str
    bias: MultiTimeframeBiasState
    bos: bool
    choch: bool
    mss: bool
    structure_confidence: MultiTimeframeStructureConfidence
    data_availability: MultiTimeframeDataAvailability
    explanation: str


class MultiTimeframeBiasReport(BaseModel):
    h4: MultiTimeframeBiasItem
    h1: MultiTimeframeBiasItem
    m5: MultiTimeframeBiasItem
    alignment: MultiTimeframeAlignment
    conflict: bool
    confidence: MultiTimeframeContextConfidence
    summary: str


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
    multi_timeframe_bias: MultiTimeframeBiasReport | None = None
