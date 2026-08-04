from __future__ import annotations

from dataclasses import dataclass

from app.market.service import MarketService
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.decision_center import ChecklistItem
from app.schemas.decision_center import ConfluenceItem
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import FinalRecommendation
from app.schemas.decision_center import ImportanceLevel
from app.schemas.decision_center import InstitutionalScoreReport
from app.schemas.decision_center import InstitutionalZonesReport
from app.schemas.decision_center import LiquidityReport
from app.schemas.decision_center import MarketBias
from app.schemas.decision_center import MarketBiasReport
from app.schemas.decision_center import MarketStructureReport
from app.schemas.decision_center import QualityLevel
from app.schemas.decision_center import RecommendationType
from app.schemas.decision_center import RiskAssessmentReport
from app.schemas.decision_center import ZoneStatus
from app.smart_money.service import SmartMoneyService


@dataclass(slots=True)
class _ConfluenceSignal:
    name: str
    detected: bool
    importance: ImportanceLevel
    explanation: str
    weight: int


class DecisionCenter:

    @staticmethod
    def build_report(decision: DecisionContext) -> DecisionReport:
        tick = MarketService.latest_tick(decision.symbol)
        candles = MarketService.candles(decision.symbol, timeframe="M5", count=120) or []
        structure = SmartMoneyService.structure(decision.symbol, timeframe="M5", candles=300, left=3, right=3)

        price = DecisionCenter._resolve_price(decision, tick)
        rr_expected, risk_percent = DecisionCenter._compute_rr_and_risk(decision, price)
        volatility = DecisionCenter._compute_volatility(candles, decision.symbol)
        risk_level = DecisionCenter._risk_level(rr_expected, risk_percent, volatility)

        market_bias = DecisionCenter._market_bias(decision, structure)
        liquidity = DecisionCenter._liquidity(candles)
        zones = DecisionCenter._zones(candles, price, structure)
        market_structure = DecisionCenter._market_structure(structure)

        confluences = DecisionCenter._confluences(
            decision=decision,
            market_bias=market_bias,
            structure=structure,
            zones=zones,
            liquidity=liquidity,
            rr_expected=rr_expected,
            volatility=volatility,
            risk_level=risk_level,
        )

        institutional_score = DecisionCenter._institutional_score(confluences, rr_expected)
        checklist = DecisionCenter._checklist(liquidity, structure, zones, rr_expected, risk_level, confluences)
        recommendation = DecisionCenter._recommendation(
            decision=decision,
            market_bias=market_bias,
            institutional_score=institutional_score,
            rr_expected=rr_expected,
            risk_level=risk_level,
            confluences=confluences,
        )
        narrative = DecisionCenter._narrative(
            decision=decision,
            market_bias=market_bias,
            liquidity=liquidity,
            market_structure=market_structure,
            zones=zones,
            risk_level=risk_level,
            rr_expected=rr_expected,
            institutional_score=institutional_score,
            recommendation=recommendation,
        )

        return DecisionReport(
            context=decision,
            market_bias=market_bias,
            institutional_score=institutional_score,
            liquidity=liquidity,
            market_structure=market_structure,
            institutional_zones=zones,
            confluences=[
                ConfluenceItem(
                    name=item.name,
                    detected=item.detected,
                    importance=item.importance,
                    explanation=item.explanation,
                )
                for item in confluences
            ],
            risk_assessment=RiskAssessmentReport(
                rr_expected=round(rr_expected, 2),
                risk=risk_level,
                risk_percent=round(risk_percent, 2),
                volatility=round(volatility, 2),
                setup_quality=institutional_score.quality_level,
            ),
            execution_checklist=checklist,
            final_recommendation=recommendation,
            narrative=narrative,
        )

    @staticmethod
    def _resolve_price(decision: DecisionContext, tick) -> float | None:
        if decision.price is not None:
            return float(decision.price)

        if tick is None:
            return None

        if decision.side == TradeSide.BUY:
            return float(tick.ask)

        return float(tick.bid)

    @staticmethod
    def _compute_rr_and_risk(decision: DecisionContext, price: float | None) -> tuple[float, float]:
        if price is None or decision.sl is None or decision.tp is None:
            return 0.0, 100.0

        if decision.side == TradeSide.BUY:
            reward = decision.tp - price
            risk = price - decision.sl
        else:
            reward = price - decision.tp
            risk = decision.sl - price

        if reward <= 0 or risk <= 0:
            return 0.0, 100.0

        rr_expected = reward / risk
        risk_percent = (risk / price) * 100.0 if price > 0 else 100.0
        return rr_expected, risk_percent

    @staticmethod
    def _compute_volatility(candles, symbol: str) -> float:
        if not candles:
            return 0.0

        factor = 100.0 if "JPY" in symbol.upper() else 10000.0
        window = candles[-20:] if len(candles) >= 20 else candles
        ranges = [max((bar.high - bar.low) * factor, 0.0) for bar in window]

        if not ranges:
            return 0.0

        return float(sum(ranges) / len(ranges))

    @staticmethod
    def _risk_level(rr_expected: float, risk_percent: float, volatility: float) -> str:
        if rr_expected < 1.0 or risk_percent > 1.2 or volatility > 25:
            return "HIGH"

        if rr_expected < 1.5 or risk_percent > 0.8 or volatility > 15:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _market_bias(decision: DecisionContext, structure) -> MarketBiasReport:
        trend = getattr(structure, "trend", "RANGE") if structure is not None else "RANGE"

        if trend == "BULLISH":
            bias = MarketBias.BULLISH
        elif trend == "BEARISH":
            bias = MarketBias.BEARISH
        else:
            bias = MarketBias.NEUTRAL

        side_label = "BUY" if decision.side == TradeSide.BUY else "SELL"
        explanation = (
            f"Bias {bias.value} derived from market structure trend={trend}. "
            f"DecisionContext side={side_label}."
        )
        return MarketBiasReport(bias=bias, explanation=explanation)

    @staticmethod
    def _liquidity(candles) -> LiquidityReport:
        if not candles:
            return LiquidityReport(
                buy_liquidity=0,
                sell_liquidity=0,
                liquidity_taken=0,
                pending_liquidity=0,
                explanation="No candles available to compute liquidity profile.",
            )

        window = candles[-60:] if len(candles) >= 60 else candles
        buy_liquidity = sum(int(bar.tick_volume) for bar in window if bar.close >= bar.open)
        sell_liquidity = sum(int(bar.tick_volume) for bar in window if bar.close < bar.open)

        liquidity_taken = 0
        if len(window) >= 20:
            last = window[-1]
            prev = window[-20:-1]
            prev_high = max(bar.high for bar in prev)
            prev_low = min(bar.low for bar in prev)
            if last.high > prev_high or last.low < prev_low:
                liquidity_taken = int(last.tick_volume)

        pending_liquidity = abs(buy_liquidity - sell_liquidity)
        explanation = (
            "Buy and sell liquidity are calculated from directional tick volume on the recent candle window. "
            "Liquidity taken is flagged when the last candle sweeps the previous local high or low."
        )

        return LiquidityReport(
            buy_liquidity=buy_liquidity,
            sell_liquidity=sell_liquidity,
            liquidity_taken=liquidity_taken,
            pending_liquidity=pending_liquidity,
            explanation=explanation,
        )

    @staticmethod
    def _zones(candles, price: float | None, structure) -> InstitutionalZonesReport:
        trend = getattr(structure, "trend", "RANGE") if structure is not None else "RANGE"
        choch = bool(getattr(structure, "choch", False)) if structure is not None else False

        order_block_active = False
        mitigation_active = False
        order_block_explanation = "No valid order block detected from available candles."

        if candles and price is not None:
            window = candles[-30:] if len(candles) >= 30 else candles
            selected = None
            if trend == "BULLISH":
                for candle in reversed(window):
                    if candle.close < candle.open:
                        selected = candle
                        break
            elif trend == "BEARISH":
                for candle in reversed(window):
                    if candle.close > candle.open:
                        selected = candle
                        break

            if selected is not None:
                low = min(selected.open, selected.close, selected.low, selected.high)
                high = max(selected.open, selected.close, selected.low, selected.high)
                order_block_active = low <= price <= high
                mitigation_active = order_block_active
                order_block_explanation = (
                    f"Reference candle range [{low:.5f}, {high:.5f}] "
                    f"used as order block. Current price={price:.5f}."
                )

        fvg_active, fvg_explanation = DecisionCenter._detect_fvg(candles, price)

        premium_active = False
        discount_active = False
        premium_explanation = "Premium/discount unavailable due to missing price or candles."
        discount_explanation = premium_explanation

        if candles and price is not None:
            rng = candles[-50:] if len(candles) >= 50 else candles
            highest = max(bar.high for bar in rng)
            lowest = min(bar.low for bar in rng)
            midpoint = (highest + lowest) / 2.0
            premium_active = price > midpoint
            discount_active = price <= midpoint
            premium_explanation = f"Price={price:.5f} above midpoint={midpoint:.5f}."
            discount_explanation = f"Price={price:.5f} at or below midpoint={midpoint:.5f}."

        breaker_active = choch
        breaker_explanation = "Breaker active because CHOCH is detected." if choch else "Breaker inactive because CHOCH is not detected."

        return InstitutionalZonesReport(
            order_block=ZoneStatus(active=order_block_active, explanation=order_block_explanation),
            breaker=ZoneStatus(active=breaker_active, explanation=breaker_explanation),
            mitigation=ZoneStatus(
                active=mitigation_active,
                explanation="Mitigation active when price revisits the selected order block range."
                if mitigation_active
                else "Mitigation inactive because price has not revisited the selected order block.",
            ),
            fvg=ZoneStatus(active=fvg_active, explanation=fvg_explanation),
            premium=ZoneStatus(active=premium_active, explanation=premium_explanation),
            discount=ZoneStatus(active=discount_active, explanation=discount_explanation),
        )

    @staticmethod
    def _detect_fvg(candles, price: float | None) -> tuple[bool, str]:
        if not candles or len(candles) < 3 or price is None:
            return False, "FVG unavailable due to missing candle window or price."

        for i in range(len(candles) - 3, -1, -1):
            c1 = candles[i]
            c3 = candles[i + 2]

            if c1.high < c3.low:
                low = c1.high
                high = c3.low
                active = low <= price <= high
                return active, f"Bullish FVG zone [{low:.5f}, {high:.5f}] with price={price:.5f}."

            if c1.low > c3.high:
                low = c3.high
                high = c1.low
                active = low <= price <= high
                return active, f"Bearish FVG zone [{low:.5f}, {high:.5f}] with price={price:.5f}."

        return False, "No FVG pattern detected in the recent candle sequence."

    @staticmethod
    def _market_structure(structure) -> MarketStructureReport:
        if structure is None:
            return MarketStructureReport(
                trend="UNKNOWN",
                bos=False,
                choch=False,
                mss=False,
                explanation="No market structure computed from SmartMoneyService.",
            )

        explanation = (
            f"Trend={structure.trend}, BOS={bool(structure.bos)}, "
            f"CHOCH={bool(structure.choch)}, MSS={bool(structure.mss)} "
            "derived from swing classification."
        )

        return MarketStructureReport(
            trend=structure.trend,
            bos=bool(structure.bos),
            choch=bool(structure.choch),
            mss=bool(structure.mss),
            explanation=explanation,
        )

    @staticmethod
    def _confluences(
        decision: DecisionContext,
        market_bias: MarketBiasReport,
        structure,
        zones: InstitutionalZonesReport,
        liquidity: LiquidityReport,
        rr_expected: float,
        volatility: float,
        risk_level: str,
    ) -> list[_ConfluenceSignal]:
        side_is_buy = decision.side == TradeSide.BUY
        side_aligns = (
            (side_is_buy and market_bias.bias == MarketBias.BULLISH)
            or ((not side_is_buy) and market_bias.bias == MarketBias.BEARISH)
        )

        bos = bool(getattr(structure, "bos", False)) if structure is not None else False
        choch = bool(getattr(structure, "choch", False)) if structure is not None else False
        mss = bool(getattr(structure, "mss", False)) if structure is not None else False

        zone_alignment = zones.discount.active if side_is_buy else zones.premium.active
        institutional_zone_active = (
            zones.order_block.active or zones.breaker.active or zones.mitigation.active or zones.fvg.active
        )

        signals = [
            _ConfluenceSignal(
                name="Bias aligned with DecisionContext side",
                detected=side_aligns,
                importance=ImportanceLevel.HIGH,
                explanation="Trade side is aligned with market bias." if side_aligns else "Trade side is not aligned with market bias.",
                weight=20,
            ),
            _ConfluenceSignal(
                name="BOS confirmed",
                detected=bos,
                importance=ImportanceLevel.HIGH,
                explanation="Break of structure is confirmed." if bos else "Break of structure is not confirmed.",
                weight=15,
            ),
            _ConfluenceSignal(
                name="MSS confirmed",
                detected=mss,
                importance=ImportanceLevel.MEDIUM,
                explanation="Market shift signal is present." if mss else "Market shift signal is not present.",
                weight=10,
            ),
            _ConfluenceSignal(
                name="FVG active",
                detected=zones.fvg.active,
                importance=ImportanceLevel.MEDIUM,
                explanation=zones.fvg.explanation,
                weight=10,
            ),
            _ConfluenceSignal(
                name="Institutional zone active",
                detected=institutional_zone_active,
                importance=ImportanceLevel.HIGH,
                explanation="At least one institutional zone is active."
                if institutional_zone_active
                else "No institutional zones are currently active.",
                weight=10,
            ),
            _ConfluenceSignal(
                name="Premium/Discount alignment",
                detected=zone_alignment,
                importance=ImportanceLevel.MEDIUM,
                explanation="Price location aligns with side (discount for BUY, premium for SELL)."
                if zone_alignment
                else "Price location does not align with side context.",
                weight=10,
            ),
            _ConfluenceSignal(
                name="Risk reward threshold",
                detected=rr_expected >= 1.5,
                importance=ImportanceLevel.HIGH,
                explanation=f"RR expected={rr_expected:.2f}",
                weight=15,
            ),
            _ConfluenceSignal(
                name="Liquidity sweep detected",
                detected=liquidity.liquidity_taken > 0,
                importance=ImportanceLevel.MEDIUM,
                explanation="Last candle swept liquidity pool." if liquidity.liquidity_taken > 0 else "No liquidity sweep on recent candle.",
                weight=5,
            ),
            _ConfluenceSignal(
                name="Volatility control",
                detected=(volatility <= 15 and risk_level != "HIGH"),
                importance=ImportanceLevel.LOW,
                explanation=f"Volatility={volatility:.2f} pips, risk={risk_level}.",
                weight=5,
            ),
            _ConfluenceSignal(
                name="CHOCH contradiction check",
                detected=(not choch) or bos,
                importance=ImportanceLevel.MEDIUM,
                explanation="No structural contradiction." if ((not choch) or bos) else "CHOCH without BOS adds directional contradiction.",
                weight=0,
            ),
        ]

        return signals

    @staticmethod
    def _institutional_score(confluences: list[_ConfluenceSignal], rr_expected: float) -> InstitutionalScoreReport:
        max_score = sum(item.weight for item in confluences if item.weight > 0)
        raw_score = sum(item.weight for item in confluences if item.weight > 0 and item.detected)

        confidence = (raw_score / max_score) * 100.0 if max_score > 0 else 0.0

        quality_level = QualityLevel.NO_TRADE
        if confidence >= 90:
            quality_level = QualityLevel.A_PLUS
        elif confidence >= 80:
            quality_level = QualityLevel.A
        elif confidence >= 65:
            quality_level = QualityLevel.B
        elif confidence >= 50:
            quality_level = QualityLevel.C

        if rr_expected < 1.0:
            quality_level = QualityLevel.NO_TRADE

        return InstitutionalScoreReport(
            score=int(raw_score),
            confidence=round(confidence, 2),
            quality_level=quality_level,
        )

    @staticmethod
    def _checklist(
        liquidity: LiquidityReport,
        structure,
        zones: InstitutionalZonesReport,
        rr_expected: float,
        risk_level: str,
        confluences: list[_ConfluenceSignal],
    ) -> list[ChecklistItem]:
        bos = bool(getattr(structure, "bos", False)) if structure is not None else False
        contradiction_free = next(
            (item.detected for item in confluences if item.name == "CHOCH contradiction check"),
            True,
        )

        return [
            ChecklistItem(
                label="Liquidity taken",
                checked=liquidity.liquidity_taken > 0,
                explanation="Recent sweep is required to confirm liquidity engagement.",
            ),
            ChecklistItem(
                label="BOS confirmed",
                checked=bos,
                explanation="Break of structure confirms directional continuation.",
            ),
            ChecklistItem(
                label="FVG mitigated",
                checked=zones.fvg.active and zones.mitigation.active,
                explanation="FVG should be active with mitigation context.",
            ),
            ChecklistItem(
                label="Institutional zone",
                checked=(zones.order_block.active or zones.breaker.active or zones.mitigation.active),
                explanation="At least one institutional zone must be active.",
            ),
            ChecklistItem(
                label="Risk valid",
                checked=(rr_expected >= 1.5 and risk_level != "HIGH"),
                explanation="Risk is valid when RR is above threshold and risk is not HIGH.",
            ),
            ChecklistItem(
                label="No contradictions",
                checked=contradiction_free,
                explanation="Structural signals should not conflict for execution readiness.",
            ),
        ]

    @staticmethod
    def _recommendation(
        decision: DecisionContext,
        market_bias: MarketBiasReport,
        institutional_score: InstitutionalScoreReport,
        rr_expected: float,
        risk_level: str,
        confluences: list[_ConfluenceSignal],
    ) -> FinalRecommendation:
        contradictions = [item for item in confluences if item.name == "CHOCH contradiction check" and not item.detected]

        if institutional_score.quality_level == QualityLevel.NO_TRADE or rr_expected < 1.0:
            return FinalRecommendation(
                recommendation=RecommendationType.NO_TRADE,
                explanation=(
                    "Setup quality is insufficient for execution. "
                    f"Quality={institutional_score.quality_level.value}, RR={rr_expected:.2f}."
                ),
            )

        if risk_level == "HIGH" or contradictions:
            return FinalRecommendation(
                recommendation=RecommendationType.WAIT,
                explanation=(
                    "Market shows elevated risk or structural contradiction. "
                    f"Risk={risk_level}, contradictions={len(contradictions)}."
                ),
            )

        if institutional_score.confidence >= 70 and rr_expected >= 1.5:
            if decision.side == TradeSide.BUY and market_bias.bias == MarketBias.BULLISH:
                return FinalRecommendation(
                    recommendation=RecommendationType.BUY,
                    explanation=(
                        "Directional confluence supports BUY: bullish bias, acceptable risk, "
                        "and score above threshold. Final decision remains with the trader."
                    ),
                )

            if decision.side == TradeSide.SELL and market_bias.bias == MarketBias.BEARISH:
                return FinalRecommendation(
                    recommendation=RecommendationType.SELL,
                    explanation=(
                        "Directional confluence supports SELL: bearish bias, acceptable risk, "
                        "and score above threshold. Final decision remains with the trader."
                    ),
                )

        return FinalRecommendation(
            recommendation=RecommendationType.WAIT,
            explanation=(
                "Confluences are partial or directional alignment is weak. "
                "Waiting for clearer confirmation is recommended."
            ),
        )

    @staticmethod
    def _narrative(
        decision: DecisionContext,
        market_bias: MarketBiasReport,
        liquidity: LiquidityReport,
        market_structure: MarketStructureReport,
        zones: InstitutionalZonesReport,
        risk_level: str,
        rr_expected: float,
        institutional_score: InstitutionalScoreReport,
        recommendation: FinalRecommendation,
    ) -> str:
        side_text = "compra" if decision.side == TradeSide.BUY else "venta"
        trend_text = market_structure.trend.lower()

        return (
            f"El mercado presenta un sesgo {market_bias.bias.value.lower()} con tendencia {trend_text}. "
            f"La liquidez compradora ({liquidity.buy_liquidity}) y vendedora ({liquidity.sell_liquidity}) "
            f"muestra una toma de liquidez de {liquidity.liquidity_taken}. "
            f"En estructura se observa BOS={market_structure.bos}, CHOCH={market_structure.choch} y MSS={market_structure.mss}. "
            f"Las zonas institucionales activas son: order block={zones.order_block.active}, "
            f"breaker={zones.breaker.active}, mitigation={zones.mitigation.active}, FVG={zones.fvg.active}. "
            f"El riesgo actual es {risk_level} con RR esperado de {rr_expected:.2f} y calidad {institutional_score.quality_level.value}. "
            f"La recomendacion final para el contexto de {side_text} es {recommendation.recommendation.value}. "
            "La decision final corresponde al trader."
        )
