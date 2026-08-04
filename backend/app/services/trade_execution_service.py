from time import perf_counter

import MetaTrader5 as mt5

from app.core.logger import logger
from app.services.trade_errors import BrokerRejected
from app.services.trade_errors import ConnectionError


class TradeExecutionService:

    def send(self, request: dict, operation: str):

        start = perf_counter()

        if not mt5.initialize():
            raise ConnectionError()

        logger.info(
            "orden enviada | operation=%s | symbol=%s | ticket=%s",
            operation,
            request.get("symbol"),
            request.get("position") or request.get("order"),
        )

        response = mt5.order_send(request)

        latency = (perf_counter() - start) * 1000.0

        if response is None:
            logger.warning(
                "orden rechazada | operation=%s | latency_ms=%.2f",
                operation,
                latency,
            )
            raise BrokerRejected("Broker returned no response")

        retcode = getattr(response, "retcode", None)
        success_codes = {
            getattr(mt5, "TRADE_RETCODE_DONE", 10009),
            getattr(mt5, "TRADE_RETCODE_PLACED", 10008),
            getattr(mt5, "TRADE_RETCODE_DONE_PARTIAL", 10010),
        }

        if retcode not in success_codes:
            message = getattr(response, "comment", None) or f"retcode={retcode}"
            logger.warning(
                "orden rechazada | operation=%s | ticket=%s | latency_ms=%.2f | message=%s",
                operation,
                getattr(response, "order", None),
                latency,
                message,
            )
            raise BrokerRejected(message)

        logger.info(
            "orden ejecutada | operation=%s | ticket=%s | latency_ms=%.2f",
            operation,
            getattr(response, "order", None),
            latency,
        )

        return response, latency