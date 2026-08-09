from __future__ import annotations

from app.execution.models import ValidationResult
from app.execution.models import ValidationSeverity
from app.execution.models import ValidationStatus


def validateRisk(risk_percent: float, max_risk_percent: float = 2.0) -> ValidationResult:
    if risk_percent <= 0:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="Risk percent must be greater than zero.",
            severity=ValidationSeverity.HIGH,
        )

    if risk_percent <= max_risk_percent:
        return ValidationResult(
            status=ValidationStatus.PASS,
            message="Risk percent is within allowed limits.",
            severity=ValidationSeverity.LOW,
        )

    if risk_percent <= max_risk_percent * 1.25:
        return ValidationResult(
            status=ValidationStatus.WARN,
            message="Risk percent is slightly above policy.",
            severity=ValidationSeverity.MEDIUM,
        )

    return ValidationResult(
        status=ValidationStatus.FAIL,
        message="Risk percent exceeds institutional policy.",
        severity=ValidationSeverity.HIGH,
    )


def validateRR(rr: float, min_rr: float = 2.0) -> ValidationResult:
    if rr <= 0:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="RR is not valid.",
            severity=ValidationSeverity.HIGH,
        )

    if rr >= min_rr:
        return ValidationResult(
            status=ValidationStatus.PASS,
            message="RR meets institutional minimum.",
            severity=ValidationSeverity.LOW,
        )

    if rr >= min_rr * 0.8:
        return ValidationResult(
            status=ValidationStatus.WARN,
            message="RR is below target but close to threshold.",
            severity=ValidationSeverity.MEDIUM,
        )

    return ValidationResult(
        status=ValidationStatus.FAIL,
        message="RR is too low for institutional execution.",
        severity=ValidationSeverity.HIGH,
    )


def validateSpread(spread: float, max_spread: float = 2.5) -> ValidationResult:
    if spread < 0:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="Spread cannot be negative.",
            severity=ValidationSeverity.HIGH,
        )

    if spread <= max_spread:
        return ValidationResult(
            status=ValidationStatus.PASS,
            message="Spread is acceptable.",
            severity=ValidationSeverity.LOW,
        )

    if spread <= max_spread * 1.5:
        return ValidationResult(
            status=ValidationStatus.WARN,
            message="Spread is elevated.",
            severity=ValidationSeverity.MEDIUM,
        )

    return ValidationResult(
        status=ValidationStatus.FAIL,
        message="Spread is too high for safe execution.",
        severity=ValidationSeverity.HIGH,
    )


def validateLot(lot_size: float, min_lot: float = 0.01, max_lot: float = 100.0) -> ValidationResult:
    if lot_size < min_lot:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="Lot size is below symbol minimum.",
            severity=ValidationSeverity.HIGH,
        )

    if lot_size > max_lot:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="Lot size exceeds symbol maximum.",
            severity=ValidationSeverity.HIGH,
        )

    return ValidationResult(
        status=ValidationStatus.PASS,
        message="Lot size is valid.",
        severity=ValidationSeverity.LOW,
    )


def validateStops(
    side: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
) -> ValidationResult:
    normalized_side = side.upper()

    if normalized_side not in {"BUY", "SELL"}:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="Trade side must be BUY or SELL.",
            severity=ValidationSeverity.HIGH,
        )

    if normalized_side == "BUY":
        if stop_loss >= entry_price:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                message="BUY stop loss must be below entry.",
                severity=ValidationSeverity.HIGH,
            )

        if take_profit <= entry_price:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                message="BUY take profit must be above entry.",
                severity=ValidationSeverity.HIGH,
            )

    if normalized_side == "SELL":
        if stop_loss <= entry_price:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                message="SELL stop loss must be above entry.",
                severity=ValidationSeverity.HIGH,
            )

        if take_profit >= entry_price:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                message="SELL take profit must be below entry.",
                severity=ValidationSeverity.HIGH,
            )

    return ValidationResult(
        status=ValidationStatus.PASS,
        message="Stops are coherent with trade side.",
        severity=ValidationSeverity.LOW,
    )


def validateMargin(
    margin_required: float,
    account_balance: float,
    safety_buffer: float = 0.7,
) -> ValidationResult:
    if account_balance <= 0:
        return ValidationResult(
            status=ValidationStatus.FAIL,
            message="Account balance is unavailable.",
            severity=ValidationSeverity.HIGH,
        )

    if margin_required <= 0:
        return ValidationResult(
            status=ValidationStatus.WARN,
            message="Margin estimate unavailable.",
            severity=ValidationSeverity.MEDIUM,
        )

    usage = margin_required / account_balance

    if usage <= safety_buffer:
        return ValidationResult(
            status=ValidationStatus.PASS,
            message="Margin usage is healthy.",
            severity=ValidationSeverity.LOW,
        )

    if usage <= 0.9:
        return ValidationResult(
            status=ValidationStatus.WARN,
            message="Margin usage is high.",
            severity=ValidationSeverity.MEDIUM,
        )

    return ValidationResult(
        status=ValidationStatus.FAIL,
        message="Insufficient free margin for this setup.",
        severity=ValidationSeverity.HIGH,
    )
