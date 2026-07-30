# backend/app/smart_money/service.py
# REEMPLAZAR COMPLETAMENTE EL ARCHIVO

from app.market.service import MarketService

from app.smart_money.models import Swing
from app.smart_money.market_structure import MarketStructureEngine
from app.smart_money.schemas import SwingResponse
from app.smart_money.swing_engine import SwingEngine


class SmartMoneyService:

    @staticmethod
    def swings(
        symbol: str,
        timeframe: str = "M5",
        candles: int = 300,
        left: int = 3,
        right: int = 3,
    ) -> list[SwingResponse]:

        bars = MarketService.candles(
            symbol=symbol,
            timeframe=timeframe,
            count=candles,
        )

        if not bars:
            return []

        raw = []

        for candle in bars:

            raw.append(
                {
                    "time": candle.time.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "tick_volume": candle.tick_volume,
                }
            )

        swings = SwingEngine.detect(
            candles=raw,
            left=left,
            right=right,
        )

        response = []

        for swing in swings:

            response.append(

                SwingResponse(

                    index=swing.index,

                    time=swing.time,

                    price=swing.price,

                    kind=swing.kind,

                    structure=swing.structure or "",

                )

            )

        return response

    @staticmethod
    def structure(
        symbol: str,
        timeframe: str = "M5",
        candles: int = 300,
        left: int = 3,
        right: int = 3,
    ):

        bars = MarketService.candles(
            symbol=symbol,
            timeframe=timeframe,
            count=candles,
        )

        if not bars:
            return None

        raw = []

        for candle in bars:

            raw.append(
                {
                    "time": candle.time.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                }
            )

        detected = SwingEngine.detect(
            raw,
            left,
            right,
        )

        swings = [

            Swing(

                index=s.index,

                time=s.time,

                price=s.price,

                kind=s.kind,

                structure=s.structure or "",

            )

            for s in detected

        ]

        return MarketStructureEngine.analyze(
            swings
        )