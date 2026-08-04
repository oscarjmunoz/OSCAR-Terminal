class TradeError(Exception):
    default_message = "Trade operation failed"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


class ConnectionError(TradeError):
    default_message = "MT5 connection unavailable"


class InvalidOrder(TradeError):
    default_message = "Invalid order"


class BrokerRejected(TradeError):
    default_message = "Broker rejected the order"


class TradeDisabled(TradeError):
    default_message = "Trading is disabled"


class MarketClosed(TradeError):
    default_message = "Market is closed"


class InsufficientMargin(TradeError):
    default_message = "Insufficient margin"