from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import MetaTrader5 as mt5

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.settings import settings  # noqa: E402
from app.core.logger import logger  # noqa: E402
from app.schemas.decision import DecisionContext  # noqa: E402
from app.schemas.decision import TradeSide  # noqa: E402
from app.schemas.health import HealthStatus  # noqa: E402
from app.services.health_engine import HealthEngine  # noqa: E402
from app.services.trade_execution_service import TradeExecutionService  # noqa: E402
from app.services.trade_executor import TradeExecutor  # noqa: E402


PASS = "PASS"
FAIL = "FAIL"
SKIPPED = "SKIPPED"
NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class StepResult:
    name: str
    status: str
    details: str = ""
    latency_ms: float | None = None
    ticket: int | None = None
    price: float | None = None


class ValidationHalt(Exception):
    pass


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_json(value: Any) -> str:
    return json.dumps(value, default=str, ensure_ascii=True, indent=2)


def _status_icon(status: str) -> str:
    if status == PASS:
        return "[PASS]"
    if status == FAIL:
        return "[FAIL]"
    if status == SKIPPED:
        return "[SKIPPED]"
    return "[N/A]"


def _resolve_symbol(configured_symbol: str) -> str | None:
    symbols = mt5.symbols_get()
    if symbols is None:
        return None

    target = configured_symbol.upper()

    for item in symbols:
        if item.name.upper() == target:
            return item.name

    for item in symbols:
        if item.name.upper().startswith(target):
            return item.name

    return None


def compute_protective_levels(symbol_info: Any, side: TradeSide, price: float) -> tuple[float, float]:
    point = _safe_float(getattr(symbol_info, "point", 0.0)) or 0.0001
    stops_level = int(getattr(symbol_info, "trade_stops_level", 0) or 0)
    buffer_points = max(stops_level + 30, 100)
    distance = point * buffer_points

    if side == TradeSide.BUY:
        sl = price - distance
        tp = price + distance
    else:
        sl = price + distance
        tp = price - distance

    digits = int(getattr(symbol_info, "digits", 5) or 5)
    return round(sl, digits), round(tp, digits)


def pending_supported() -> bool:
    required = (
        "TRADE_ACTION_PENDING",
        "ORDER_TYPE_BUY_LIMIT",
        "ORDER_TIME_GTC",
    )
    return all(hasattr(mt5, attr) for attr in required)


def build_report_markdown(
    generated_at: datetime,
    broker: str | None,
    account: int | None,
    server: str | None,
    symbol: str,
    results: dict[str, StepResult],
    average_latency_ms: float | None,
    total_seconds: float,
    final_result: str,
) -> str:
    lines = [
        "# E2E Trade Validation Report",
        "",
        f"- Fecha: {generated_at.isoformat()}",
        f"- Broker: {broker or 'N/A'}",
        f"- Cuenta: {account if account is not None else 'N/A'}",
        f"- Servidor: {server or 'N/A'}",
        f"- Simbolo: {symbol}",
        "",
        "## Resultados",
    ]

    ordered_keys = [
        "HEALTH",
        "BUY",
        "SELL",
        "MODIFY",
        "CLOSE",
        "PENDING",
        "ERRORS",
    ]

    for key in ordered_keys:
        item = results.get(key, StepResult(name=key, status=NOT_EXECUTED, details="No ejecutado"))
        detail = item.details or "-"
        ticket = f" | ticket={item.ticket}" if item.ticket is not None else ""
        price = f" | price={item.price}" if item.price is not None else ""
        latency = f" | latency_ms={item.latency_ms:.2f}" if item.latency_ms is not None else ""
        lines.append(f"- {key}: {_status_icon(item.status)} {detail}{ticket}{price}{latency}")

    lines.extend(
        [
            "",
            f"- Latencia promedio: {average_latency_ms:.2f} ms" if average_latency_ms is not None else "- Latencia promedio: N/A",
            f"- Tiempo total: {total_seconds:.2f} s",
            f"- Resultado final: {final_result}",
            "",
            "## Detalle Tecnico",
            "",
            "```json",
            _as_json({
                key: {
                    "status": value.status,
                    "details": value.details,
                    "latency_ms": value.latency_ms,
                    "ticket": value.ticket,
                    "price": value.price,
                }
                for key, value in results.items()
            }),
            "```",
        ]
    )

    return "\n".join(lines) + "\n"


