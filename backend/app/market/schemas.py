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
    