from typing import Any

from pydantic import BaseModel


class TradeOrder(BaseModel):
    action: int
    symbol: str
    volume: float
    orderType: int
    price: float
    sl: float | None = None
    tp: float | None = None
    deviation: int
    magicNumber: int
    comment: str | None = None
    position: int | None = None
    order: int | None = None

    def as_mt5_request(self) -> dict[str, Any]:
        request: dict[str, Any] = {
            "action": self.action,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": self.orderType,
            "price": self.price,
            "deviation": self.deviation,
            "magic": self.magicNumber,
            "comment": self.comment,
        }

        if self.sl is not None:
            request["sl"] = self.sl

        if self.tp is not None:
            request["tp"] = self.tp

        if self.position is not None:
            request["position"] = self.position

        if self.order is not None:
            request["order"] = self.order

        return request


class TradeResult(BaseModel):
    success: bool
    ticket: int | None = None
    order: TradeOrder | None = None
    price: float | None = None
    volume: float | None = None
    sl: float | None = None
    tp: float | None = None
    brokerMessage: str | None = None
    executionTime: float | None = None
    error: str | None = None


class TicketRequest(BaseModel):
    ticket: int


class StopLossRequest(BaseModel):
    ticket: int
    stopLoss: float


class TakeProfitRequest(BaseModel):
    ticket: int
    takeProfit: float