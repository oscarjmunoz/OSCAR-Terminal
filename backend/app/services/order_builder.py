import MetaTrader5 as mt5

from app.config.settings import settings
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.trade import TradeOrder
from app.services.trade_errors import InvalidOrder


class OrderBuilder:

    def build_market_order(
        self,
        decision: DecisionContext,
        price: float,
    ) -> TradeOrder:

        if not decision.symbol:
            raise InvalidOrder("Symbol is required")

        if decision.volume <= 0:
            raise InvalidOrder("Volume is required")

        if decision.side == TradeSide.BUY:
            order_type = getattr(mt5, "ORDER_TYPE_BUY")
            action = getattr(mt5, "TRADE_ACTION_DEAL")
        else:
            order_type = getattr(mt5, "ORDER_TYPE_SELL")
            action = getattr(mt5, "TRADE_ACTION_DEAL")

        return TradeOrder(
            action=action,
            symbol=decision.symbol,
            volume=decision.volume,
            orderType=order_type,
            price=price,
            sl=decision.sl,
            tp=decision.tp,
            deviation=settings.defaultDeviation,
            magicNumber=settings.magicNumber,
            comment=decision.comment,
        )

    def build_close_order(
        self,
        position,
        price: float,
    ) -> TradeOrder:

        position_type = getattr(position, "type", None)

        if position_type is None:
            raise InvalidOrder("Position type is required")

        if position_type == getattr(mt5, "POSITION_TYPE_BUY", 0):
            order_type = getattr(mt5, "ORDER_TYPE_SELL")
        else:
            order_type = getattr(mt5, "ORDER_TYPE_BUY")

        return TradeOrder(
            action=getattr(mt5, "TRADE_ACTION_DEAL"),
            symbol=position.symbol,
            volume=float(position.volume),
            orderType=order_type,
            price=price,
            deviation=settings.defaultDeviation,
            magicNumber=settings.magicNumber,
            comment="OSCAR close position",
            position=position.ticket,
        )

    def build_modify_sl_order(self, position, stop_loss: float) -> TradeOrder:

        return TradeOrder(
            action=getattr(mt5, "TRADE_ACTION_SLTP"),
            symbol=position.symbol,
            volume=float(position.volume),
            orderType=getattr(mt5, "ORDER_TYPE_BUY"),
            price=float(getattr(position, "price_current", 0.0) or 0.0),
            sl=stop_loss,
            tp=float(getattr(position, "tp", 0.0) or 0.0) or None,
            deviation=settings.defaultDeviation,
            magicNumber=settings.magicNumber,
            comment="OSCAR modify SL",
            position=position.ticket,
        )

    def build_modify_tp_order(self, position, take_profit: float) -> TradeOrder:

        return TradeOrder(
            action=getattr(mt5, "TRADE_ACTION_SLTP"),
            symbol=position.symbol,
            volume=float(position.volume),
            orderType=getattr(mt5, "ORDER_TYPE_BUY"),
            price=float(getattr(position, "price_current", 0.0) or 0.0),
            sl=float(getattr(position, "sl", 0.0) or 0.0) or None,
            tp=take_profit,
            deviation=settings.defaultDeviation,
            magicNumber=settings.magicNumber,
            comment="OSCAR modify TP",
            position=position.ticket,
        )

    def build_cancel_order(self, order) -> TradeOrder:

        return TradeOrder(
            action=getattr(mt5, "TRADE_ACTION_REMOVE"),
            symbol=order.symbol,
            volume=float(getattr(order, "volume_current", 0.0) or 0.0),
            orderType=getattr(mt5, "ORDER_TYPE_BUY"),
            price=float(getattr(order, "price_open", 0.0) or 0.0),
            deviation=settings.defaultDeviation,
            magicNumber=settings.magicNumber,
            comment="OSCAR cancel pending order",
            order=order.ticket,
        )