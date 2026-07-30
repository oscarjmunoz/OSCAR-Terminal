# backend/app/smart_money/schemas.py
# REEMPLAZAR COMPLETAMENTE EL ARCHIVO

from pydantic import BaseModel


class SwingRequest(BaseModel):

    symbol: str

    timeframe: str = "M5"

    candles: int = 300

    left: int = 3

    right: int = 3


class SwingResponse(BaseModel):

    index: int

    time: str

    price: float

    kind: str

    structure: str


class MarketStructureResponse(BaseModel):

    trend: str

    last_high: float | None = None

    last_low: float | None = None

    bos: bool

    choch: bool

    mss: bool