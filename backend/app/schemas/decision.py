from enum import Enum

from pydantic import BaseModel


class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class DecisionContext(BaseModel):
    symbol: str
    side: TradeSide
    volume: float
    sl: float | None = None
    tp: float | None = None
    comment: str | None = None
    ticket: int | None = None
    price: float | None = None