from __future__ import annotations

from collections.abc import Iterable
from threading import RLock
from typing import Protocol

from app.journal.models import JournalEntry


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
