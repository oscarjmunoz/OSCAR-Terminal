from app.core.logger import logger
from app.schemas.health import HealthStatusChanged
from app.services.health_engine import HealthEngine


class HealthService:

    def __init__(self, engine: HealthEngine | None = None, publisher=None):
        self._engine = engine or HealthEngine()
        self._publisher = publisher
        self._last_status = None

    def getHealthSnapshot(self):

        snapshot = self._engine.collect_snapshot()

        if self._last_status is not None and self._last_status != snapshot.overallStatus:

            logger.info(
                "Health status changed from %s to %s",
                self._last_status,
                snapshot.overallStatus,
            )

            if snapshot.overallStatus.name == "ERROR":
                logger.warning("Health degradation detected.")

            if self._last_status.name == "ERROR" and snapshot.overallStatus.name == "HEALTHY":
                logger.info("Health recovered.")

            if self._publisher is not None:
                self._publisher(
                    HealthStatusChanged(
                        timestamp=snapshot.timestamp,
                        previousStatus=self._last_status,
                        currentStatus=snapshot.overallStatus,
                    )
                )

        self._last_status = snapshot.overallStatus

        return snapshot