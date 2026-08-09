from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.decision_center import MultiTimeframeAlignment
from app.schemas.decision_center import MultiTimeframeBiasState
from app.services import decision_center as decision_center_module
from app.services import multi_timeframe_bias as multi_timeframe_module
from app.services.decision_center import DecisionCenter


class _FakeCandle(SimpleNamespace):
    pass


def _build_candle(close: float):
    return _FakeCandle(
        time=datetime(2026, 8, 9, 10, 0, 0),
        open=close,
        high=close + 0.01,
        low=close - 0.01,
        close=close,
        tick_volume=100,
    )


def _build_structure(trend: str):
    return SimpleNamespace(trend=trend, bos=True, choch=False, mss=True, last_high=1.01, last_low=0.99)


def _patch_timeframe_services(monkeypatch, *, h4_trend="BULLISH", h1_trend="BULLISH", m5_trend="BULLISH"):
    def fake_candles(symbol, timeframe, count=300):
        return [_build_candle(1.0)]

    def fake_structure(symbol, timeframe="M5", candles=300, left=3, right=3):
        if timeframe == "H4":
            return _build_structure(h4_trend)
        if timeframe == "H1":
            return _build_structure(h1_trend)
        return _build_structure(m5_trend)

    monkeypatch.setattr(decision_center_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=300: fake_candles(symbol, timeframe, count)))
    monkeypatch.setattr(decision_center_module.MarketService, "latest_tick", classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0, ask=1.0002, spread=2.0)))
    monkeypatch.setattr(decision_center_module.SmartMoneyService, "structure", staticmethod(fake_structure))
    monkeypatch.setattr(multi_timeframe_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=300: fake_candles(symbol, timeframe, count)))
    monkeypatch.setattr(multi_timeframe_module.SmartMoneyService, "structure", staticmethod(fake_structure))


def test_aligned_bullish_report(monkeypatch):
    _patch_timeframe_services(monkeypatch, h4_trend="BULLISH", h1_trend="BULLISH", m5_trend="BULLISH")

    report = multi_timeframe_module.MultiTimeframeBiasService.build_report("EURUSD")

    assert report.h4.bias == MultiTimeframeBiasState.BULLISH
    assert report.h1.bias == MultiTimeframeBiasState.BULLISH
    assert report.m5.bias == MultiTimeframeBiasState.BULLISH
    assert report.alignment == MultiTimeframeAlignment.ALIGNED_BULLISH
    assert report.conflict is False


def test_aligned_bearish_report(monkeypatch):
    _patch_timeframe_services(monkeypatch, h4_trend="BEARISH", h1_trend="BEARISH", m5_trend="BEARISH")

    report = multi_timeframe_module.MultiTimeframeBiasService.build_report("EURUSD")

    assert report.alignment == MultiTimeframeAlignment.ALIGNED_BEARISH


def test_mixed_alignment(monkeypatch):
    _patch_timeframe_services(monkeypatch, h4_trend="BULLISH", h1_trend="BEARISH", m5_trend="BULLISH")

    report = multi_timeframe_module.MultiTimeframeBiasService.build_report("EURUSD")

    assert report.alignment == MultiTimeframeAlignment.MIXED


def test_conflict_alignment(monkeypatch):
    _patch_timeframe_services(monkeypatch, h4_trend="BULLISH", h1_trend="BEARISH", m5_trend="BEARISH")

    report = multi_timeframe_module.MultiTimeframeBiasService.build_report("EURUSD")

    assert report.alignment == MultiTimeframeAlignment.CONFLICT


def test_missing_h4_data_sets_unavailable(monkeypatch):
    def fake_candles(symbol, timeframe, count=300):
        if timeframe == "H4":
            return []
        return [_build_candle(1.0)]

    def fake_structure(symbol, timeframe="M5", candles=300, left=3, right=3):
        return _build_structure("BULLISH")

    monkeypatch.setattr(decision_center_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=300: fake_candles(symbol, timeframe, count)))
    monkeypatch.setattr(decision_center_module.MarketService, "latest_tick", classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0, ask=1.0002, spread=2.0)))
    monkeypatch.setattr(decision_center_module.SmartMoneyService, "structure", staticmethod(fake_structure))
    monkeypatch.setattr(multi_timeframe_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=300: fake_candles(symbol, timeframe, count)))
    monkeypatch.setattr(multi_timeframe_module.SmartMoneyService, "structure", staticmethod(fake_structure))

    report = multi_timeframe_module.MultiTimeframeBiasService.build_report("EURUSD")

    assert report.h4.bias == MultiTimeframeBiasState.UNAVAILABLE
    assert report.alignment == MultiTimeframeAlignment.UNAVAILABLE


def test_decision_center_includes_multitimeframe_context(monkeypatch):
    _patch_timeframe_services(monkeypatch, h4_trend="BULLISH", h1_trend="BULLISH", m5_trend="BULLISH")

    decision = DecisionContext(symbol="EURUSD.pro", side=TradeSide.BUY, volume=0.10, sl=1.0980, tp=1.1030, price=1.1000)
    report = DecisionCenter.build_report(decision)

    assert report.multi_timeframe_bias is not None
    assert report.multi_timeframe_bias.alignment == MultiTimeframeAlignment.ALIGNED_BULLISH


def test_decision_api_returns_multitimeframe_context(monkeypatch):
    def fake_candles(symbol, timeframe, count=300):
        return [_build_candle(1.0)]

    monkeypatch.setattr(decision_center_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=300: fake_candles(symbol, timeframe, count)))
    monkeypatch.setattr(decision_center_module.MarketService, "latest_tick", classmethod(lambda cls, symbol: SimpleNamespace(symbol=symbol, bid=1.0, ask=1.0002, spread=2.0)))
    monkeypatch.setattr(decision_center_module.SmartMoneyService, "structure", staticmethod(lambda symbol, timeframe="M5", candles=300, left=3, right=3: _build_structure("BULLISH")))
    monkeypatch.setattr(multi_timeframe_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=300: fake_candles(symbol, timeframe, count)))
    monkeypatch.setattr(multi_timeframe_module.SmartMoneyService, "structure", staticmethod(lambda symbol, timeframe="M5", candles=300, left=3, right=3: _build_structure("BULLISH")))

    client = TestClient(app)
    response = client.post(
        "/api/v1/decision/report",
        json={
            "symbol": "EURUSD.pro",
            "side": "BUY",
            "volume": 0.1,
            "sl": 1.0980,
            "tp": 1.1030,
            "price": 1.1000,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "multi_timeframe_bias" in payload
