from app.scanner.scheduler import ScannerScheduler


class FakeScannerService:
    def __init__(self):
        self.calls = 0

    def refresh_opportunities(self):
        self.calls += 1
        return []


def test_scheduler_run_once_executes_refresh():
    service = FakeScannerService()
    scheduler = ScannerScheduler(service=service, interval_seconds=30)

    scheduler.run_once()

    assert service.calls == 1


def test_scheduler_start_and_stop(monkeypatch):
    service = FakeScannerService()
    scheduler = ScannerScheduler(service=service, interval_seconds=0)

    # Run immediately without waiting to ensure the loop triggers.
    scheduler.start()
    scheduler.stop()

    assert service.calls >= 1
