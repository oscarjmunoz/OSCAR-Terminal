from time import perf_counter

import MetaTrader5 as mt5

from app.core.logger import logger
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.trade import TradeResult
from app.services.order_builder import OrderBuilder
from app.services.order_validator import OrderValidator
from app.services.trade_errors import TradeError
from app.services.trade_execution_service import TradeExecutionService


class TradeExecutor:

    def __init__(
        self,
        execution_service: TradeExecutionService | None = None,
        builder: OrderBuilder | None = None,
        validator: OrderValidator | None = None,
    ):

        self._execution_service = execution_service or TradeExecutionService()
        self._builder = builder or OrderBuilder()
        self._validator = validator or OrderValidator()

    def executeBuy(self, decision: DecisionContext) -> TradeResult:
        return self._execute_market(decision.model_copy(update={"side": TradeSide.BUY}))

    def executeSell(self, decision: DecisionContext) -> TradeResult:
        return self._execute_market(decision.model_copy(update={"side": TradeSide.SELL}))

    def closePosition(self, ticket: int) -> TradeResult:
        return self._execute_close(ticket)

    def modifyStopLoss(self, ticket: int, stop_loss: float) -> TradeResult:
        return self._execute_modify_sl(ticket, stop_loss)

    def modifyTakeProfit(self, ticket: int, take_profit: float) -> TradeResult:
        return self._execute_modify_tp(ticket, take_profit)

    def cancelPendingOrder(self, ticket: int) -> TradeResult:
        return self._execute_cancel(ticket)

    def _execute_market(self, decision: DecisionContext) -> TradeResult:
        started_at = perf_counter()

        try:
            symbol_info = mt5.symbol_info(decision.symbol)
            if symbol_info is None:
                raise TradeError(f"Symbol not found: {decision.symbol}")

            tick = mt5.symbol_info_tick(decision.symbol)
            if tick is None:
                raise TradeError("No tick available")

            price = float(tick.ask if decision.side == TradeSide.BUY else tick.bid)
            order = self._builder.build_market_order(decision, price)

            self._validator.validate_market_order(
                symbol=order.symbol,
                volume=order.volume,
                side=decision.side.value,
                price=price,
                sl=order.sl,
                tp=order.tp,
                order_type=order.orderType,
            )

            response, latency = self._execution_service.send(
                order.as_mt5_request(),
                f"{decision.side.value.lower()}_market",
            )

            ticket = getattr(response, "order", None) or getattr(response, "deal", None)

            result = TradeResult(
                success=True,
                ticket=ticket,
                order=order,
                price=getattr(response, "price", price),
                volume=order.volume,
                sl=order.sl,
                tp=order.tp,
                brokerMessage=getattr(response, "comment", None),
                executionTime=latency,
            )

            logger.info(
                "trade result | action=%s | ticket=%s | latency_ms=%.2f",
                decision.side.value,
                ticket,
                latency,
            )

            return result

        except TradeError as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("orden rechazada | action=%s | error=%s", decision.side.value, exc)
            return TradeResult(
                success=False,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

        except Exception as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("orden rechazada | action=%s | error=%s", decision.side.value, exc)
            return TradeResult(
                success=False,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

    def _execute_close(self, ticket: int) -> TradeResult:
        started_at = perf_counter()

        try:
            positions = mt5.positions_get(ticket=ticket)
            position = positions[0] if positions else None
            self._validator.validate_position(position)

            tick = mt5.symbol_info_tick(position.symbol)
            if tick is None:
                raise TradeError("No tick available")

            close_price = float(tick.bid if position.type == getattr(mt5, "POSITION_TYPE_BUY", 0) else tick.ask)
            order = self._builder.build_close_order(position, close_price)
            response, latency = self._execution_service.send(
                order.as_mt5_request(),
                "close_position",
            )

            logger.info("cierre ejecutado | ticket=%s | latency_ms=%.2f", ticket, latency)

            return TradeResult(
                success=True,
                ticket=getattr(response, "order", None) or getattr(response, "deal", None) or ticket,
                order=order,
                price=getattr(response, "price", close_price),
                volume=order.volume,
                sl=position.sl,
                tp=position.tp,
                brokerMessage=getattr(response, "comment", None),
                executionTime=latency,
            )

        except TradeError as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("cierre rechazado | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

        except Exception as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("cierre rechazado | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

    def _execute_modify_sl(self, ticket: int, stop_loss: float) -> TradeResult:
        started_at = perf_counter()

        try:
            positions = mt5.positions_get(ticket=ticket)
            position = positions[0] if positions else None
            self._validator.validate_position(position)

            order = self._builder.build_modify_sl_order(position, stop_loss)
            response, latency = self._execution_service.send(
                order.as_mt5_request(),
                "modify_stop_loss",
            )

            logger.info("modificacion SL ejecutada | ticket=%s | latency_ms=%.2f", ticket, latency)

            return TradeResult(
                success=True,
                ticket=ticket,
                order=order,
                price=getattr(position, "price_current", None),
                volume=order.volume,
                sl=stop_loss,
                tp=getattr(position, "tp", None),
                brokerMessage=getattr(response, "comment", None),
                executionTime=latency,
            )

        except TradeError as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("modificacion SL rechazada | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

        except Exception as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("modificacion SL rechazada | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

    def _execute_modify_tp(self, ticket: int, take_profit: float) -> TradeResult:
        started_at = perf_counter()

        try:
            positions = mt5.positions_get(ticket=ticket)
            position = positions[0] if positions else None
            self._validator.validate_position(position)

            order = self._builder.build_modify_tp_order(position, take_profit)
            response, latency = self._execution_service.send(
                order.as_mt5_request(),
                "modify_take_profit",
            )

            logger.info("modificacion TP ejecutada | ticket=%s | latency_ms=%.2f", ticket, latency)

            return TradeResult(
                success=True,
                ticket=ticket,
                order=order,
                price=getattr(position, "price_current", None),
                volume=order.volume,
                sl=getattr(position, "sl", None),
                tp=take_profit,
                brokerMessage=getattr(response, "comment", None),
                executionTime=latency,
            )

        except TradeError as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("modificacion TP rechazada | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

        except Exception as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("modificacion TP rechazada | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

    def _execute_cancel(self, ticket: int) -> TradeResult:
        started_at = perf_counter()

        try:
            orders = mt5.orders_get(ticket=ticket)
            order_item = orders[0] if orders else None
            self._validator.validate_pending_order(order_item)

            order = self._builder.build_cancel_order(order_item)
            response, latency = self._execution_service.send(
                order.as_mt5_request(),
                "cancel_pending_order",
            )

            logger.info("orden pendiente cancelada | ticket=%s | latency_ms=%.2f", ticket, latency)

            return TradeResult(
                success=True,
                ticket=ticket,
                order=order,
                price=getattr(order_item, "price_open", None),
                volume=getattr(order_item, "volume_current", None),
                brokerMessage=getattr(response, "comment", None),
                executionTime=latency,
            )

        except TradeError as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("cancelacion rechazada | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )

        except Exception as exc:
            latency = (perf_counter() - started_at) * 1000.0
            logger.warning("cancelacion rechazada | ticket=%s | error=%s", ticket, exc)
            return TradeResult(
                success=False,
                ticket=ticket,
                brokerMessage=str(exc),
                executionTime=latency,
                error=exc.__class__.__name__,
            )