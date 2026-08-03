from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from typing import TypedDict

from app.engines.context.ContextEngine import ContextEngineInputFairValueGap
from app.engines.context.ContextEngine import ContextEngineInputLiquidity
from app.engines.context.ContextEngine import ContextEngineInputOrderBlock
from app.engines.context.ContextResult import ContextResult
from app.engines.decision.InstitutionalDecisionResult import DecisionDirection
from app.engines.liquidity.LiquidityMap import LiquidityMap
from app.engines.liquidity.LiquidityMapEngine import LiquidityMapInput
from app.engines.mss.MSSResult import MSSResult
from app.engines.mss.MSSEngine import MSSInput
from app.engines.premium_discount.PremiumDiscountEngine import PremiumDiscountInput
from app.engines.premium_discount.PremiumDiscountResult import PremiumDiscountResult
from app.engines.structure.MarketStructureEngine import MarketStructureInput
from app.engines.structure.MarketStructureResult import MarketStructureResult


ExecutionAction = Literal["BUY", "SELL", "WAIT", "NO_TRADE"]
Bias = Literal["BULLISH", "BEARISH", "NEUTRAL"]
SessionName = Literal["ASIA", "LONDON", "NEW_YORK", "OVERLAP", "OFF_HOURS"]


class MarketInput(TypedDict):
    symbol: str
    timeframe: str
    bias: Bias
    session: SessionName
    currentPrice: float


class InstitutionalContextInput(TypedDict):
    liquidity: ContextEngineInputLiquidity
    orderBlock: ContextEngineInputOrderBlock
    fairValueGap: ContextEngineInputFairValueGap


class RiskInput(TypedDict):
    riskPercent: float
    rr: float
    exposurePercent: float
    stopAligned: bool
    session: str


class InstitutionalPipelineInput(TypedDict):
    market: MarketInput
    liquidity: LiquidityMapInput
    structure: MarketStructureInput
    context: InstitutionalContextInput
    premiumDiscount: PremiumDiscountInput
    mss: MSSInput
    risk: RiskInput


@dataclass(frozen=True, slots=True)
class LiquidityResult:
    valid: bool
    sweepSide: Literal["BSL", "SSL", "NONE"]
    data: LiquidityMap
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StructureResult:
    valid: bool
    direction: DecisionDirection
    trend: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"]
    marketStructure: MarketStructureResult
    mss: MSSResult
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RiskResult:
    valid: bool
    riskScore: int
    riskPercent: float
    rr: float
    exposurePercent: float
    sessionAllowed: bool
    passedRules: tuple[str, ...]
    failedRules: tuple[str, ...]
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExecutionRecommendation:
    action: ExecutionAction
    explanation: str


@dataclass(frozen=True, slots=True)
class DecisionResult:
    valid: bool
    direction: DecisionDirection
    institutionalScore: int
    confidence: int
    state: Literal["VALID_LONG", "VALID_SHORT", "INVALID"]
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionContext:
    market: str
    timeframe: str
    bias: Bias
    liquidity: LiquidityResult
    structure: StructureResult
    risk: RiskResult
    institutionalScore: int
    confidence: int
    narrative: str
    warnings: tuple[str, ...]
    executionRecommendation: ExecutionRecommendation


class PipelineArtifacts(TypedDict):
    context: ContextResult
    premiumDiscount: PremiumDiscountResult
