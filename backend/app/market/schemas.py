from datetime import datetime

from pydantic import BaseModel


class TerminalStatus(BaseModel):
    connected: bool
    account: int | None = None
    company: str | None = None
    server: str | None = None


class TickResponse(BaseModel):
    symbol: str
    bid: float
    ask: float
    spread: float


class CandleResponse(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int


class MarketStateResponse(BaseModel):
    market_open: bool
    session: str
    spread: float
    spread_status: str
    tradable: bool
    reason: str | None = None