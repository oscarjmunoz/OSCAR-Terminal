from types import SimpleNamespace

from app.scanner.models import OpportunityStage
from app.scanner.repository import InMemoryScannerRepository
from app.scanner.service import ScannerService
from app.scanner import service as scanner_service_module


def test_refresh_opportunities_builds_snapshots(monkeypatch):
    repository = InMemoryScannerRepository()
    service = ScannerService(repository=repository)

    monkeypatch.setattr(scanner_service_module.settings, "availableSymbols", "EURUSD,USDJPY")
    monkeypatch.setattr(scanner_service_module.settings, "defaultTimeframe", "M5")
    monkeypatch.setattr(scanner_service_module.settings, "maxSlippage", 20)

    structure = SimpleNamespace(trend="BULLISH", bos=True, choch=True, mss=True)

    monkeypatch.setattr(
        scanner_service_module.SmartMoneyService,
        "structure",
        staticmethod(lambda symbol, timeframe, candles=300, left=3, right=3: structure),
    )
    monkeypatch.setattr(
        scanner_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: SimpleNamespace(spread=1.4, bid=1.1, ask=1.1001)),
    )

    snapshots = service.refresh_opportunities()

    assert len(snapshots) == 2
    assert snapshots[0].stage == OpportunityStage.ENTRY_READY
    assert snapshots[0].health == "GREEN"
    assert "Context BUY" in snapshots[0].decision_summary


def test_refresh_opportunities_handles_missing_structure(monkeypatch):
    repository = InMemoryScannerRepository()
    service = ScannerService(repository=repository)

    monkeypatch.setattr(scanner_service_module.settings, "availableSymbols", "EURUSD")

    monkeypatch.setattr(
        scanner_service_module.SmartMoneyService,
        "structure",
        staticmethod(lambda symbol, timeframe, candles=300, left=3, right=3: None),
    )
    monkeypatch.setattr(
        scanner_service_module.MarketService,
        "latest_tick",
        classmethod(lambda cls, symbol: None),
    )

    snapshots = service.refresh_opportunities()

    assert len(snapshots) == 1
    assert snapshots[0].stage == OpportunityStage.BUILDING_CONTEXT
    assert snapshots[0].bias == "UNKNOWN"
    assert snapshots[0].health == "RED"
