from datetime import datetime

import MetaTrader5 as mt5

from app.market.schemas import CandleResponse
from app.market.schemas import TerminalStatus
from app.market.schemas import TickResponse
from app.market.timeframes import TIMEFRAMES
from app.market.market_state import MarketState
from app.market.schemas import MarketStateResponse


class MarketService:

    _initialized = False

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return True

        cls._initialized = mt5.initialize()
        return cls._initialized

    @staticmethod
    def _resolve_symbol(symbol: str):

        symbols = mt5.symbols_get()

        if symbols is None:
            return None

        symbol = symbol.upper()

        # Coincidencia exacta
        for item in symbols:
            if item.name.upper() == symbol:
                return item.name

        # Coincidencia por prefijo
        for item in symbols:
            if item.name.upper().startswith(symbol):
                return item.name

        return None

    @classmethod
    def terminal_status(cls):

        if not cls.initialize():
            return TerminalStatus(connected=False)

        info = mt5.account_info()

        if info is None:
            return TerminalStatus(connected=False)

        return TerminalStatus(
            connected=True,
            account=info.login,
            company=info.company,
            server=info.server,
        )

    @classmethod
    def latest_tick(cls, symbol: str):

        if not cls.initialize():
            return None

        real_symbol = cls._resolve_symbol(symbol)

        if real_symbol is None:
            return None

        mt5.symbol_select(real_symbol, True)

        tick = mt5.symbol_info_tick(real_symbol)

        if tick is None:
            return None

        return TickResponse(
            symbol=real_symbol,
            bid=tick.bid,
            ask=tick.ask,
            spread=round((tick.ask - tick.bid) * 10000, 1),
        )

    @classmethod
    def latest_tick_time(cls, symbol: str):

        if not cls.initialize():
            return None

        real_symbol = cls._resolve_symbol(symbol)

        if real_symbol is None:
            return None

        mt5.symbol_select(real_symbol, True)

        tick = mt5.symbol_info_tick(real_symbol)

        if tick is None or getattr(tick, "time", None) is None:
            return None

        return datetime.fromtimestamp(int(tick.time))

    @classmethod
    def latest_candle_time(cls, symbol: str, timeframe: str):

        if not cls.initialize():
            return None

        real_symbol = cls._resolve_symbol(symbol)

        if real_symbol is None:
            return None

        tf = TIMEFRAMES.get(timeframe.upper())

        if tf is None:
            return None

        rates = mt5.copy_rates_from_pos(
            real_symbol,
            tf,
            0,
            1,
        )

        if rates is None or len(rates) == 0:
            return None

        return datetime.fromtimestamp(int(rates[-1]["time"]))

    @classmethod
    def candles(cls, symbol: str, timeframe: str, count: int = 200):

        if not cls.initialize():
            return None

        real_symbol = cls._resolve_symbol(symbol)

        if real_symbol is None:
            return None

        mt5.symbol_select(real_symbol, True)

        tf = TIMEFRAMES.get(timeframe.upper())

        if tf is None:
            return None

        rates = mt5.copy_rates_from_pos(
            real_symbol,
            tf,
            0,
            count,
        )

        if rates is None:
            return None

        candles = []

        for bar in rates:

            candles.append(
                CandleResponse(
                    time=datetime.fromtimestamp(int(bar["time"])),
                    open=float(bar["open"]),
                    high=float(bar["high"]),
                    low=float(bar["low"]),
                    close=float(bar["close"]),
                    tick_volume=int(bar["tick_volume"]),
                )
            )

        return candles