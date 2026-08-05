from __future__ import annotations

from collections import Counter
from statistics import mean

from app.analytics.models import AnalyticsSummary
from app.analytics.models import ConfluenceStats
from app.analytics.models import ConfluenceFrequency
from app.analytics.models import PlaybookStats
from app.analytics.models import RecommendationStats
from app.analytics.models import RiskStats
from app.analytics.models import SessionStats
from app.analytics.models import SymbolStats
from app.analytics.models import TimeframeStats
from app.journal.models import JournalEntry
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision
from app.journal.service import JournalService
from app.playbook.service import PlaybookService


class AnalyticsService:
    _SESSIONS = ("ASIA", "LONDON", "NEW_YORK")
    _TIMEFRAMES = ("M1", "M5", "M15", "H1", "H4")
    _RECOMMENDATIONS = (
        TraderDecision.FOLLOWED_OSCAR,
        TraderDecision.IGNORED_OSCAR,
        TraderDecision.WAITED,
        TraderDecision.CANCELLED,
    )

    def __init__(self, journal_service: JournalService, playbook_service: PlaybookService):
        self._journal_service = journal_service
        self._playbook_service = playbook_service

    def getSummary(self) -> AnalyticsSummary:
        entries = self._journal_service.listEntries()
        return self._summary_from_entries(entries)

    def getSessionStats(self) -> list[SessionStats]:
        entries = self._journal_service.listEntries()
        reports: list[SessionStats] = []

        for session in self._SESSIONS:
            scoped_entries = [entry for entry in entries if entry.session.strip().upper() == session]
            reports.append(
                SessionStats(
                    session=session,
                    trades=len(scoped_entries),
                    winRate=self._win_rate(scoped_entries),
                    averageRR=self._average_rr(scoped_entries),
                    averageDuration=self._average_duration(scoped_entries),
                )
            )

        return reports

    def getTimeframeStats(self) -> list[TimeframeStats]:
        entries = self._journal_service.listEntries()
        reports: list[TimeframeStats] = []

        for timeframe in self._TIMEFRAMES:
            scoped_entries = [entry for entry in entries if entry.timeframe.strip().upper() == timeframe]
            reports.append(
                TimeframeStats(
                    timeframe=timeframe,
                    trades=len(scoped_entries),
                    winRate=self._win_rate(scoped_entries),
                    averageRR=self._average_rr(scoped_entries),
                    averageDuration=self._average_duration(scoped_entries),
                )
            )

        return reports

    def getSymbolStats(self) -> list[SymbolStats]:
        entries = self._journal_service.listEntries()
        grouped: dict[str, list[JournalEntry]] = {}

        for entry in entries:
            symbol = entry.symbol.strip().upper()
            grouped.setdefault(symbol, []).append(entry)

        reports: list[SymbolStats] = []
        for symbol in sorted(grouped):
            scoped_entries = grouped[symbol]
            reports.append(
                SymbolStats(
                    symbol=symbol,
                    trades=len(scoped_entries),
                    winRate=self._win_rate(scoped_entries),
                    averageRR=self._average_rr(scoped_entries),
                    averageDuration=self._average_duration(scoped_entries),
                )
            )

        return reports

    def getPlaybookStats(self) -> list[PlaybookStats]:
        entries = self._journal_service.listEntries()
        reports: list[PlaybookStats] = []

        for setup in self._playbook_service.listSetups():
            scoped_entries = [
                entry
                for entry in entries
                if self._playbook_service._evaluate(setup, self._playbook_service._from_snapshot(entry.decisionSnapshot)).matched
            ]
            expectancy = self._expectancy_rr(scoped_entries)
            reports.append(
                PlaybookStats(
                    setupId=setup.id,
                    setupName=setup.name,
                    totalTrades=len(scoped_entries),
                    winRate=self._win_rate(scoped_entries),
                    averageRR=self._average_rr(scoped_entries),
                    expectancy=expectancy,
                )
            )

        return reports

    def getRecommendationStats(self) -> list[RecommendationStats]:
        entries = self._journal_service.listEntries()
        reports: list[RecommendationStats] = []

        for recommendation in self._RECOMMENDATIONS:
            scoped_entries = [entry for entry in entries if entry.traderDecision == recommendation]
            reports.append(
                RecommendationStats(
                    recommendation=recommendation.value,
                    trades=len(scoped_entries),
                    winRate=self._win_rate(scoped_entries),
                    averageRR=self._average_rr(scoped_entries),
                    profitFactor=self._profit_factor(scoped_entries),
                )
            )

        return reports

    def getConfluenceStats(self) -> ConfluenceStats:
        entries = self._journal_service.listEntries()
        winning = Counter()

        for entry in entries:
            detected_names = [item.name for item in entry.decisionSnapshot.confluences if item.detected]
            if entry.tradeOutcome == TradeOutcome.WIN:
                winning.update(detected_names)

        return ConfluenceStats(
            winningTrades=self._counter_to_rows(winning),
        )

    def getRiskStats(self) -> RiskStats:
        entries = self._journal_service.listEntries()
        ordered = sorted(entries, key=lambda item: item.createdAt)
        average_expected_rr = self._average_expected_rr(entries)
        average_realized_rr = self._average_rr(entries)

        return RiskStats(
            averageRisk=self._average_risk(entries),
            averageExpectedRR=average_expected_rr,
            averageRealizedRR=average_realized_rr,
            rrDelta=round(average_realized_rr - average_expected_rr, 2),
            maxDrawdown=self._max_drawdown(ordered),
            bestStreak=self._best_streak(ordered),
            worstStreak=self._worst_streak(ordered),
        )

    # Compatibility aliases to avoid breaking consumers during migration.
    def getPerformance(self) -> AnalyticsSummary:
        return self.getSummary()

    def getSessions(self) -> list[SessionStats]:
        return self.getSessionStats()

    def getTimeframes(self) -> list[TimeframeStats]:
        return self.getTimeframeStats()

    def getSetups(self) -> list[PlaybookStats]:
        return self.getPlaybookStats()

    def getRecommendations(self) -> list[RecommendationStats]:
        return self.getRecommendationStats()

    def getConfluences(self) -> ConfluenceStats:
        return self.getConfluenceStats()

    def getBehaviour(self) -> list[RecommendationStats]:
        return self.getRecommendationStats()

    @staticmethod
    def _summary_from_entries(entries: list[JournalEntry]) -> AnalyticsSummary:
        wins = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.WIN)
        losses = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.LOSS)
        break_even = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.BREAK_EVEN)
        cancelled = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.CANCELLED)
        average_profit, average_loss = AnalyticsService._average_profit_loss(entries)

        return AnalyticsSummary(
            totalTrades=len(entries),
            wins=wins,
            losses=losses,
            breakEven=break_even,
            cancelled=cancelled,
            winRate=AnalyticsService._ratio(wins, len(entries)),
            averageRR=AnalyticsService._average_rr(entries),
            averageProfit=average_profit,
            averageLoss=average_loss,
            expectancy=AnalyticsService._expectancy(entries),
            profitFactor=AnalyticsService._profit_factor(entries),
        )

    @staticmethod
    def _average_rr(entries: list[JournalEntry]) -> float:
        rr_values = [entry.realizedRR for entry in entries if entry.realizedRR is not None]
        return round(mean(rr_values), 2) if rr_values else 0.0

    @staticmethod
    def _average_duration(entries: list[JournalEntry]) -> float:
        durations = [entry.durationMinutes for entry in entries if entry.durationMinutes is not None]
        return round(mean(durations), 2) if durations else 0.0

    @staticmethod
    def _average_risk(entries: list[JournalEntry]) -> float:
        risk_values = [entry.riskPercent for entry in entries]
        return round(mean(risk_values), 2) if risk_values else 0.0

    @staticmethod
    def _average_expected_rr(entries: list[JournalEntry]) -> float:
        expected_values = [entry.expectedRR for entry in entries]
        return round(mean(expected_values), 2) if expected_values else 0.0

    @staticmethod
    def _average_profit_loss(entries: list[JournalEntry]) -> tuple[float, float]:
        values = [AnalyticsService._result_value(entry) for entry in entries]
        profits = [value for value in values if value > 0]
        losses = [value for value in values if value < 0]

        average_profit = round(mean(profits), 2) if profits else 0.0
        average_loss = round(abs(mean(losses)), 2) if losses else 0.0
        return average_profit, average_loss

    @staticmethod
    def _expectancy(entries: list[JournalEntry]) -> float:
        average_profit, average_loss = AnalyticsService._average_profit_loss(entries)
        wins = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.WIN)
        losses = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.LOSS)
        total = len(entries)

        if total == 0:
            return 0.0

        win_probability = wins / total
        loss_probability = losses / total
        expectancy = (win_probability * average_profit) - (loss_probability * average_loss)
        return round(expectancy, 2)

    @staticmethod
    def _expectancy_rr(entries: list[JournalEntry]) -> float:
        wins = [entry.realizedRR for entry in entries if entry.tradeOutcome == TradeOutcome.WIN and entry.realizedRR is not None]
        losses = [entry.realizedRR for entry in entries if entry.tradeOutcome == TradeOutcome.LOSS and entry.realizedRR is not None]
        total = len(entries)

        if total == 0:
            return 0.0

        avg_win = mean(wins) if wins else 0.0
        avg_loss = abs(mean(losses)) if losses else 0.0
        win_probability = len(wins) / total
        loss_probability = len(losses) / total
        expectancy = (win_probability * avg_win) - (loss_probability * avg_loss)
        return round(expectancy, 2)

    @staticmethod
    def _profit_factor(entries: list[JournalEntry]) -> float:
        values = [AnalyticsService._result_value(entry) for entry in entries]
        gross_profit = sum(value for value in values if value > 0)
        gross_loss = abs(sum(value for value in values if value < 0))

        if gross_profit == 0:
            return 0.0
        if gross_loss == 0:
            return round(gross_profit, 2)
        return round(gross_profit / gross_loss, 2)

    @staticmethod
    def _result_value(entry: JournalEntry) -> float:
        if entry.profitLoss is not None:
            return entry.profitLoss
        if entry.realizedRR is not None:
            return entry.realizedRR
        return 0.0

    @staticmethod
    def _win_rate(entries: list[JournalEntry]) -> float:
        wins = sum(1 for entry in entries if entry.tradeOutcome == TradeOutcome.WIN)
        return AnalyticsService._ratio(wins, len(entries))

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        return round((numerator / denominator) * 100, 2) if denominator else 0.0

    @staticmethod
    def _counter_to_rows(counter: Counter[str]) -> list[ConfluenceFrequency]:
        ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0].lower()))
        return [ConfluenceFrequency(name=name, frequency=frequency) for name, frequency in ordered]

    @staticmethod
    def _max_drawdown(entries: list[JournalEntry]) -> float:
        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0

        for entry in entries:
            if entry.realizedRR is None:
                continue
            equity += entry.realizedRR
            peak = max(peak, equity)
            max_drawdown = max(max_drawdown, peak - equity)

        return round(max_drawdown, 2)

    @staticmethod
    def _best_streak(entries: list[JournalEntry]) -> int:
        current = 0
        best = 0

        for entry in entries:
            if entry.tradeOutcome == TradeOutcome.WIN:
                current += 1
                best = max(best, current)
            else:
                current = 0

        return best

    @staticmethod
    def _worst_streak(entries: list[JournalEntry]) -> int:
        current = 0
        worst = 0

        for entry in entries:
            if entry.tradeOutcome == TradeOutcome.LOSS:
                current += 1
                worst = max(worst, current)
            else:
                current = 0

        return worst