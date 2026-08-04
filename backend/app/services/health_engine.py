from datetime import datetime
from typing import Callable

from app.config.settings import settings
from app.core.logger import logger
from app.market.service import MarketService
from app.schemas.health import HealthSnapshot
from app.schemas.health import HealthStatus


class HealthEngine:

    def __init__(
        self,
        symbol: str = "USDCHF",
        timeframe: str = "M5",
        health_check_interval: int | None = None,
        pipeline_timeout: int | None = None,
        tick_timeout: int | None = None,
        clock: Callable[[], datetime] | None = None,
    ):

        self.symbol = symbol
        self.timeframe = timeframe
        self.healthCheckInterval = (
            health_check_interval
            if health_check_interval is not None
            else settings.healthCheckInterval
        )
        self.pipelineTimeout = (
            pipeline_timeout
            if pipeline_timeout is not None
            else settings.pipelineTimeout
        )
        self.tickTimeout = (
            tick_timeout
            if tick_timeout is not None
            else settings.tickTimeout
        )
        self._clock = clock or datetime.now
        self._last_tick_observed: datetime | None = None
        self._last_candle_observed: datetime | None = None
        self._last_decision_context_seen: datetime | None = None
        self._event_bus_last_activity: datetime | None = None
        self._market_signal_seen = False

    def collect_snapshot(self) -> HealthSnapshot:

        timestamp = self._clock()

        mt5_connected = self._read_mt5_connection()
        last_tick_time = self._read_last_tick_time()
        last_candle_time = self._read_last_candle_time()
        last_decision_context = self._read_last_decision_context()
        pipeline_active = self._read_pipeline_responsive()
        event_bus_active = self._read_event_bus_active()

        mt5_status = self._status_from_boolean(mt5_connected)
        market_status = self._market_status(
            mt5_status,
            last_tick_time,
            last_candle_time,
            timestamp,
        )
        pipeline_status, pipeline_latency = self._pipeline_status(
            pipeline_active,
            last_decision_context,
            timestamp,
        )
        event_bus_status = self._status_from_boolean(event_bus_active)

        overall_status = self._overall_status(
            mt5_status,
            market_status,
            pipeline_status,
            event_bus_status,
        )

        return HealthSnapshot(
            timestamp=timestamp,
            overallStatus=overall_status,
            mt5Connection=mt5_status,
            pipelineStatus=pipeline_status,
            marketStatus=market_status,
            eventBusStatus=event_bus_status,
            lastDecisionContext=last_decision_context,
            lastTickTime=last_tick_time,
            lastCandleTime=last_candle_time,
            pipelineLatency=pipeline_latency,
        )

    def _read_mt5_connection(self) -> bool:
        return MarketService.terminal_status().connected

    def _read_last_tick_time(self) -> datetime | None:
        tick_time = MarketService.latest_tick_time(self.symbol)

        if tick_time is not None:
            if self._last_tick_observed != tick_time:
                logger.info(
                    "TickReceived observed | symbol=%s | time=%s",
                    self.symbol,
                    tick_time,
                )
            self._last_tick_observed = tick_time
            self._event_bus_last_activity = tick_time
            self._market_signal_seen = True

        return tick_time

    def _read_last_candle_time(self) -> datetime | None:
        candle_time = MarketService.latest_candle_time(self.symbol, self.timeframe)

        if candle_time is not None:
            if self._last_candle_observed != candle_time:
                logger.info(
                    "CandleClosed observed | symbol=%s | timeframe=%s | time=%s",
                    self.symbol,
                    self.timeframe,
                    candle_time,
                )
            self._last_candle_observed = candle_time
            self._event_bus_last_activity = candle_time
            self._market_signal_seen = True

        return candle_time

    def _read_last_decision_context(self) -> datetime | None:
        candidates = [
            value
            for value in (self._last_tick_observed, self._last_candle_observed)
            if value is not None
        ]

        if not candidates:
            return None

        decision_time = max(candidates)

        if self._last_decision_context_seen != decision_time:
            logger.info(
                "DecisionContext updated | symbol=%s | time=%s",
                self.symbol,
                decision_time,
            )

        self._last_decision_context_seen = decision_time
        return self._last_decision_context_seen

    def _read_pipeline_responsive(self) -> bool:
        responsive = self._last_decision_context_seen is not None
        logger.info("InstitutionalPipeline heartbeat | active=%s", responsive)
        return responsive

    def _read_event_bus_active(self) -> bool:
        event_active = self._event_bus_last_activity is not None and self._market_signal_seen
        if event_active:
            logger.info(
                "EventBus publish/consume observed | last_activity=%s",
                self._event_bus_last_activity,
            )
        else:
            logger.info("EventBus publish/consume observed | no activity")
        return event_active

    def _status_from_boolean(self, value: bool) -> HealthStatus:
        return HealthStatus.HEALTHY if value else HealthStatus.ERROR

    def _status_from_age(
        self,
        value: datetime | None,
        timeout_seconds: int,
        current_time: datetime,
    ) -> HealthStatus:

        if value is None:
            return HealthStatus.ERROR

        age_seconds = (current_time - value).total_seconds()

        if age_seconds <= timeout_seconds:
            return HealthStatus.HEALTHY

        if age_seconds <= timeout_seconds * 2:
            return HealthStatus.WARNING

        return HealthStatus.ERROR

    def _market_status(
        self,
        mt5_status: HealthStatus,
        last_tick_time: datetime | None,
        last_candle_time: datetime | None,
        current_time: datetime,
    ) -> HealthStatus:

        if mt5_status == HealthStatus.ERROR:
            return HealthStatus.ERROR

        tick_status = self._status_from_age(
            last_tick_time,
            self.tickTimeout,
            current_time,
        )

        candle_status = self._status_from_age(
            last_candle_time,
            self.tickTimeout,
            current_time,
        )

        return self._worst_status(tick_status, candle_status)

    def _pipeline_status(
        self,
        pipeline_active: bool,
        last_decision_context: datetime | None,
        current_time: datetime,
    ) -> tuple[HealthStatus, float | None]:

        if not pipeline_active:
            return HealthStatus.ERROR, None

        if last_decision_context is None:
            return HealthStatus.ERROR, None

        pipeline_latency = (current_time - last_decision_context).total_seconds()

        if pipeline_latency <= self.pipelineTimeout:
            return HealthStatus.HEALTHY, pipeline_latency

        if pipeline_latency <= self.pipelineTimeout * 2:
            return HealthStatus.WARNING, pipeline_latency

        return HealthStatus.ERROR, pipeline_latency

    def _overall_status(self, *statuses: HealthStatus) -> HealthStatus:
        if HealthStatus.ERROR in statuses:
            return HealthStatus.ERROR

        if HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY

    def _worst_status(self, *statuses: HealthStatus) -> HealthStatus:
        return self._overall_status(*statuses)