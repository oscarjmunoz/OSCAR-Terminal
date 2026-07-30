import MetaTrader5 as mt5

from app.market.schemas import TerminalStatus
from app.market.schemas import TickResponse


class MarketService:

    @staticmethod
    def _resolve_symbol(symbol: str) -> str | None:
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

    @staticmethod
    def terminal_status() -> TerminalStatus:

        if not mt5.initialize():
            return TerminalStatus(connected=False)

        info = mt5.account_info()

        if info is None:
            mt5.shutdown()
            return TerminalStatus(connected=False)

        result = TerminalStatus(
            connected=True,
            account=info.login,
            company=info.company,
            server=info.server,
        )

        mt5.shutdown()

        return result

    @staticmethod
    def latest_tick(symbol: str):

        if not mt5.initialize():
            return None

        real_symbol = MarketService._resolve_symbol(symbol)

        if real_symbol is None:
            mt5.shutdown()
            return None

        mt5.symbol_select(real_symbol, True)

        tick = mt5.symbol_info_tick(real_symbol)

        if tick is None:
            mt5.shutdown()
            return None

        result = TickResponse(
            symbol=real_symbol,
            bid=tick.bid,
            ask=tick.ask,
            spread=round((tick.ask - tick.bid) * 10000, 1),
        )

        mt5.shutdown()

        return result