class E2ETradeValidator:
    def __init__(self, symbol: str, volume: float = 0.01) -> None:
        self.configured_symbol = symbol
        self.volume = volume
        self.executor = TradeExecutor()
        self.execution_service = TradeExecutionService()
        self.results: dict[str, StepResult] = {}
        self.latencies: list[float] = []
        self.broker: str | None = None
        self.account: int | None = None
        self.server: str | None = None
        self.symbol: str = symbol

    def _record(
        self,
        key: str,
        status: str,
        details: str,
        latency_ms: float | None = None,
        ticket: int | None = None,
        price: float | None = None,
    ) -> None:
        self.results[key] = StepResult(
            name=key,
            status=status,
            details=details,
            latency_ms=latency_ms,
            ticket=ticket,
            price=price,
        )
        logger.info("%s %s | %s", _status_icon(status), key, details)
        if latency_ms is not None:
            self.latencies.append(latency_ms)

    def _halt(self, key: str, message: str) -> None:
        self._record(key, FAIL, message)
        raise ValidationHalt(message)

    def _verify_mt5_connection(self) -> None:
        logger.info("step 1/10 | verifying MT5 connection")
        connected = mt5.initialize()
        if not connected:
            self._halt("MT5_CONNECTION", "MT5 initialize() returned False")

        terminal = mt5.terminal_info()
        account = mt5.account_info()
        self.broker = getattr(account, "company", None)
        self.account = getattr(account, "login", None)
        self.server = getattr(account, "server", None)

        details = {
            "connected": connected,
            "trade_allowed": getattr(terminal, "trade_allowed", None),
            "broker": self.broker,
            "account": self.account,
            "server": self.server,
        }
        self._record("MT5_CONNECTION", PASS, _as_json(details))

    def _verify_health(self) -> None:
        logger.info("step 2/10 | verifying HealthEngine")
        engine = HealthEngine(symbol=self.configured_symbol)
        snapshot = engine.collect_snapshot()

        if snapshot.overallStatus != HealthStatus.HEALTHY:
            self._halt(
                "HEALTH",
                (
                    f"HealthEngine status={snapshot.overallStatus.value} "
                    f"(mt5={snapshot.mt5Connection.value}, market={snapshot.marketStatus.value}, "
                    f"pipeline={snapshot.pipelineStatus.value}, eventBus={snapshot.eventBusStatus.value})"
                ),
            )

        self._record("HEALTH", PASS, f"overallStatus={snapshot.overallStatus.value}")

    def _verify_symbol(self) -> Any:
        logger.info("step 3/10 | verifying symbol")
        resolved = _resolve_symbol(self.configured_symbol)
        if resolved is None:
            self._halt("SYMBOL", f"Configured symbol not found: {self.configured_symbol}")

        self.symbol = resolved
        symbol_info = mt5.symbol_info(resolved)
        if symbol_info is None:
            self._halt("SYMBOL", f"symbol_info unavailable for {resolved}")

        selected = mt5.symbol_select(resolved, True)
        tick = mt5.symbol_info_tick(resolved)
        terminal = mt5.terminal_info()

        is_visible = bool(getattr(symbol_info, "visible", False) or selected)
        trade_allowed = bool(getattr(terminal, "trade_allowed", False))
        trade_mode = int(getattr(symbol_info, "trade_mode", -1))
        symbol_trade_enabled = trade_mode != getattr(mt5, "SYMBOL_TRADE_MODE_DISABLED", 0)
        market_open = tick is not None

        details = {
            "symbol": resolved,
            "market_open": market_open,
            "visible": is_visible,
            "trade_allowed": trade_allowed,
            "symbol_trade_enabled": symbol_trade_enabled,
            "trade_mode": trade_mode,
        }

        if not market_open or not is_visible or not trade_allowed or not symbol_trade_enabled:
            self._halt("SYMBOL", _as_json(details))

        self._record("SYMBOL", PASS, _as_json(details))
        return symbol_info

    def _run_market_cycle(self, side: TradeSide, symbol_info: Any) -> tuple[StepResult, StepResult, StepResult]:
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            msg = f"No tick available for {self.symbol}"
            failed = StepResult(name=side.value, status=FAIL, details=msg)
            return failed, StepResult("MODIFY", SKIPPED, msg), StepResult("CLOSE", SKIPPED, msg)

        price = float(tick.ask if side == TradeSide.BUY else tick.bid)
        sl, tp = compute_protective_levels(symbol_info, side, price)

        decision = DecisionContext(
            symbol=self.symbol,
            side=side,
            volume=self.volume,
            sl=sl,
            tp=tp,
            comment=f"e2e_{side.value.lower()}_{int(time.time())}",
        )

        open_result = self.executor.executeBuy(decision) if side == TradeSide.BUY else self.executor.executeSell(decision)

        if not open_result.success or open_result.ticket is None:
            detail = f"open failed error={open_result.error} message={open_result.brokerMessage}"
            open_step = StepResult(side.value, FAIL, detail, open_result.executionTime, open_result.ticket, open_result.price)
            return open_step, StepResult("MODIFY", SKIPPED, "Open failed"), StepResult("CLOSE", SKIPPED, "Open failed")

        open_step = StepResult(
            side.value,
            PASS,
            "Open operation succeeded",
            open_result.executionTime,
            open_result.ticket,
            open_result.price,
        )

        updated_tick = mt5.symbol_info_tick(self.symbol)
        if updated_tick is None:
            modify_step = StepResult("MODIFY", FAIL, "No tick available before modify")
            close_step = StepResult("CLOSE", SKIPPED, "Modify failed")
            return open_step, modify_step, close_step

        modify_price = float(updated_tick.ask if side == TradeSide.BUY else updated_tick.bid)
        new_sl, new_tp = compute_protective_levels(symbol_info, side, modify_price)

        modify_sl = self.executor.modifyStopLoss(open_result.ticket, new_sl)
        modify_tp = self.executor.modifyTakeProfit(open_result.ticket, new_tp)

        if modify_sl.success and modify_tp.success:
            modify_latency = None
            if modify_sl.executionTime is not None and modify_tp.executionTime is not None:
                modify_latency = (modify_sl.executionTime + modify_tp.executionTime) / 2.0
            modify_step = StepResult(
                "MODIFY",
                PASS,
                "SL/TP modified successfully",
                modify_latency,
                open_result.ticket,
                modify_price,
            )
        else:
            modify_step = StepResult(
                "MODIFY",
                FAIL,
                (
                    f"modify_sl(success={modify_sl.success}, error={modify_sl.error}, msg={modify_sl.brokerMessage}); "
                    f"modify_tp(success={modify_tp.success}, error={modify_tp.error}, msg={modify_tp.brokerMessage})"
                ),
                None,
                open_result.ticket,
                modify_price,
            )

        close_result = self.executor.closePosition(open_result.ticket)
        if close_result.success:
            close_step = StepResult(
                "CLOSE",
                PASS,
                "Position closed successfully",
                close_result.executionTime,
                close_result.ticket,
                close_result.price,
            )
        else:
            close_step = StepResult(
                "CLOSE",
                FAIL,
                f"close failed error={close_result.error} message={close_result.brokerMessage}",
                close_result.executionTime,
                close_result.ticket,
                close_result.price,
            )

        return open_step, modify_step, close_step

    def _run_pending_test(self, symbol_info: Any) -> StepResult:
        logger.info("step 8/10 | pending order test")

        if not pending_supported():
            return StepResult("PENDING", SKIPPED, "Pending constants not available in MT5 package")

        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return StepResult("PENDING", SKIPPED, "No tick available for pending test")

        point = _safe_float(getattr(symbol_info, "point", 0.0)) or 0.0001
        stops_level = int(getattr(symbol_info, "trade_stops_level", 0) or 0)
        buffer_points = max(stops_level + 40, 120)
        distance = point * buffer_points

        entry_price = round(float(tick.bid - distance), int(getattr(symbol_info, "digits", 5) or 5))
        sl = round(entry_price - distance, int(getattr(symbol_info, "digits", 5) or 5))
        tp = round(entry_price + distance, int(getattr(symbol_info, "digits", 5) or 5))

        request: dict[str, Any] = {
            "action": getattr(mt5, "TRADE_ACTION_PENDING"),
            "symbol": self.symbol,
            "volume": self.volume,
            "type": getattr(mt5, "ORDER_TYPE_BUY_LIMIT"),
            "price": entry_price,
            "sl": sl,
            "tp": tp,
            "deviation": settings.defaultDeviation,
            "magic": settings.magicNumber,
            "comment": f"e2e_pending_{int(time.time())}",
            "type_time": getattr(mt5, "ORDER_TIME_GTC"),
        }

        if hasattr(mt5, "ORDER_FILLING_RETURN"):
            request["type_filling"] = getattr(mt5, "ORDER_FILLING_RETURN")
        elif hasattr(mt5, "ORDER_FILLING_IOC"):
            request["type_filling"] = getattr(mt5, "ORDER_FILLING_IOC")

        try:
            response, latency = self.execution_service.send(request, "pending_create")
        except Exception as exc:
            message = str(exc)
            lowered = message.lower()
            if "not supported" in lowered or "unsupported" in lowered:
                return StepResult("PENDING", SKIPPED, f"Broker does not support pending orders: {message}")
            return StepResult("PENDING", FAIL, f"Pending creation failed: {message}")

        ticket = getattr(response, "order", None) or getattr(response, "deal", None)
        if ticket is None:
            return StepResult("PENDING", FAIL, "Pending order created without ticket")

        cancel_result = self.executor.cancelPendingOrder(int(ticket))
        if not cancel_result.success:
            return StepResult(
                "PENDING",
                FAIL,
                f"Pending cancel failed error={cancel_result.error} message={cancel_result.brokerMessage}",
                cancel_result.executionTime,
                int(ticket),
                entry_price,
            )

        cancel_latency = cancel_result.executionTime
        total_latency = latency + (cancel_latency or 0.0)

        return StepResult(
            "PENDING",
            PASS,
            "Pending order created and cancelled",
            total_latency,
            int(ticket),
            entry_price,
        )

    def _run_error_tests(self, symbol_info: Any) -> StepResult:
        logger.info("step 9/10 | error handling tests")
        failures: list[str] = []
        checks: list[str] = []

        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return StepResult("ERRORS", SKIPPED, "No tick available for error tests")

        buy_price = float(tick.ask)
        valid_sl, valid_tp = compute_protective_levels(symbol_info, TradeSide.BUY, buy_price)

        invalid_volume = self.executor.executeBuy(
            DecisionContext(
                symbol=self.symbol,
                side=TradeSide.BUY,
                volume=0.0,
                sl=valid_sl,
                tp=valid_tp,
                comment="e2e_invalid_volume",
            )
        )
        checks.append(f"invalid_volume={invalid_volume.error}")
        if invalid_volume.success or invalid_volume.error != "InvalidOrder":
            failures.append("invalid_volume")

        invalid_sl = self.executor.executeBuy(
            DecisionContext(
                symbol=self.symbol,
                side=TradeSide.BUY,
                volume=self.volume,
                sl=round(buy_price + abs(buy_price * 0.001), int(getattr(symbol_info, "digits", 5) or 5)),
                tp=valid_tp,
                comment="e2e_invalid_sl",
            )
        )
        checks.append(f"invalid_sl={invalid_sl.error}")
        if invalid_sl.success or invalid_sl.error != "InvalidOrder":
            failures.append("invalid_sl")

        checks.append("market_closed=SKIPPED")

        if failures:
            return StepResult("ERRORS", FAIL, f"failed={','.join(failures)} | checks={'; '.join(checks)}")

        return StepResult("ERRORS", PASS, f"checks={'; '.join(checks)}")

    def run(self) -> tuple[str, Path]:
        started = time.perf_counter()
        generated_at = datetime.now(timezone.utc)

        self.results = {
            "HEALTH": StepResult("HEALTH", NOT_EXECUTED, "No ejecutado"),
            "BUY": StepResult("BUY", NOT_EXECUTED, "No ejecutado"),
            "SELL": StepResult("SELL", NOT_EXECUTED, "No ejecutado"),
            "MODIFY": StepResult("MODIFY", NOT_EXECUTED, "No ejecutado"),
            "CLOSE": StepResult("CLOSE", NOT_EXECUTED, "No ejecutado"),
            "PENDING": StepResult("PENDING", NOT_EXECUTED, "No ejecutado"),
            "ERRORS": StepResult("ERRORS", NOT_EXECUTED, "No ejecutado"),
        }

        try:
            self._verify_mt5_connection()
            self._verify_health()
            symbol_info = self._verify_symbol()

            logger.info("step 4-7/10 | BUY/SELL lifecycle tests")

            buy_open, buy_modify, buy_close = self._run_market_cycle(TradeSide.BUY, symbol_info)
            self._record("BUY", buy_open.status, buy_open.details, buy_open.latency_ms, buy_open.ticket, buy_open.price)

            sell_open, sell_modify, sell_close = self._run_market_cycle(TradeSide.SELL, symbol_info)
            self._record("SELL", sell_open.status, sell_open.details, sell_open.latency_ms, sell_open.ticket, sell_open.price)

            modify_status = PASS if buy_modify.status == PASS and sell_modify.status == PASS else FAIL
            modify_details = (
                f"buy={buy_modify.status} ({buy_modify.details}) | "
                f"sell={sell_modify.status} ({sell_modify.details})"
            )
            modify_latency = None
            if buy_modify.latency_ms is not None and sell_modify.latency_ms is not None:
                modify_latency = (buy_modify.latency_ms + sell_modify.latency_ms) / 2.0
            self._record("MODIFY", modify_status, modify_details, modify_latency)

            close_status = PASS if buy_close.status == PASS and sell_close.status == PASS else FAIL
            close_details = (
                f"buy={buy_close.status} ({buy_close.details}) | "
                f"sell={sell_close.status} ({sell_close.details})"
            )
            close_latency = None
            if buy_close.latency_ms is not None and sell_close.latency_ms is not None:
                close_latency = (buy_close.latency_ms + sell_close.latency_ms) / 2.0
            self._record("CLOSE", close_status, close_details, close_latency)

            pending = self._run_pending_test(symbol_info)
            self._record("PENDING", pending.status, pending.details, pending.latency_ms, pending.ticket, pending.price)

            errors = self._run_error_tests(symbol_info)
            self._record("ERRORS", errors.status, errors.details, errors.latency_ms, errors.ticket, errors.price)

        except ValidationHalt as exc:
            logger.warning("Validation halted: %s", exc)

        except Exception as exc:
            logger.exception("Unexpected validation failure: %s", exc)
            self._record("ERRORS", FAIL, f"Unhandled exception: {exc}")

        finally:
            try:
                mt5.shutdown()
            except Exception:
                logger.warning("MT5 shutdown failed", exc_info=True)

        required = ["BUY", "SELL", "MODIFY", "CLOSE", "HEALTH"]
        required_ok = all(self.results.get(key, StepResult(key, FAIL)).status == PASS for key in required)

        report_exists = True
        final_result = PASS if required_ok and report_exists else FAIL

        total_seconds = time.perf_counter() - started
        average_latency = sum(self.latencies) / len(self.latencies) if self.latencies else None

        report_content = build_report_markdown(
            generated_at=generated_at,
            broker=self.broker,
            account=self.account,
            server=self.server,
            symbol=self.symbol,
            results=self.results,
            average_latency_ms=average_latency,
            total_seconds=total_seconds,
            final_result=final_result,
        )

        reports_dir = PROJECT_ROOT / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / "e2e_trade_report.md"
        report_path.write_text(report_content, encoding="utf-8")

        logger.info("Report generated at %s", report_path)

        return final_result, report_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="E2E trade validation for OSCAR Trade IA")
    parser.add_argument(
        "--symbol",
        default=os.getenv("E2E_SYMBOL", "USDCHF"),
        help="Configured symbol to validate (default: E2E_SYMBOL or USDCHF)",
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=0.01,
        help="Trade volume for BUY/SELL test orders (default: 0.01)",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    validator = E2ETradeValidator(symbol=args.symbol, volume=args.volume)
    final_result, report_path = validator.run()
    logger.info("Validation result: %s", final_result)
    logger.info("Report path: %s", report_path)
    return 0 if final_result == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
