from __future__ import annotations

from threading import Event
from threading import Thread

from app.scanner.service import ScannerService


class ScannerScheduler:

    def __init__(
        self,
        service: ScannerService,
        interval_seconds: int = 30,
    ):
        self._service = service
        self._interval_seconds = interval_seconds
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, name="scanner-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=2)

        self._thread = None

    def run_once(self) -> None:
        self._service.refresh_opportunities()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self.run_once()
            self._stop_event.wait(self._interval_seconds)
