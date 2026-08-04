import MetaTrader5 as mt5

from app.services.trade_errors import InsufficientMargin


class RiskEngine:

    @staticmethod
    def check_margin(order_type: int, symbol: str, volume: float, price: float):
        account = mt5.account_info()

        if account is None:
            return True

        margin_required = None

        if hasattr(mt5, "order_calc_margin"):
            margin_required = mt5.order_calc_margin(
                order_type,
                symbol,
                volume,
                price,
            )

        if margin_required is None:
            return True

        free_margin = getattr(account, "margin_free", None)

        if free_margin is None:
            return True

        if margin_required > free_margin:
            raise InsufficientMargin()

        return True