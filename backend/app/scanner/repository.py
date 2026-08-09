from __future__ import annotations

from datetime import datetime
from threading import RLock

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base
from app.database.session import SessionLocal
from app.scanner.models import OpportunitySnapshot
from app.scanner.models import OpportunityStage


class ScannerRepository:
    def upsert(self, snapshot: OpportunitySnapshot) -> OpportunitySnapshot:
        raise NotImplementedError

    def list(self) -> list[OpportunitySnapshot]:
        raise NotImplementedError

    def get(self, symbol: str, timeframe: str) -> OpportunitySnapshot | None:
        raise NotImplementedError


class ScannerSnapshotORM(Base):
    __tablename__ = "scanner_snapshots"

    symbol: Mapped[str] = mapped_column(String(64), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(16), primary_key=True)
    bias: Mapped[str] = mapped_column(String(32), nullable=False)
    structure: Mapped[str] = mapped_column(String(255), nullable=False)
    liquidity_target: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    institutional_score: Mapped[float] = mapped_column(Float, nullable=False)
    execution_quality: Mapped[float] = mapped_column(Float, nullable=False)
    last_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    health: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False)


class InMemoryScannerRepository(ScannerRepository):
    def __init__(self):
        self._snapshots: dict[tuple[str, str], OpportunitySnapshot] = {}
        self._lock = RLock()

    def upsert(self, snapshot: OpportunitySnapshot) -> OpportunitySnapshot:
        key = (snapshot.symbol.upper(), snapshot.timeframe.upper())
        with self._lock:
            self._snapshots[key] = snapshot
            return snapshot

    def list(self) -> list[OpportunitySnapshot]:
        with self._lock:
            snapshots = list(self._snapshots.values())
            snapshots.sort(key=lambda item: (item.symbol, item.timeframe))
            return snapshots

    def get(self, symbol: str, timeframe: str) -> OpportunitySnapshot | None:
        key = (symbol.upper(), timeframe.upper())
        with self._lock:
            return self._snapshots.get(key)


class SqlAlchemyScannerRepository(ScannerRepository):
    def __init__(self, session_factory=None):
        self._session_factory = session_factory or SessionLocal

    def upsert(self, snapshot: OpportunitySnapshot) -> OpportunitySnapshot:
        with self._session_factory() as session:
            row = session.get(
                ScannerSnapshotORM,
                (snapshot.symbol.upper(), snapshot.timeframe.upper()),
            )
            if row is None:
                row = ScannerSnapshotORM(
                    symbol=snapshot.symbol.upper(),
                    timeframe=snapshot.timeframe.upper(),
                )
                session.add(row)

            row.bias = snapshot.bias
            row.structure = snapshot.structure
            row.liquidity_target = snapshot.liquidity_target
            row.stage = snapshot.stage.value if isinstance(snapshot.stage, OpportunityStage) else str(snapshot.stage)
            row.institutional_score = snapshot.institutional_score
            row.execution_quality = snapshot.execution_quality
            row.last_update = snapshot.last_update
            row.health = snapshot.health
            row.decision_summary = snapshot.decision_summary

            session.commit()
            session.refresh(row)
            return self._to_snapshot(row)

    def list(self) -> list[OpportunitySnapshot]:
        with self._session_factory() as session:
            rows = session.query(ScannerSnapshotORM).all()
            return [self._to_snapshot(row) for row in rows]

    def get(self, symbol: str, timeframe: str) -> OpportunitySnapshot | None:
        with self._session_factory() as session:
            row = session.get(ScannerSnapshotORM, (symbol.upper(), timeframe.upper()))
            return self._to_snapshot(row) if row is not None else None

    @staticmethod
    def _to_snapshot(row: ScannerSnapshotORM) -> OpportunitySnapshot:
        return OpportunitySnapshot(
            symbol=row.symbol,
            timeframe=row.timeframe,
            bias=row.bias,
            structure=row.structure,
            liquidity_target=row.liquidity_target,
            stage=OpportunityStage(row.stage),
            institutional_score=row.institutional_score,
            execution_quality=row.execution_quality,
            last_update=row.last_update,
            health=row.health,
            decision_summary=row.decision_summary,
        )
