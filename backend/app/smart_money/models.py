# backend/app/smart_money/models.py

from dataclasses import dataclass


@dataclass(slots=True)
class Swing:

    index: int

    time: str

    price: float

    kind: str

    structure: str


@dataclass(slots=True)
class MarketStructure:

    trend: str

    last_high: float | None

    last_low: float | None

    bos: bool = False

    choch: bool = False

    mss: bool = False