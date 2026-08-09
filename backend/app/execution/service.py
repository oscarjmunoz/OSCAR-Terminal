from __future__ import annotations

from types import SimpleNamespace

import MetaTrader5 as mt5

from app.execution import calculator
from app.execution import validator
from app.execution.models import ValidationResult
from app.execution.models import ValidationSeverity
from app.execution.models import ValidationStatus
from app.execution.schemas import ExecutionRequest
from app.execution.schemas import ExecutionResult
from app.execution.schemas import ExecutionStatus
from app.execution.schemas import ValidationResultSchema
from app.market.service import MarketService


class ExecutionService:

    @staticmethod
    def prepare(request: ExecutionRequest) -> ExecutionResult:
        account_balance = request.account_balance or ExecutionService._resolve_account_balance()
        spread = ExecutionService._resolve_spread(request.symbol, request.spread)
        symbol_info = None
        if request.pip_value is None or request.tick_value is None or request.contract_size is None:
            symbol_info = ExecutionService._resolve_symbol_info(request.symbol)

        pip_value = request.pip_value or float(getattr(symbol_info, "trade_tick_value", 10.0) or 10.0)
        tick_value = request.tick_value or float(getattr(symbol_info, "trade_tick_value", pip_value) or pip_value)
        leverage = request.leverage or ExecutionService._resolve_leverage()
        contract_size = request.contract_size or float(getattr(symbol_info, "trade_contract_size", 100000.0) or 100000.0)

        risk_money = calculator.calculateRiskMoney(account_balance, request.risk_percent)
        risk_pips = calculator.calculatePipDistance(request.entry_price, request.stop_loss, request.symbol)
        reward_pips = calculator.calculateRewardDistance(request.entry_price, request.take_profit, request.symbol)
        rr = calculator.calculateRR(reward_pips, risk_pips)
        lot_size = calculator.calculateLotSize(risk_money, risk_pips, pip_value)
        margin_required = calculator.calculateMarginEstimate(
            request.entry_price,
            lot_size,
            leverage,
            contract_size,
        )
        reward_money = calculator.calculateRewardMoney(reward_pips, pip_value, lot_size)

        validations = [
            validator.validateRisk(request.risk_percent, request.max_risk_percent),
            validator.validateRR(rr, request.min_rr),
            validator.validateSpread(spread, request.max_spread),
            validator.validateLot(lot_size, request.min_lot, request.max_lot),
            validator.validateStops(request.side.value, request.entry_price, request.stop_loss, request.take_profit),
            validator.validateMargin(margin_required, account_balance, request.margin_buffer),
        ]

        institutional_score = ExecutionService._institutional_score(validations)
        execution_status = ExecutionService._execution_status(validations)

        return ExecutionResult(
            symbol=request.symbol,
            side=request.side,
            entry=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            lot_size=lot_size,
            risk_percent=round(request.risk_percent, 2),
            risk_money=risk_money,
            reward_money=reward_money,
            risk_pips=risk_pips,
            reward_pips=reward_pips,
            rr=rr,
            pip_value=round(pip_value, 4),
            tick_value=round(tick_value, 4),
            margin_required=margin_required,
            spread=round(spread, 2),
            validation_results=[
                ValidationResultSchema(
                    status=result.status.value,
                    message=result.message,
                    severity=result.severity.value,
                )
                for result in validations
            ],
            institutional_score=institutional_score,
            execution_status=execution_status,
        )

    @staticmethod
    def _resolve_account_balance() -> float:
        if not MarketService.initialize():
            return 0.0

        info = mt5.account_info()

        if info is None:
            return 0.0

        balance = float(getattr(info, "balance", 0.0) or 0.0)

        if balance > 0:
            return balance

        equity = float(getattr(info, "equity", 0.0) or 0.0)
        return max(equity, 0.0)

    @staticmethod
    def _resolve_leverage() -> float:
        if not MarketService.initialize():
            return 100.0

        info = mt5.account_info()

        if info is None:
            return 100.0

        leverage = float(getattr(info, "leverage", 100.0) or 100.0)

        if leverage <= 0:
            return 100.0

        return leverage

    @staticmethod
    def _resolve_spread(symbol: str, provided_spread: float | None) -> float:
        if provided_spread is not None:
            return float(provided_spread)

        tick = MarketService.latest_tick(symbol)

        if tick is None:
            return 0.0

        return float(getattr(tick, "spread", 0.0) or 0.0)

    @staticmethod
    def _resolve_symbol_info(symbol: str):
        if not MarketService.initialize():
            return SimpleNamespace()

        info = mt5.symbol_info(symbol)

        if info is None:
            return SimpleNamespace()

        return info

    @staticmethod
    def _institutional_score(results: list[ValidationResult]) -> float:
        score = 100.0

        for result in results:
            if result.status == ValidationStatus.PASS:
                continue

            if result.status == ValidationStatus.WARN:
                if result.severity == ValidationSeverity.MEDIUM:
                    score -= 8.0
                else:
                    score -= 5.0

            if result.status == ValidationStatus.FAIL:
                if result.severity == ValidationSeverity.HIGH:
                    score -= 25.0
                elif result.severity == ValidationSeverity.MEDIUM:
                    score -= 18.0
                else:
                    score -= 12.0

        return round(max(score, 0.0), 2)

    @staticmethod
    def _execution_status(results: list[ValidationResult]) -> ExecutionStatus:
        has_high_fail = any(
            result.status == ValidationStatus.FAIL and result.severity == ValidationSeverity.HIGH
            for result in results
        )

        if has_high_fail:
            return ExecutionStatus.BLOCKED

        has_fail = any(result.status == ValidationStatus.FAIL for result in results)
        has_warn = any(result.status == ValidationStatus.WARN for result in results)

        if has_fail or has_warn:
            return ExecutionStatus.REVIEW

        return ExecutionStatus.READY
