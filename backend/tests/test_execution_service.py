from types import SimpleNamespace

from app.execution.schemas import ExecutionRequest
from app.execution.schemas import ExecutionStatus
from app.execution.schemas import TradeSide
from app.execution.service import ExecutionService
from app.execution import service as execution_service_module


class FakeMT5:

    def __init__(self):
        self._account = SimpleNamespace(balance=10000.0, equity=10020.0, leverage=100)
        self._symbol_info = SimpleNamespace(trade_tick_value=10.0, trade_contract_size=100000.0)

    def account_info(self):
        return self._account

    def symbol_info(self, _symbol: str):
        return self._symbol_info


def test_prepare_execution_ready(monkeypatch):
    fake_mt5 = FakeMT5()

    monkeypatch.setattr(execution_service_module, "mt5", fake_mt5)
    monkeypatch.setattr(execution_service_module.MarketService, "initialize", lambda: True)
    monkeypatch.setattr(
        execution_service_module.MarketService,
        "latest_tick",
        lambda _symbol: SimpleNamespace(spread=1.2),
    )

    request = ExecutionRequest(
        symbol="EURUSD",
        side=TradeSide.BUY,
        entry_price=1.17520,
        stop_loss=1.17440,
        take_profit=1.17760,
        risk_percent=0.5,
    )

    result = ExecutionService.prepare(request)

    assert result.execution_status == ExecutionStatus.READY
    assert result.rr == 3.0
    assert result.risk_money == 50.0
    assert result.spread == 1.2


def test_prepare_execution_blocked_when_rr_and_stops_fail(monkeypatch):
    fake_mt5 = FakeMT5()

    monkeypatch.setattr(execution_service_module, "mt5", fake_mt5)
    monkeypatch.setattr(execution_service_module.MarketService, "initialize", lambda: True)
    monkeypatch.setattr(
        execution_service_module.MarketService,
        "latest_tick",
        lambda _symbol: SimpleNamespace(spread=1.0),
    )

    request = ExecutionRequest(
        symbol="EURUSD",
        side=TradeSide.BUY,
        entry_price=1.17520,
        stop_loss=1.17540,
        take_profit=1.17560,
        risk_percent=0.5,
    )

    result = ExecutionService.prepare(request)

    assert result.execution_status == ExecutionStatus.BLOCKED


def test_prepare_execution_uses_provided_account_balance(monkeypatch):
    fake_mt5 = FakeMT5()

    monkeypatch.setattr(execution_service_module, "mt5", fake_mt5)
    monkeypatch.setattr(execution_service_module.MarketService, "initialize", lambda: True)
    monkeypatch.setattr(
        execution_service_module.MarketService,
        "latest_tick",
        lambda _symbol: SimpleNamespace(spread=2.0),
    )

    request = ExecutionRequest(
        symbol="EURUSD",
        side=TradeSide.SELL,
        entry_price=1.17520,
        stop_loss=1.17600,
        take_profit=1.17280,
        risk_percent=1.0,
        account_balance=5000.0,
    )

    result = ExecutionService.prepare(request)

    assert result.risk_money == 50.0
    assert result.execution_status in {ExecutionStatus.READY, ExecutionStatus.REVIEW}
