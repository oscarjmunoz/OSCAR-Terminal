import MetaTrader5 as mt5

from app.config.settings import settings
from app.engines.risk_engine import RiskEngine
from app.market.service import MarketService
from app.services.trade_errors import ConnectionError
from app.services.trade_errors import InvalidOrder
from app.services.trade_errors import MarketClosed
from app.services.trade_errors import TradeDisabled


class OrderValidator:

    def __init__(self, risk_engine: RiskEngine | None = None):
        self._risk_engine = risk_engine or RiskEngine()

    def validate_market_order(
        self,
        symbol: str,
        volume: float,
        side: str,
        price: float,
        sl: float | None,
        tp: float | None,
        order_type: int,
    ):

        if not MarketService.initialize():
            raise ConnectionError()

        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            raise InvalidOrder(f"Symbol not available: {symbol}")

        terminal_info = mt5.terminal_info()

        if terminal_info is not None and not getattr(terminal_info, "trade_allowed", True):
            raise TradeDisabled()

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            raise MarketClosed()

        if volume <= 0:
            raise InvalidOrder("Volume must be greater than zero")

        minimum = float(getattr(symbol_info, "volume_min", 0.0) or 0.0)
        maximum = float(getattr(symbol_info, "volume_max", 0.0) or 0.0)
        step = float(getattr(symbol_info, "volume_step", 0.0) or 0.0)

        if volume < minimum:
            raise InvalidOrder("Volume below minimum")

        if maximum and volume > maximum:
            raise InvalidOrder("Volume above maximum")

        if step:
            steps = round((volume - minimum) / step)
            aligned = minimum + steps * step

            if abs(aligned - volume) > 1e-9:
                raise InvalidOrder("Volume does not match symbol step")

        self._validate_stops(side, price, sl, tp)

        spread_points = self._spread_points(symbol_info, tick)

        if spread_points > settings.maxSlippage:
            raise MarketClosed("Spread exceeds configured max slippage")

        self._risk_engine.check_margin(order_type, symbol, volume, price)

    def validate_position(self, position):

        if position is None:
            raise InvalidOrder("Position not found")

    def validate_pending_order(self, order):

        if order is None:
            raise InvalidOrder("Pending order not found")

    def _validate_stops(
        self,
        side: str,
        price: float,
        sl: float | None,
        tp: float | None,
    ):

        if side == "BUY":
            if sl is not None and sl >= price:
                raise InvalidOrder("Stop Loss must be below buy price")

            if tp is not None and tp <= price:
                raise InvalidOrder("Take Profit must be above buy price")

        if side == "SELL":
            if sl is not None and sl <= price:
                raise InvalidOrder("Stop Loss must be above sell price")

            if tp is not None and tp >= price:
                raise InvalidOrder("Take Profit must be below sell price")

    def _spread_points(self, symbol_info, tick) -> float:

        point = float(getattr(symbol_info, "point", 0.0) or 0.0)

        if point <= 0:
            return 0.0

        ask = float(getattr(tick, "ask", 0.0) or 0.0)
        bid = float(getattr(tick, "bid", 0.0) or 0.0)

        return abs(ask - bid) / point