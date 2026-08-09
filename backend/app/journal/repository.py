from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from threading import RLock
from typing import Protocol

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base
from app.database.session import SessionLocal
from app.journal.models import JournalDecisionSnapshot
from app.journal.models import JournalEntry
from app.journal.models import JournalEntryCreate
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision


class JournalRepository(Protocol):
    def add(self, entry: JournalEntry) -> JournalEntry:
        ...

    def get(self, entry_id: str) -> JournalEntry | None:
        ...

    def list(self) -> list[JournalEntry]:
        ...

    def update(self, entry: JournalEntry) -> JournalEntry:
        ...

    def delete(self, entry_id: str) -> JournalEntry | None:
        ...

    def clear(self) -> None:
        ...


class JournalEntryORM(Base):
    __tablename__ = "journal_entries"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    session: Mapped[str] = mapped_column(String(64), nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    position_size: Mapped[float] = mapped_column(Float, nullable=False)
    risk_percent: Mapped[float] = mapped_column(Float, nullable=False)
    expected_rr: Mapped[float] = mapped_column(Float, nullable=False)
    decision_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    trader_decision: Mapped[str] = mapped_column(String(32), nullable=False)
    trade_outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    profit_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    realized_rr: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    close_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    personal_notes: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False)


class InMemoryJournalRepository:
    def __init__(self):
        self._entries: dict[str, JournalEntry] = {}
        self._lock = RLock()

    def add(self, entry: JournalEntry) -> JournalEntry:
        with self._lock:
            stored = entry.model_copy(deep=True)
            self._entries[stored.id] = stored
            return stored.model_copy(deep=True)

    def get(self, entry_id: str) -> JournalEntry | None:
        with self._lock:
            entry = self._entries.get(entry_id)
            return entry.model_copy(deep=True) if entry is not None else None

    def list(self) -> list[JournalEntry]:
        with self._lock:
            return [entry.model_copy(deep=True) for entry in self._entries.values()]

    def update(self, entry: JournalEntry) -> JournalEntry:
        with self._lock:
            if entry.id not in self._entries:
                raise KeyError(entry.id)

            stored = entry.model_copy(deep=True)
            self._entries[stored.id] = stored
            return stored.model_copy(deep=True)

    def delete(self, entry_id: str) -> JournalEntry | None:
        with self._lock:
            entry = self._entries.pop(entry_id, None)
            return entry.model_copy(deep=True) if entry is not None else None

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


class SqlAlchemyJournalRepository(JournalRepository):
    def __init__(self, session_factory=None):
        self._session_factory = session_factory or SessionLocal

    def add(self, entry: JournalEntry) -> JournalEntry:
        row = self._to_row(entry)
        with self._session_factory() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_entry(row)

    def get(self, entry_id: str) -> JournalEntry | None:
        with self._session_factory() as session:
            row = session.get(JournalEntryORM, entry_id)
            return self._to_entry(row) if row is not None else None

    def list(self) -> list[JournalEntry]:
        with self._session_factory() as session:
            rows = session.query(JournalEntryORM).order_by(JournalEntryORM.created_at.desc()).all()
            return [self._to_entry(row) for row in rows]

    def update(self, entry: JournalEntry) -> JournalEntry:
        with self._session_factory() as session:
            row = session.get(JournalEntryORM, entry.id)
            if row is None:
                raise KeyError(entry.id)

            row.created_at = entry.createdAt
            row.symbol = entry.symbol
            row.timeframe = entry.timeframe
            row.session = entry.session
            row.entry_price = entry.entryPrice
            row.stop_loss = entry.stopLoss
            row.take_profit = entry.takeProfit
            row.position_size = entry.positionSize
            row.risk_percent = entry.riskPercent
            row.expected_rr = entry.expectedRR
            row.decision_snapshot = json.dumps(entry.decisionSnapshot.model_dump(mode="json"))
            row.trader_decision = entry.traderDecision.value
            row.trade_outcome = entry.tradeOutcome.value
            row.profit_loss = entry.profitLoss
            row.realized_rr = entry.realizedRR
            row.duration_minutes = entry.durationMinutes
            row.close_reason = entry.closeReason
            row.personal_notes = entry.personalNotes
            row.tags = json.dumps(entry.tags)

            session.commit()
            session.refresh(row)
            return self._to_entry(row)

    def delete(self, entry_id: str) -> JournalEntry | None:
        with self._session_factory() as session:
            row = session.get(JournalEntryORM, entry_id)
            if row is None:
                return None
            deleted = self._to_entry(row)
            session.delete(row)
            session.commit()
            return deleted

    def clear(self) -> None:
        with self._session_factory() as session:
            session.query(JournalEntryORM).delete()
            session.commit()

    def _to_entry(self, row: JournalEntryORM | None) -> JournalEntry | None:
        if row is None:
            return None

        data = json.loads(row.decision_snapshot)
        return JournalEntry(
            id=row.id,
            createdAt=row.created_at,
            symbol=row.symbol,
            timeframe=row.timeframe,
            session=row.session,
            entryPrice=row.entry_price,
            stopLoss=row.stop_loss,
            takeProfit=row.take_profit,
            positionSize=row.position_size,
            riskPercent=row.risk_percent,
            expectedRR=row.expected_rr,
            decisionSnapshot=JournalDecisionSnapshot.model_validate(data),
            traderDecision=TraderDecision(row.trader_decision),
            tradeOutcome=TradeOutcome(row.trade_outcome),
            profitLoss=row.profit_loss,
            realizedRR=row.realized_rr,
            durationMinutes=row.duration_minutes,
            closeReason=row.close_reason,
            personalNotes=row.personal_notes,
            tags=json.loads(row.tags) if row.tags else [],
        )

    def _to_row(self, entry: JournalEntry) -> JournalEntryORM:
        return JournalEntryORM(
            id=entry.id,
            created_at=entry.createdAt,
            symbol=entry.symbol,
            timeframe=entry.timeframe,
            session=entry.session,
            entry_price=entry.entryPrice,
            stop_loss=entry.stopLoss,
            take_profit=entry.takeProfit,
            position_size=entry.positionSize,
            risk_percent=entry.riskPercent,
            expected_rr=entry.expectedRR,
            decision_snapshot=json.dumps(entry.decisionSnapshot.model_dump(mode="json")),
            trader_decision=entry.traderDecision.value,
            trade_outcome=entry.tradeOutcome.value,
            profit_loss=entry.profitLoss,
            realized_rr=entry.realizedRR,
            duration_minutes=entry.durationMinutes,
            close_reason=entry.closeReason,
            personal_notes=entry.personalNotes,
            tags=json.dumps(entry.tags),
        )

    def _to_entry_from_payload(self, payload: JournalEntryCreate) -> JournalEntry:
        return JournalEntry(
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            session=payload.session,
            entryPrice=payload.entryPrice,
            stopLoss=payload.stopLoss,
            takeProfit=payload.takeProfit,
            positionSize=payload.positionSize,
            riskPercent=payload.riskPercent,
            expectedRR=payload.expectedRR,
            decisionSnapshot=JournalDecisionSnapshot.from_report(payload.decisionReport),
            traderDecision=payload.traderDecision,
            personalNotes=payload.personalNotes,
            tags=list(payload.tags),
        )
