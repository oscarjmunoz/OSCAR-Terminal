from __future__ import annotations

from dataclasses import dataclass

from app.market.service import MarketService
from app.market.timeframes import TIMEFRAMES
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.decision_center import ConfluenceItem
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import FinalRecommendation
from app.schemas.decision_center import RiskAssessmentReport
from app.services.decision_center import DecisionCenter
from app.services.multi_timeframe_bias import MultiTimeframeBiasService
from app.smart_money.service import SmartMoneyService


class OperationalAnalysisError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(slots=True)
class LiveAnalysisRequest:
    symbol: str
    timeframe: str


class OperationalAnalysisService:

    @staticmethod
    def build_report(request: LiveAnalysisRequest) -> DecisionReport:
        timeframe = request.timeframe.strip().upper()

        if timeframe not in TIMEFRAMES:
            raise OperationalAnalysisError(
                code="invalid_timeframe",
                message=f"Unsupported timeframe: {request.timeframe}",
            )

        terminal = MarketService.terminal_status()
        if not terminal.connected:
            raise OperationalAnalysisError(
                code="mt5_disconnected",
                message="MT5 is disconnected.",
            )

        tick = MarketService.latest_tick(request.symbol)
        candles = MarketService.candles(request.symbol, timeframe=timeframe, count=120) or []
        structure = SmartMoneyService.structure(request.symbol, timeframe=timeframe, candles=300, left=3, right=3)

        if tick is None and not candles:
            raise OperationalAnalysisError(
                code="no_data",
                message="No market data available for the selected symbol and timeframe.",
            )

        decision = OperationalAnalysisService._build_context(
            symbol=request.symbol,
            timeframe=timeframe,
            tick=tick,
            candles=candles,
            structure=structure,
        )

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
        multi_timeframe_bias = MultiTimeframeBiasService.build_report(
            request.symbol,
            m5_candles=candles,
            m5_structure=structure,
            include_higher_timeframes=False,
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
            multi_timeframe_bias=multi_timeframe_bias,
        )

    @staticmethod
    def _build_context(symbol: str, timeframe: str, tick, candles, structure) -> DecisionContext:
        side = TradeSide.SELL if getattr(structure, "trend", "RANGE") == "BEARISH" else TradeSide.BUY

        if tick is not None:
            price = float(tick.ask if side == TradeSide.BUY else tick.bid)
        elif candles:
            price = float(candles[-1].close)
        else:
            price = None

        sl, tp = OperationalAnalysisService._project_levels(side, price, candles, structure)

        return DecisionContext(
            symbol=symbol.upper(),
            side=side,
            volume=0.10,
            sl=sl,
            tp=tp,
            price=price,
            comment=f"live-operational-analysis:{timeframe}",
        )

    @staticmethod
    def _project_levels(side: TradeSide, price: float | None, candles, structure) -> tuple[float | None, float | None]:
        if price is None or not candles:
            return None, None

        recent_window = candles[-20:] if len(candles) >= 20 else candles
        recent_high = max(float(candle.high) for candle in recent_window)
        recent_low = min(float(candle.low) for candle in recent_window)

        structure_high = getattr(structure, "last_high", None)
        structure_low = getattr(structure, "last_low", None)
        anchor_high = max(recent_high, float(structure_high)) if structure_high is not None else recent_high
        anchor_low = min(recent_low, float(structure_low)) if structure_low is not None else recent_low

        if side == TradeSide.BUY:
            sl = anchor_low
            risk = max(price - sl, max(anchor_high - anchor_low, price * 0.001) / 2)
            tp = price + (risk * 2)
            if sl >= price:
                sl = price - max(risk, price * 0.001)
            if tp <= price:
                tp = price + max(risk * 2, price * 0.002)
            return round(sl, 5), round(tp, 5)

        sl = anchor_high
        risk = max(sl - price, max(anchor_high - anchor_low, price * 0.001) / 2)
        tp = price - (risk * 2)
        if sl <= price:
            sl = price + max(risk, price * 0.001)
        if tp >= price:
            tp = price - max(risk * 2, price * 0.002)
        return round(sl, 5), round(tp, 5)
