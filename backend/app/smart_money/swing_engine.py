# backend/app/smart_money/swing_engine.py

from dataclasses import dataclass


@dataclass(slots=True)
class SwingPoint:
    index: int
    time: str
    price: float
    kind: str  # HIGH | LOW
    structure: str | None = None  # HH | HL | LH | LL


class SwingEngine:

    @staticmethod
    def detect(
        candles: list,
        left: int = 3,
        right: int = 3,
    ) -> list[SwingPoint]:

        if len(candles) < (left + right + 1):
            return []

        swings: list[SwingPoint] = []

        for i in range(left, len(candles) - right):

            current = candles[i]

            is_high = True
            is_low = True

            # -------- LEFT --------

            for j in range(i - left, i):

                if candles[j]["high"] >= current["high"]:
                    is_high = False

                if candles[j]["low"] <= current["low"]:
                    is_low = False

            # -------- RIGHT --------

            for j in range(i + 1, i + right + 1):

                if candles[j]["high"] > current["high"]:
                    is_high = False

                if candles[j]["low"] < current["low"]:
                    is_low = False

            if is_high:

                swings.append(

                    SwingPoint(
                        index=i,
                        time=str(current["time"]),
                        price=float(current["high"]),
                        kind="HIGH",
                    )

                )

            if is_low:

                swings.append(

                    SwingPoint(
                        index=i,
                        time=str(current["time"]),
                        price=float(current["low"]),
                        kind="LOW",
                    )

                )

        return SwingEngine.classify(swings)

    @staticmethod
    def classify(
        swings: list[SwingPoint],
    ) -> list[SwingPoint]:

        last_high = None
        last_low = None

        for swing in swings:

            if swing.kind == "HIGH":

                if last_high is None:

                    swing.structure = "HH"

                else:

                    if swing.price > last_high:

                        swing.structure = "HH"

                    else:

                        swing.structure = "LH"

                last_high = swing.price

            else:

                if last_low is None:

                    swing.structure = "LL"

                else:

                    if swing.price > last_low:

                        swing.structure = "HL"

                    else:

                        swing.structure = "LL"

                last_low = swing.price

        return swings