from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.services import trade_execution_service as execution_module
from app.services import trade_executor as executor_module
from app.services import order_validator as validator_module
from app.market import service as market_service_module


client = TestClient(app)


class FakeMT5:
    TRADE_ACTION_DEAL = 1
    TRADE_ACTION_SLTP = 2
    TRADE_ACTION_REMOVE = 3
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    POSITION_TYPE_BUY = 0
    POSITION_TYPE_SELL = 1
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 1
    TRADE_RETCODE_DONE = 10009
    TRADE_RETCODE_PLACED = 10008
    TRADE_RETCODE_DONE_PARTIAL = 10010

    def __init__(self):
        self.connected = True
        self.trade_allowed = True
        self.symbol_name = "USDCHF.pro"
        self.symbol_visible = True
        self.tick = SimpleNamespace(bid=0.9000, ask=0.9002, time=1)
        self.order_response = SimpleNamespace(
            retcode=self.TRADE_RETCODE_DONE,
            order=123456,
            deal=654321,
            price=0.9002,
            comment="done",
        )
        self.rejected_response = SimpleNamespace(
            retcode=99999,
            order=None,
            deal=None,
            price=0.0,
            comment="rejected by broker",
        )
        self.positions = {
            777: SimpleNamespace(
                ticket=777,
                symbol=self.symbol_name,
                volume=0.10,
                type=self.POSITION_TYPE_BUY,
                sl=0.8990,
                tp=0.9020,
                price_current=0.9001,
            )
        }
        self.pending_orders = {
            888: SimpleNamespace(
                ticket=888,
                symbol=self.symbol_name,
                volume_current=0.10,
                price_open=0.9000,
            )
        }
        self.sent_requests = []

    def initialize(self):
        return self.connected

    def terminal_info(self):
        return SimpleNamespace(trade_allowed=self.trade_allowed)

    def account_info(self):
        return SimpleNamespace(
            login=123456,
            company="OSCAR Demo",
            server="Demo-Server",
            margin_free=10000.0,
        )

    def symbols_get(self):
        return [SimpleNamespace(name=self.symbol_name)]

    def symbol_info(self, symbol):
        if symbol != self.symbol_name:
            return None

        return SimpleNamespace(
            name=symbol,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
            point=0.0001,
            trade_mode=4,
            trade_stops_level=10,
        )

    def symbol_select(self, symbol, enable):
        return symbol == self.symbol_name and enable

    def symbol_info_tick(self, symbol):
        if symbol != self.symbol_name:
            return None

        return self.tick

    def order_calc_margin(self, order_type, symbol, volume, price):
        return 100.0

    def order_send(self, request):
        self.sent_requests.append(request)
        if request.get("comment") == "reject":
            return self.rejected_response
        return self.order_response

    def positions_get(self, ticket=None):
        if ticket is None:
            return list(self.positions.values())
        position = self.positions.get(ticket)
        return [position] if position else []

    def orders_get(self, ticket=None):
        if ticket is None:
            return list(self.pending_orders.values())
        order = self.pending_orders.get(ticket)
        return [order] if order else []


def patch_mt5(monkeypatch, fake_mt5):
    monkeypatch.setattr(market_service_module, "mt5", fake_mt5)
    monkeypatch.setattr(validator_module, "mt5", fake_mt5)
    monkeypatch.setattr(execution_module, "mt5", fake_mt5)
    monkeypatch.setattr(executor_module, "mt5", fake_mt5)


def test_buy_success(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().executeBuy(
        DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=0.8990, tp=0.9020)
    )

    assert result.success is True
    assert result.ticket == 123456
    assert result.order.symbol == "USDCHF.pro"


def test_sell_success(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().executeSell(
        DecisionContext(symbol="USDCHF.pro", side=TradeSide.SELL, volume=0.10, sl=0.9010, tp=0.8980)
    )

    assert result.success is True
    assert result.ticket == 123456
    assert result.order.orderType == fake_mt5.ORDER_TYPE_SELL


def test_close_position(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().closePosition(777)

    assert result.success is True
    assert result.ticket == 123456
    assert result.volume == 0.10


def test_modify_stop_loss(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().modifyStopLoss(777, 0.8985)

    assert result.success is True
    assert result.sl == 0.8985


def test_modify_take_profit(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().modifyTakeProfit(777, 0.9030)

    assert result.success is True
    assert result.tp == 0.9030


def test_cancel_pending_order(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().cancelPendingOrder(888)

    assert result.success is True
    assert result.ticket == 888


def test_broker_reject(monkeypatch):
    fake_mt5 = FakeMT5()
    fake_mt5.order_response = fake_mt5.rejected_response
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().executeBuy(
        DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=0.8990, tp=0.9020, comment="reject")
    )

    assert result.success is False
    assert result.error == "BrokerRejected"


def test_invalid_order(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().executeBuy(
        DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.0, sl=0.8990, tp=0.9020)
    )

    assert result.success is False
    assert result.error == "InvalidOrder"


def test_connection_lost(monkeypatch):
    fake_mt5 = FakeMT5()
    fake_mt5.connected = False
    patch_mt5(monkeypatch, fake_mt5)

    result = executor_module.TradeExecutor().executeBuy(
        DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=0.8990, tp=0.9020)
    )

    assert result.success is False
    assert result.error == "ConnectionError"


def test_trade_api_buy(monkeypatch):
    fake_mt5 = FakeMT5()
    patch_mt5(monkeypatch, fake_mt5)

    response = client.post(
        "/api/v1/trade/buy",
        json={
            "symbol": "USDCHF.pro",
            "side": "BUY",
            "volume": 0.10,
            "sl": 0.8990,
            "tp": 0.9020,
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True