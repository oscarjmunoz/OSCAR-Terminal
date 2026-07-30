import MetaTrader5 as mt5

from app.market.schemas import TerminalStatus


class MarketService:

    @staticmethod
    def terminal_status() -> TerminalStatus:

        if not mt5.initialize():

            return TerminalStatus(
                connected=False,
            )

        info = mt5.account_info()

        if info is None:

            mt5.shutdown()

            return TerminalStatus(
                connected=False,
            )

        status = TerminalStatus(
            connected=True,
            account=info.login,
            company=info.company,
            server=info.server,
        )

        mt5.shutdown()

        return status