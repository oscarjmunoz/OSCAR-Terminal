# backend/app/smart_money/geometry.py

from app.smart_money.models import MarketStructure
from app.smart_money.models import Swing


class GeometryEngine:

    @staticmethod
    def market_structure(
        swings: list[Swing],
    ) -> MarketStructure:

        highs = [
            swing
            for swing in swings
            if swing.kind == "HIGH"
        ]

        lows = [
            swing
            for swing in swings
            if swing.kind == "LOW"
        ]

        last_high = (
            highs[-1].price
            if highs
            else None
        )

        last_low = (
            lows[-1].price
            if lows
            else None
        )

        hh = sum(
            1
            for swing in highs
            if swing.structure == "HH"
        )

        lh = sum(
            1
            for swing in highs
            if swing.structure == "LH"
        )

        hl = sum(
            1
            for swing in lows
            if swing.structure == "HL"
        )

        ll = sum(
            1
            for swing in lows
            if swing.structure == "LL"
        )

        trend = "RANGE"

        if hh > lh and hl > ll:
            trend = "BULLISH"

        elif lh > hh and ll > hl:
            trend = "BEARISH"

        structure = MarketStructure(

            trend=trend,

            last_high=last_high,

            last_low=last_low,

            bos=False,

            choch=False,

            mss=False,

        )

        if len(swings) >= 2:

            previous = swings[-2]

            current = swings[-1]

            # -------- BOS --------

            if (
                trend == "BULLISH"
                and current.kind == "HIGH"
                and current.structure == "HH"
            ):
                structure.bos = True

            elif (
                trend == "BEARISH"
                and current.kind == "LOW"
                and current.structure == "LL"
            ):
                structure.bos = True

            # -------- CHoCH --------

            if (
                previous.structure == "HH"
                and current.structure == "LL"
            ):
                structure.choch = True

            elif (
                previous.structure == "LL"
                and current.structure == "HH"
            ):
                structure.choch = True

            # -------- MSS --------

            if (
                previous.kind != current.kind
                and previous.structure != current.structure
            ):
                structure.mss = True

        return structure