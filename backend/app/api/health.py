from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from app.analytics.router import get_analytics_service
from app.config.settings import settings
from app.journal.router import get_journal_service
from app.journal.service import JournalService
from app.playbook.router import get_playbook_service
from app.playbook.service import PlaybookService
from app.schemas.health import HealthSnapshot
from app.schemas.health import HealthStatus
from app.schemas.operational import OperationalReadinessItem
from app.schemas.operational import OperationalReadinessSnapshot
from app.schemas.operational import OperationalStatus
from app.services.health_engine import HealthEngine
from app.analytics.service import AnalyticsService
from app.market.service import MarketService

router = APIRouter(tags=["Health"])


def build_health_payload() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health")
async def health():
    return build_health_payload()


def _status_to_operational(status: HealthStatus) -> OperationalStatus:
    if status == HealthStatus.HEALTHY:
        return OperationalStatus.GREEN
    if status == HealthStatus.WARNING:
        return OperationalStatus.YELLOW
    return OperationalStatus.RED


def _format_observed_at(value: datetime | None) -> str:
    return value.isoformat() if value is not None else "No timestamp available."


def _build_readiness_items(
    snapshot: HealthSnapshot,
    symbol: str,
    timeframe: str,
    journal_count: int,
    enabled_playbooks: int,
    analytics_trades: int,
):
    terminal = MarketService.terminal_status()

    journal_status = OperationalStatus.GREEN if journal_count > 0 else OperationalStatus.YELLOW
    playbook_status = OperationalStatus.GREEN if enabled_playbooks > 0 else OperationalStatus.YELLOW
    analytics_status = OperationalStatus.GREEN if analytics_trades > 0 else OperationalStatus.YELLOW

    broker_detail = (
        f"{terminal.company} · {terminal.server}" if terminal.connected and terminal.company and terminal.server else "Broker metadata unavailable."
    )
    market_detail = (
        f"Live feed checked on {symbol.upper()} {timeframe.upper()}. "
        f"Last tick={_format_observed_at(snapshot.lastTickTime)} · last candle={_format_observed_at(snapshot.lastCandleTime)}"
    )

    return [
        OperationalReadinessItem(
            key="mt5",
            label="MT5",
            status=_status_to_operational(snapshot.mt5Connection),
            detail="Terminal connected and responding." if terminal.connected else "MT5 disconnected.",
        ),
        OperationalReadinessItem(
            key="broker",
            label="Broker",
            status=_status_to_operational(snapshot.mt5Connection),
            detail=broker_detail,
        ),
        OperationalReadinessItem(
            key="market-feed",
            label="Market Feed",
            status=_status_to_operational(snapshot.marketStatus),
            detail=market_detail,
        ),
        OperationalReadinessItem(
            key="last-tick",
            label="Last Tick",
            status=_status_to_operational(HealthEngine(symbol=symbol, timeframe=timeframe)._status_from_age(snapshot.lastTickTime, settings.tickTimeout, snapshot.timestamp)),
            detail=f"Last tick observed at {_format_observed_at(snapshot.lastTickTime)}",
            observedAt=snapshot.lastTickTime,
        ),
        OperationalReadinessItem(
            key="last-candle",
            label="Last Candle",
            status=_status_to_operational(HealthEngine(symbol=symbol, timeframe=timeframe)._status_from_age(snapshot.lastCandleTime, settings.tickTimeout, snapshot.timestamp)),
            detail=f"Last candle observed at {_format_observed_at(snapshot.lastCandleTime)}",
            observedAt=snapshot.lastCandleTime,
        ),
        OperationalReadinessItem(
            key="decision-center",
            label="Decision Center",
            status=_status_to_operational(snapshot.pipelineStatus),
            detail=(
                f"Live context refreshed from current market inputs. Latency={snapshot.pipelineLatency:.2f}s"
                if snapshot.pipelineLatency is not None
                else "No current decision context available for the selected market."
            ),
            observedAt=snapshot.lastDecisionContext,
        ),
        OperationalReadinessItem(
            key="journal",
            label="Journal",
            status=journal_status,
            detail=(
                f"{journal_count} historical entries available."
                if journal_count > 0
                else "Journal service available but no historical entries exist yet."
            ),
        ),
        OperationalReadinessItem(
            key="playbook",
            label="Playbook",
            status=playbook_status,
            detail=(
                f"{enabled_playbooks} enabled setups available for live matching."
                if enabled_playbooks > 0
                else "Playbook service is available but no enabled setups exist."
            ),
        ),
        OperationalReadinessItem(
            key="analytics",
            label="Analytics",
            status=analytics_status,
            detail=(
                f"Analytics built from {analytics_trades} tracked trades."
                if analytics_trades > 0
                else "Analytics service available but there is no tracked history yet."
            ),
        ),
    ]


@router.get("/health/readiness", response_model=OperationalReadinessSnapshot)
async def readiness(
    symbol: str | None = None,
    timeframe: str | None = None,
    journal_service: JournalService = Depends(get_journal_service),
    playbook_service: PlaybookService = Depends(get_playbook_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    selected_symbol = (symbol or settings.defaultSymbol).upper()
    selected_timeframe = (timeframe or settings.defaultTimeframe).upper()

    snapshot = HealthEngine(
        symbol=selected_symbol,
        timeframe=selected_timeframe,
    ).collect_snapshot()

    journal_entries = journal_service.listEntries()
    playbook_setups = playbook_service.listSetups()
    analytics_summary = analytics_service.getSummary()

    items = _build_readiness_items(
        snapshot=snapshot,
        symbol=selected_symbol,
        timeframe=selected_timeframe,
        journal_count=len(journal_entries),
        enabled_playbooks=sum(1 for setup in playbook_setups if setup.enabled),
        analytics_trades=analytics_summary.totalTrades,
    )

    overall = OperationalStatus.GREEN
    if any(item.status == OperationalStatus.RED for item in items):
        overall = OperationalStatus.RED
    elif any(item.status == OperationalStatus.YELLOW for item in items):
        overall = OperationalStatus.YELLOW

    return OperationalReadinessSnapshot(
        symbol=selected_symbol,
        timeframe=selected_timeframe,
        generatedAt=snapshot.timestamp,
        overallStatus=overall,
        items=items,
    )