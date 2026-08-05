from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.analytics.router import get_analytics_service
from app.journal.router import get_journal_service
from app.main import app
from app.playbook.router import get_playbook_service
from app.schemas.health import HealthSnapshot
from app.schemas.health import HealthStatus
from app.services import operational_analysis as operational_analysis_module
from app.api import health as health_module

client = TestClient(app)


def _build_candle(index: int, open_price: float, close_price: float, high: float, low: float, volume: int):
    return SimpleNamespace(
        time=datetime(2026, 8, 4, 10, index % 60, 0),
        open=open_price,
        close=close_price,
        high=high,
        low=low,
        tick_volume=volume,
    )


def test_live_report_uses_requested_timeframe(monkeypatch):
    observed = {"timeframes": []}

    tick = SimpleNamespace(symbol="EURUSD", bid=1.0890, ask=1.0892, spread=2.0)
    candles = [_build_candle(1, 1.0880, 1.0885, 1.0895, 1.0875, 180)]
    structure = SimpleNamespace(
        trend="BEARISH",
        bos=True,
        choch=False,
        mss=True,
        last_high=1.0900,
        last_low=1.0870,
    )

    monkeypatch.setattr(operational_analysis_module.MarketService, "terminal_status", classmethod(lambda cls: SimpleNamespace(connected=True, company="Broker X", server="Demo-01")))
    monkeypatch.setattr(operational_analysis_module.MarketService, "latest_tick", classmethod(lambda cls, symbol: tick))

    def fake_candles(cls, symbol, timeframe, count=120):
        observed["timeframes"].append(timeframe)
        return candles

    monkeypatch.setattr(operational_analysis_module.MarketService, "candles", classmethod(fake_candles))
    monkeypatch.setattr(
        operational_analysis_module.SmartMoneyService,
        "structure",
        staticmethod(lambda symbol, timeframe="M5", candles=300, left=3, right=3: observed["timeframes"].append(timeframe) or structure),
    )

    response = client.post("/api/v1/decision/live-report", json={"symbol": "EURUSD", "timeframe": "H1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["context"]["comment"] == "live-operational-analysis:H1"
    assert payload["context"]["symbol"] == "EURUSD"
    assert observed["timeframes"] == ["H1", "H1"]


def test_operational_settings_contract():
    response = client.get("/api/v1/system/settings")

    assert response.status_code == 200
    payload = response.json()
    assert payload["defaultSymbol"]
    assert payload["defaultTimeframe"]
    assert "EURUSD" in payload["availableSymbols"]
    assert "M5" in payload["availableTimeframes"]


def test_operational_readiness_contract(monkeypatch):
    snapshot = HealthSnapshot(
        timestamp=datetime(2026, 8, 4, 10, 10, 0),
        overallStatus=HealthStatus.HEALTHY,
        mt5Connection=HealthStatus.HEALTHY,
        pipelineStatus=HealthStatus.HEALTHY,
        marketStatus=HealthStatus.WARNING,
        eventBusStatus=HealthStatus.HEALTHY,
        lastDecisionContext=datetime(2026, 8, 4, 10, 9, 59),
        lastTickTime=datetime(2026, 8, 4, 10, 9, 58),
        lastCandleTime=datetime(2026, 8, 4, 10, 5, 0),
        pipelineLatency=1.2,
    )

    class FakeJournalService:
        def listEntries(self):
            return [SimpleNamespace(id="j-1")]

    class FakePlaybookService:
        def listSetups(self):
            return [SimpleNamespace(enabled=True)]

    class FakeAnalyticsService:
        def getSummary(self):
            return SimpleNamespace(totalTrades=8)

    monkeypatch.setattr(health_module.HealthEngine, "collect_snapshot", lambda self: snapshot)
    monkeypatch.setattr(health_module.MarketService, "terminal_status", classmethod(lambda cls: SimpleNamespace(connected=True, company="Broker X", server="Demo-01")))

    app.dependency_overrides[get_journal_service] = lambda: FakeJournalService()
    app.dependency_overrides[get_playbook_service] = lambda: FakePlaybookService()
    app.dependency_overrides[get_analytics_service] = lambda: FakeAnalyticsService()

    try:
        response = client.get("/api/v1/health/readiness?symbol=EURUSD&timeframe=M5")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["overallStatus"] == "RED"
    labels = {item["label"] for item in payload["items"]}
    assert labels == {
        "MT5",
        "Broker",
        "Market Feed",
        "Last Tick",
        "Last Candle",
        "Decision Center",
        "Journal",
        "Playbook",
        "Analytics",
    }
