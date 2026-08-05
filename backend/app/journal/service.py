from __future__ import annotations

from collections.abc import Iterable

from app.journal.models import JournalDecisionSnapshot
from app.journal.models import JournalEntry
from app.journal.models import JournalEntryCreate
from app.journal.models import JournalFilterCriteria
from app.journal.models import JournalOutcomeUpdate
from app.journal.models import TradeOutcome
from app.journal.repository import InMemoryJournalRepository
from app.journal.repository import JournalRepository


class JournalNotFoundError(KeyError):
    def __init__(self, entry_id: str):
        super().__init__(entry_id)
        self.entry_id = entry_id


class JournalService:
    def __init__(self, repository: JournalRepository | None = None):
        self._repository = repository or InMemoryJournalRepository()

    def createEntry(self, payload: JournalEntryCreate) -> JournalEntry:
        entry = JournalEntry(
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
        return self._repository.add(entry)

    def updateOutcome(self, entry_id: str, payload: JournalOutcomeUpdate) -> JournalEntry:
        entry = self.getEntry(entry_id)

        updated = entry.model_copy(
            update={
                "traderDecision": payload.traderDecision if payload.traderDecision is not None else entry.traderDecision,
                "tradeOutcome": payload.tradeOutcome if payload.tradeOutcome is not None else entry.tradeOutcome,
                "profitLoss": payload.profitLoss if payload.profitLoss is not None else entry.profitLoss,
                "realizedRR": payload.realizedRR if payload.realizedRR is not None else entry.realizedRR,
                "durationMinutes": payload.durationMinutes if payload.durationMinutes is not None else entry.durationMinutes,
                "closeReason": payload.closeReason if payload.closeReason is not None else entry.closeReason,
                "personalNotes": payload.personalNotes if payload.personalNotes is not None else entry.personalNotes,
                "tags": list(payload.tags) if payload.tags is not None else list(entry.tags),
            }
        )
        return self._repository.update(updated)

    def listEntries(
        self,
        filters: JournalFilterCriteria | None = None,
        query: str | None = None,
    ) -> list[JournalEntry]:
        entries = self._repository.list()

        if filters is not None:
            entries = self.filter(filters, entries)

        if query:
            entries = self.search(query, entries)

        return sorted(entries, key=lambda entry: entry.createdAt, reverse=True)

    def getEntry(self, entry_id: str) -> JournalEntry:
        entry = self._repository.get(entry_id)
        if entry is None:
            raise JournalNotFoundError(entry_id)
        return entry

    def deleteEntry(self, entry_id: str) -> JournalEntry:
        deleted = self._repository.delete(entry_id)
        if deleted is None:
            raise JournalNotFoundError(entry_id)
        return deleted

    def search(self, query: str, entries: Iterable[JournalEntry] | None = None) -> list[JournalEntry]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return list(entries) if entries is not None else self._repository.list()

        pool = list(entries) if entries is not None else self._repository.list()
        return [entry for entry in pool if normalized_query in self._entry_text(entry)]

    def filter(
        self,
        criteria: JournalFilterCriteria,
        entries: Iterable[JournalEntry] | None = None,
    ) -> list[JournalEntry]:
        pool = list(entries) if entries is not None else self._repository.list()

        def matches(entry: JournalEntry) -> bool:
            if criteria.symbol is not None and entry.symbol.lower() != criteria.symbol.lower():
                return False
            if criteria.timeframe is not None and entry.timeframe.lower() != criteria.timeframe.lower():
                return False
            if criteria.session is not None and entry.session.lower() != criteria.session.lower():
                return False
            if criteria.traderDecision is not None and entry.traderDecision != criteria.traderDecision:
                return False
            if criteria.tradeOutcome is not None and entry.tradeOutcome != criteria.tradeOutcome:
                return False
            if criteria.tag is not None and criteria.tag.lower() not in {tag.lower() for tag in entry.tags}:
                return False
            if criteria.createdAfter is not None and entry.createdAt < criteria.createdAfter:
                return False
            if criteria.createdBefore is not None and entry.createdAt > criteria.createdBefore:
                return False
            if criteria.minExpectedRR is not None and entry.expectedRR < criteria.minExpectedRR:
                return False
            if criteria.maxExpectedRR is not None and entry.expectedRR > criteria.maxExpectedRR:
                return False
            return True

        return [entry for entry in pool if matches(entry)]

    @staticmethod
    def _entry_text(entry: JournalEntry) -> str:
        parts = [
            entry.id,
            entry.symbol,
            entry.timeframe,
            entry.session,
            entry.traderDecision.value,
            entry.tradeOutcome.value,
            entry.personalNotes,
            entry.closeReason or "",
            " ".join(entry.tags),
            entry.decisionSnapshot.bias.bias.value,
            entry.decisionSnapshot.bias.explanation,
            entry.decisionSnapshot.structure.explanation,
            entry.decisionSnapshot.liquidity.explanation,
            entry.decisionSnapshot.zones.order_block.explanation,
            entry.decisionSnapshot.zones.breaker.explanation,
            entry.decisionSnapshot.zones.mitigation.explanation,
            entry.decisionSnapshot.zones.fvg.explanation,
            entry.decisionSnapshot.zones.premium.explanation,
            entry.decisionSnapshot.zones.discount.explanation,
            entry.decisionSnapshot.recommendation.recommendation.value,
            entry.decisionSnapshot.recommendation.explanation,
            entry.decisionSnapshot.narrative,
        ]

        parts.extend(item.name for item in entry.decisionSnapshot.confluences)
        parts.extend(item.explanation for item in entry.decisionSnapshot.confluences)
        parts.extend(item.label for item in entry.decisionSnapshot.checklist)
        parts.extend(item.explanation for item in entry.decisionSnapshot.checklist)

        return " ".join(part.lower() for part in parts if part)
