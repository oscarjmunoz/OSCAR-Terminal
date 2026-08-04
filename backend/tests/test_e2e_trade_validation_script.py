from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.e2e_trade_validation import FAIL
from scripts.e2e_trade_validation import PASS
from scripts.e2e_trade_validation import StepResult
from scripts.e2e_trade_validation import TradeSide
from scripts.e2e_trade_validation import build_report_markdown
from scripts.e2e_trade_validation import compute_protective_levels
from scripts.e2e_trade_validation import pending_supported
from scripts.e2e_trade_validation import mt5


def test_compute_protective_levels_buy_sell():
    symbol_info = SimpleNamespace(point=0.0001, trade_stops_level=10, digits=5)

    buy_sl, buy_tp = compute_protective_levels(symbol_info, TradeSide.BUY, 1.10000)
    sell_sl, sell_tp = compute_protective_levels(symbol_info, TradeSide.SELL, 1.10000)

    assert buy_sl < 1.10000 < buy_tp
    assert sell_tp < 1.10000 < sell_sl


def test_pending_supported_flag(monkeypatch):
    monkeypatch.setattr(mt5, "TRADE_ACTION_PENDING", 5, raising=False)
    monkeypatch.setattr(mt5, "ORDER_TYPE_BUY_LIMIT", 2, raising=False)
    monkeypatch.setattr(mt5, "ORDER_TIME_GTC", 0, raising=False)

    assert pending_supported() is True


def test_build_report_markdown_contains_required_sections():
    results = {
        "HEALTH": StepResult("HEALTH", PASS, "healthy"),
        "BUY": StepResult("BUY", PASS, "ok", latency_ms=12.5, ticket=1001, price=1.12345),
        "SELL": StepResult("SELL", PASS, "ok", latency_ms=11.0, ticket=1002, price=1.12300),
        "MODIFY": StepResult("MODIFY", PASS, "ok"),
        "CLOSE": StepResult("CLOSE", PASS, "ok"),
        "PENDING": StepResult("PENDING", FAIL, "broker unsupported"),
        "ERRORS": StepResult("ERRORS", PASS, "handled"),
    }

    report = build_report_markdown(
        generated_at=datetime(2026, 8, 3, 0, 0, 0, tzinfo=timezone.utc),
        broker="OSCAR Demo",
        account=123456,
        server="Demo-Server",
        symbol="USDCHF.pro",
        results=results,
        average_latency_ms=11.75,
        total_seconds=4.2,
        final_result=PASS,
    )

    assert "# E2E Trade Validation Report" in report
    assert "- Broker: OSCAR Demo" in report
    assert "- Cuenta: 123456" in report
    assert "- Servidor: Demo-Server" in report
    assert "- Simbolo: USDCHF.pro" in report
    assert "- BUY: [PASS]" in report
    assert "- SELL: [PASS]" in report
    assert "- MODIFY: [PASS]" in report
    assert "- CLOSE: [PASS]" in report
    assert "- PENDING: [FAIL]" in report
    assert "- ERRORS: [PASS]" in report
    assert "- Resultado final: PASS" in report
