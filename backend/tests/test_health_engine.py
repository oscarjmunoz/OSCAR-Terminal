from datetime import datetime
from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.schemas.health import HealthSnapshot
from app.schemas.health import HealthStatus
from app.schemas.health import HealthStatusChanged
from app.services.health_engine import HealthEngine
from app.services.health_service import HealthService


def test_health_snapshot_is_immutable():

    snapshot = HealthSnapshot(
        timestamp=datetime(2026, 8, 3, 10, 0, 0),
        overallStatus=HealthStatus.HEALTHY,
        mt5Connection=HealthStatus.HEALTHY,
        pipelineStatus=HealthStatus.HEALTHY,
        marketStatus=HealthStatus.HEALTHY,
        eventBusStatus=HealthStatus.HEALTHY,
        lastDecisionContext=datetime(2026, 8, 3, 9, 59, 0),
        lastTickTime=datetime(2026, 8, 3, 9, 59, 30),
        lastCandleTime=datetime(2026, 8, 3, 9, 55, 0),
        pipelineLatency=60.0,
    )

    assert snapshot.model_dump()["overallStatus"] == HealthStatus.HEALTHY

    with pytest.raises((TypeError, ValidationError)):
        snapshot.overallStatus = HealthStatus.ERROR


def test_health_status_changed_model():

    event = HealthStatusChanged(
        timestamp=datetime(2026, 8, 3, 10, 0, 0),
        previousStatus=HealthStatus.WARNING,
        currentStatus=HealthStatus.ERROR,
    )

    assert event.previousStatus == HealthStatus.WARNING
    assert event.currentStatus == HealthStatus.ERROR
    assert event.model_dump()["timestamp"] == datetime(2026, 8, 3, 10, 0, 0)


def test_health_engine_detects_loss_of_mt5_and_missing_ticks(monkeypatch):

    current_time = datetime(2026, 8, 3, 10, 0, 0)
    engine = HealthEngine(
        pipeline_timeout=30,
        tick_timeout=15,
        clock=lambda: current_time,
    )

    monkeypatch.setattr(engine, "_read_mt5_connection", lambda: False)
    monkeypatch.setattr(engine, "_read_last_tick_time", lambda: None)
    monkeypatch.setattr(engine, "_read_last_candle_time", lambda: None)
    monkeypatch.setattr(engine, "_read_last_decision_context", lambda: None)
    monkeypatch.setattr(engine, "_read_pipeline_responsive", lambda: False)
    monkeypatch.setattr(engine, "_read_event_bus_active", lambda: True)

    snapshot = engine.collect_snapshot()

    assert snapshot.mt5Connection == HealthStatus.ERROR
    assert snapshot.marketStatus == HealthStatus.ERROR
    assert snapshot.overallStatus == HealthStatus.ERROR


def test_health_engine_detects_pipeline_timeout(monkeypatch):

    current_time = datetime(2026, 8, 3, 10, 0, 0)
    engine = HealthEngine(
        pipeline_timeout=30,
        tick_timeout=15,
        clock=lambda: current_time,
    )

    monkeypatch.setattr(engine, "_read_mt5_connection", lambda: True)
    monkeypatch.setattr(
        engine,
        "_read_last_tick_time",
        lambda: current_time - timedelta(seconds=5),
    )
    monkeypatch.setattr(
        engine,
        "_read_last_candle_time",
        lambda: current_time - timedelta(seconds=5),
    )
    monkeypatch.setattr(
        engine,
        "_read_last_decision_context",
        lambda: current_time - timedelta(seconds=45),
    )
    monkeypatch.setattr(engine, "_read_pipeline_responsive", lambda: True)
    monkeypatch.setattr(engine, "_read_event_bus_active", lambda: True)

    snapshot = engine.collect_snapshot()

    assert snapshot.pipelineStatus == HealthStatus.WARNING
    assert snapshot.pipelineLatency == 45.0
    assert snapshot.overallStatus == HealthStatus.WARNING


def test_health_engine_detects_stopped_pipeline(monkeypatch):

    current_time = datetime(2026, 8, 3, 10, 0, 0)
    engine = HealthEngine(
        pipeline_timeout=30,
        tick_timeout=15,
        clock=lambda: current_time,
    )

    monkeypatch.setattr(engine, "_read_mt5_connection", lambda: True)
    monkeypatch.setattr(
        engine,
        "_read_last_tick_time",
        lambda: current_time - timedelta(seconds=5),
    )
    monkeypatch.setattr(
        engine,
        "_read_last_candle_time",
        lambda: current_time - timedelta(seconds=5),
    )
    monkeypatch.setattr(
        engine,
        "_read_last_decision_context",
        lambda: current_time - timedelta(seconds=10),
    )
    monkeypatch.setattr(engine, "_read_pipeline_responsive", lambda: False)
    monkeypatch.setattr(engine, "_read_event_bus_active", lambda: True)

    snapshot = engine.collect_snapshot()

    assert snapshot.pipelineStatus == HealthStatus.ERROR
    assert snapshot.overallStatus == HealthStatus.ERROR


def test_health_service_publishes_only_on_status_change():

    healthy = HealthSnapshot(
        timestamp=datetime(2026, 8, 3, 10, 0, 0),
        overallStatus=HealthStatus.HEALTHY,
        mt5Connection=HealthStatus.HEALTHY,
        pipelineStatus=HealthStatus.HEALTHY,
        marketStatus=HealthStatus.HEALTHY,
        eventBusStatus=HealthStatus.HEALTHY,
        lastDecisionContext=datetime(2026, 8, 3, 9, 59, 0),
        lastTickTime=datetime(2026, 8, 3, 9, 59, 30),
        lastCandleTime=datetime(2026, 8, 3, 9, 55, 0),
        pipelineLatency=60.0,
    )

    warning = healthy.model_copy(update={"overallStatus": HealthStatus.WARNING})
    error = healthy.model_copy(update={"overallStatus": HealthStatus.ERROR})

    snapshots = [healthy, healthy, warning, warning, error]

    class FakeEngine:
        def __init__(self, items):
            self._items = list(items)

        def collect_snapshot(self):
            return self._items.pop(0)

    published_events = []
    service = HealthService(
        engine=FakeEngine(snapshots),
        publisher=published_events.append,
    )

    assert service.getHealthSnapshot().overallStatus == HealthStatus.HEALTHY
    assert service.getHealthSnapshot().overallStatus == HealthStatus.HEALTHY
    assert service.getHealthSnapshot().overallStatus == HealthStatus.WARNING
    assert service.getHealthSnapshot().overallStatus == HealthStatus.WARNING
    assert service.getHealthSnapshot().overallStatus == HealthStatus.ERROR

    assert len(published_events) == 2
    assert published_events[0].previousStatus == HealthStatus.HEALTHY
    assert published_events[0].currentStatus == HealthStatus.WARNING
    assert published_events[1].previousStatus == HealthStatus.WARNING
    assert published_events[1].currentStatus == HealthStatus.ERROR