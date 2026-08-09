from __future__ import annotations

from app.market.service import MarketService
from app.schemas.decision_center import MultiTimeframeAlignment
from app.schemas.decision_center import MultiTimeframeBiasItem
from app.schemas.decision_center import MultiTimeframeBiasReport
from app.schemas.decision_center import MultiTimeframeBiasState
from app.schemas.decision_center import MultiTimeframeContextConfidence
from app.schemas.decision_center import MultiTimeframeDataAvailability
from app.schemas.decision_center import MultiTimeframeStructureConfidence
from app.smart_money.service import SmartMoneyService


class MultiTimeframeBiasService:

    @staticmethod
    def build_report(
        symbol: str,
        *,
        m5_candles=None,
        m5_structure=None,
        h4_candles=None,
        h1_candles=None,
        h4_structure=None,
        h1_structure=None,
        include_higher_timeframes: bool = True,
    ) -> MultiTimeframeBiasReport:
        h4_item = MultiTimeframeBiasService._build_timeframe_item(
            timeframe="H4",
            symbol=symbol,
            candles=h4_candles if h4_candles is not None else (None if not include_higher_timeframes else MarketService.candles(symbol, timeframe="H4", count=120)),
            structure=h4_structure if h4_structure is not None else (None if not include_higher_timeframes else SmartMoneyService.structure(symbol, timeframe="H4", candles=300, left=3, right=3)),
        )
        h1_item = MultiTimeframeBiasService._build_timeframe_item(
            timeframe="H1",
            symbol=symbol,
            candles=h1_candles if h1_candles is not None else (None if not include_higher_timeframes else MarketService.candles(symbol, timeframe="H1", count=120)),
            structure=h1_structure if h1_structure is not None else (None if not include_higher_timeframes else SmartMoneyService.structure(symbol, timeframe="H1", candles=300, left=3, right=3)),
        )
        m5_item = MultiTimeframeBiasService._build_timeframe_item(
            timeframe="M5",
            symbol=symbol,
            candles=m5_candles if m5_candles is not None else MarketService.candles(symbol, timeframe="M5", count=120),
            structure=m5_structure if m5_structure is not None else SmartMoneyService.structure(symbol, timeframe="M5", candles=300, left=3, right=3),
        )

        alignment = MultiTimeframeBiasService._alignment([h4_item, h1_item, m5_item])
        conflict = alignment in {MultiTimeframeAlignment.CONFLICT}
        confidence = MultiTimeframeBiasService._confidence(alignment)
        summary = MultiTimeframeBiasService._summary(alignment, h4_item, h1_item, m5_item)

        return MultiTimeframeBiasReport(
            h4=h4_item,
            h1=h1_item,
            m5=m5_item,
            alignment=alignment,
            conflict=conflict,
            confidence=confidence,
            summary=summary,
        )

    @staticmethod
    def _build_timeframe_item(timeframe: str, symbol: str, candles, structure) -> MultiTimeframeBiasItem:
        if not candles:
            return MultiTimeframeBiasItem(
                timeframe=timeframe,
                bias=MultiTimeframeBiasState.UNAVAILABLE,
                bos=False,
                choch=False,
                mss=False,
                structure_confidence=MultiTimeframeStructureConfidence.UNAVAILABLE,
                data_availability=MultiTimeframeDataAvailability.UNAVAILABLE,
                explanation=f"No candles available for {timeframe} on {symbol}.",
            )

        if structure is None:
            return MultiTimeframeBiasItem(
                timeframe=timeframe,
                bias=MultiTimeframeBiasState.UNAVAILABLE,
                bos=False,
                choch=False,
                mss=False,
                structure_confidence=MultiTimeframeStructureConfidence.UNAVAILABLE,
                data_availability=MultiTimeframeDataAvailability.DEGRADED,
                explanation=f"Structure could not be evaluated for {timeframe} on {symbol}.",
            )

        trend = getattr(structure, "trend", "RANGE")
        if trend == "BULLISH":
            bias = MultiTimeframeBiasState.BULLISH
        elif trend == "BEARISH":
            bias = MultiTimeframeBiasState.BEARISH
        else:
            bias = MultiTimeframeBiasState.NEUTRAL

        structure_confidence = MultiTimeframeStructureConfidence.HIGH
        if trend == "RANGE":
            structure_confidence = MultiTimeframeStructureConfidence.LOW
        elif not any([bool(getattr(structure, "bos", False)), bool(getattr(structure, "choch", False)), bool(getattr(structure, "mss", False))]):
            structure_confidence = MultiTimeframeStructureConfidence.MEDIUM

        return MultiTimeframeBiasItem(
            timeframe=timeframe,
            bias=bias,
            bos=bool(getattr(structure, "bos", False)),
            choch=bool(getattr(structure, "choch", False)),
            mss=bool(getattr(structure, "mss", False)),
            structure_confidence=structure_confidence,
            data_availability=MultiTimeframeDataAvailability.AVAILABLE,
            explanation=f"{timeframe} structure trend={trend} with BOS={bool(getattr(structure, 'bos', False))}, CHOCH={bool(getattr(structure, 'choch', False))}, MSS={bool(getattr(structure, 'mss', False))}.",
        )

    @staticmethod
    def _alignment(items: list[MultiTimeframeBiasItem]) -> MultiTimeframeAlignment:
        if not items:
            return MultiTimeframeAlignment.UNAVAILABLE

        if any(item.bias == MultiTimeframeBiasState.UNAVAILABLE for item in items):
            return MultiTimeframeAlignment.UNAVAILABLE

        unique = {item.bias for item in items}
        if len(unique) == 1:
            if MultiTimeframeBiasState.BULLISH in unique:
                return MultiTimeframeAlignment.ALIGNED_BULLISH
            if MultiTimeframeBiasState.BEARISH in unique:
                return MultiTimeframeAlignment.ALIGNED_BEARISH
            return MultiTimeframeAlignment.MIXED

        if {MultiTimeframeBiasState.BULLISH, MultiTimeframeBiasState.BEARISH}.issubset(unique):
            if items[0].bias == items[-1].bias:
                return MultiTimeframeAlignment.MIXED
            return MultiTimeframeAlignment.CONFLICT

        return MultiTimeframeAlignment.MIXED

    @staticmethod
    def _confidence(alignment: MultiTimeframeAlignment) -> MultiTimeframeContextConfidence:
        if alignment in {MultiTimeframeAlignment.ALIGNED_BULLISH, MultiTimeframeAlignment.ALIGNED_BEARISH}:
            return MultiTimeframeContextConfidence.HIGH
        if alignment == MultiTimeframeAlignment.CONFLICT:
            return MultiTimeframeContextConfidence.LOW
        if alignment == MultiTimeframeAlignment.UNAVAILABLE:
            return MultiTimeframeContextConfidence.UNAVAILABLE
        return MultiTimeframeContextConfidence.MEDIUM

    @staticmethod
    def _summary(
        alignment: MultiTimeframeAlignment,
        h4: MultiTimeframeBiasItem,
        h1: MultiTimeframeBiasItem,
        m5: MultiTimeframeBiasItem,
    ) -> str:
        if alignment == MultiTimeframeAlignment.ALIGNED_BULLISH:
            return "Higher timeframe context is aligned bullish across H4, H1, and M5."
        if alignment == MultiTimeframeAlignment.ALIGNED_BEARISH:
            return "Higher timeframe context is aligned bearish across H4, H1, and M5."
        if alignment == MultiTimeframeAlignment.CONFLICT:
            return "Higher timeframe context is conflicting and should reduce execution aggressiveness."
        if alignment == MultiTimeframeAlignment.UNAVAILABLE:
            return "Higher timeframe context is unavailable due to missing data."
        return f"Mixed higher timeframe context: H4={h4.bias.value}, H1={h1.bias.value}, M5={m5.bias.value}."
