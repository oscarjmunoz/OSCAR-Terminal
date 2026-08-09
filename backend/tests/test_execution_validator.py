from app.execution.models import ValidationSeverity
from app.execution.models import ValidationStatus
from app.execution import validator


def test_validate_risk_pass_and_fail():
    valid = validator.validateRisk(0.5, max_risk_percent=1.0)
    invalid = validator.validateRisk(3.0, max_risk_percent=1.0)

    assert valid.status == ValidationStatus.PASS
    assert valid.severity == ValidationSeverity.LOW

    assert invalid.status == ValidationStatus.FAIL
    assert invalid.severity == ValidationSeverity.HIGH


def test_validate_rr_warn():
    result = validator.validateRR(1.7, min_rr=2.0)
    assert result.status == ValidationStatus.WARN
    assert result.severity == ValidationSeverity.MEDIUM


def test_validate_spread_and_lot():
    spread = validator.validateSpread(1.8, max_spread=2.5)
    lot = validator.validateLot(0.25, min_lot=0.01, max_lot=2.0)

    assert spread.status == ValidationStatus.PASS
    assert lot.status == ValidationStatus.PASS


def test_validate_stops_for_buy_and_sell():
    buy_ok = validator.validateStops("BUY", 1.17520, 1.17440, 1.17760)
    sell_ok = validator.validateStops("SELL", 1.17520, 1.17600, 1.17300)
    buy_fail = validator.validateStops("BUY", 1.17520, 1.17600, 1.17760)

    assert buy_ok.status == ValidationStatus.PASS
    assert sell_ok.status == ValidationStatus.PASS
    assert buy_fail.status == ValidationStatus.FAIL


def test_validate_margin_levels():
    pass_margin = validator.validateMargin(500.0, 5000.0, safety_buffer=0.7)
    warn_margin = validator.validateMargin(4000.0, 5000.0, safety_buffer=0.7)
    fail_margin = validator.validateMargin(4800.0, 5000.0, safety_buffer=0.7)

    assert pass_margin.status == ValidationStatus.PASS
    assert warn_margin.status == ValidationStatus.WARN
    assert fail_margin.status == ValidationStatus.FAIL
