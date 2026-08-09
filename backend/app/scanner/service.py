from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.config.settings import settings
from app.market.service import MarketService
from app.scanner.models import OpportunitySnapshot
from app.scanner.models import OpportunityStage
from app.scanner.repository import InMemoryScannerRepository
from app.scanner.repository import ScannerRepository
from app.scanner.schemas import OpportunitySnapshotSchema
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.smart_money.service import SmartMoneyService


class ScannerService:

    def __init__(
        self,
        repository: ScannerRepository | None = None,
    ):
        self._repository = repository or InMemoryScannerRepository()

    def list_opportunities(self) -> list[OpportunitySnapshotSchema]:
        snapshots = self._repository.list()
        return [self._to_schema(item) for item in snapshots]

    def refresh_opportunities(self) -> list[OpportunitySnapshotSchema]:
        snapshots: list[OpportunitySnapshotSchema] = []
        for symbol in self._symbols_from_settings():
            snapshot = self._build_snapshot(symbol, settings.defaultTimeframe)
            self._repository.upsert(snapshot)
            snapshots.append(self._to_schema(snapshot))

        return snapshots

    def _build_snapshot(self, symbol: str, timeframe: str) -> OpportunitySnapshot:
        structure = SmartMoneyService.structure(symbol=symbol, timeframe=timeframe, candles=300, left=3, right=3)
        tick = MarketService.latest_tick(symbol)

        trend = self._trend(structure)
        liquidity_target = self._liquidity_target(trend)

        decision_side = TradeSide.BUY if trend == "BULLISH" else TradeSide.SELL
        decision_context = DecisionContext(
            symbol=symbol,
            side=decision_side,
            volume=0.01,
        )

        spread = float(getattr(tick, "spread", 0.0) or 0.0) if tick is not None else 0.0
        stage = self._stage(structure, spread, symbol, timeframe)

        score = self._institutional_score_placeholder(structure)
        quality = self._execution_quality_placeholder(structure)
        health = self._health_label(structure, spread)

        summary = (
            f"Context {decision_context.side.value} for {decision_context.symbol}; "
            f"trend={trend}, target={liquidity_target}, spread={spread:.1f}."
        )

        return OpportunitySnapshot(
            symbol=symbol,
            timeframe=timeframe,
            bias=trend,
            structure=self._structure_label(structure),
            liquidity_target=liquidity_target,
            stage=stage,
            institutional_score=score,
            execution_quality=quality,
            last_update=datetime.now(timezone.utc),
            health=health,
            decision_summary=summary,
        )

    @staticmethod
    def _symbols_from_settings() -> list[str]:
        raw = settings.availableSymbols or ""
        parsed = [item.strip().upper() for item in raw.split(",") if item.strip()]
        return parsed or [settings.defaultSymbol.upper()]

    @staticmethod
    def _trend(structure) -> str:
        if structure is None:
            return "UNKNOWN"

        trend = str(getattr(structure, "trend", "UNKNOWN") or "UNKNOWN").upper()
        return trend

    @staticmethod
    def _liquidity_target(trend: str) -> str:
        if trend == "BULLISH":
            return "BUY_SIDE_LIQUIDITY"

        if trend == "BEARISH":
            return "SELL_SIDE_LIQUIDITY"

        return "MIXED_LIQUIDITY"

    def _stage(self, structure, spread: float, symbol: str, timeframe: str) -> OpportunityStage:
        previous = self._repository.get(symbol, timeframe)
        if previous is not None and previous.stage == OpportunityStage.TRADE_ACTIVE:
            return OpportunityStage.TRADE_ACTIVE

        if structure is None:
            return OpportunityStage.BUILDING_CONTEXT

        bos = bool(getattr(structure, "bos", False))
        choch = bool(getattr(structure, "choch", False))
        mss = bool(getattr(structure, "mss", False))

        if not bos and not choch:
            return OpportunityStage.WAITING_LIQUIDITY

        if choch and not bos:
            return OpportunityStage.WAITING_SWEEP

        if not mss:
            return OpportunityStage.WAITING_MSS

        if mss and not bos:
            return OpportunityStage.WAITING_DISPLACEMENT

        if spread <= float(settings.maxSlippage):
            return OpportunityStage.ENTRY_READY

        return OpportunityStage.WAITING_DISPLACEMENT

    @staticmethod
    def _structure_label(structure) -> str:
        if structure is None:
            return "UNKNOWN"

        trend = str(getattr(structure, "trend", "UNKNOWN") or "UNKNOWN").upper()
        bos = bool(getattr(structure, "bos", False))
        choch = bool(getattr(structure, "choch", False))
        mss = bool(getattr(structure, "mss", False))

        return f"{trend}|BOS={int(bos)}|CHOCH={int(choch)}|MSS={int(mss)}"

    @staticmethod
    def _institutional_score_placeholder(structure) -> float:
        if structure is None:
            return 0.0

        score = 40.0
        if bool(getattr(structure, "bos", False)):
            score += 20.0
        if bool(getattr(structure, "choch", False)):
            score += 10.0
        if bool(getattr(structure, "mss", False)):
            score += 20.0

        return min(score, 100.0)

    @staticmethod
    def _execution_quality_placeholder(structure) -> float:
        if structure is None:
            return 0.0

        quality = 35.0
        if bool(getattr(structure, "mss", False)):
            quality += 25.0
        if bool(getattr(structure, "bos", False)):
            quality += 20.0

        return min(quality, 100.0)

    @staticmethod
    def _health_label(structure, spread: float) -> str:
        if structure is None:
            return "RED"

        if spread > float(settings.maxSlippage):
            return "YELLOW"

        return "GREEN"

    @staticmethod
    def _to_schema(snapshot: OpportunitySnapshot) -> OpportunitySnapshotSchema:
        return OpportunitySnapshotSchema(
            symbol=snapshot.symbol,
            timeframe=snapshot.timeframe,
            bias=snapshot.bias,
            structure=snapshot.structure,
            liquidity_target=snapshot.liquidity_target,
            stage=snapshot.stage,
            institutional_score=round(snapshot.institutional_score, 2),
            execution_quality=round(snapshot.execution_quality, 2),
            last_update=snapshot.last_update,
            health=snapshot.health,
            decision_summary=snapshot.decision_summary,
        )
