# backend/app/smart_money/market_structure.py

from app.smart_money.geometry import GeometryEngine
from app.smart_money.models import MarketStructure
from app.smart_money.models import Swing


class MarketStructureEngine:

    @staticmethod
    def analyze(
        swings: list[Swing],
    ) -> MarketStructure:
        """
        Analiza la estructura del mercado a partir de los swings
        detectados.

        Devuelve:

        - Tendencia
        - Último HH
        - Último LL
        - BOS
        - CHoCH
        - MSS

        En futuras versiones este motor calculará además:

        - Internal Structure
        - External Structure
        - Break Strength
        - Liquidity Sweeps
        - Protected High / Low
        - Premium / Discount
        """

        if not swings:

            return MarketStructure(
                trend="RANGE",
                last_high=None,
                last_low=None,
                bos=False,
                choch=False,
                mss=False,
            )

        return GeometryEngine.market_structure(
            swings
        )

    @staticmethod
    def trend(
        swings: list[Swing],
    ) -> str:

        return MarketStructureEngine.analyze(
            swings
        ).trend

    @staticmethod
    def is_bullish(
        swings: list[Swing],
    ) -> bool:

        return (
            MarketStructureEngine.trend(
                swings
            )
            == "BULLISH"
        )

    @staticmethod
    def is_bearish(
        swings: list[Swing],
    ) -> bool:

        return (
            MarketStructureEngine.trend(
                swings
            )
            == "BEARISH"
        )