from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from statistics import mean

from app.journal.models import JournalDecisionSnapshot
from app.journal.models import JournalEntry
from app.journal.models import TradeOutcome
from app.journal.service import JournalService
from app.playbook.models import PlaybookEvaluationRequest
from app.playbook.models import PlaybookInstitutionalZonesCondition
from app.playbook.models import PlaybookLiquidityCondition
from app.playbook.models import PlaybookMatch
from app.playbook.models import PlaybookSetup
from app.playbook.models import PlaybookSetupConditions
from app.playbook.models import PlaybookSetupConditionsUpdate
from app.playbook.models import PlaybookSetupCreate
from app.playbook.models import PlaybookSetupStatistics
from app.playbook.models import PlaybookSetupUpdate
from app.playbook.models import PlaybookStructureCondition
from app.playbook.repository import InMemoryPlaybookRepository
from app.playbook.repository import PlaybookRepository
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import MarketBias
from app.schemas.decision_center import RecommendationType


@dataclass(slots=True)
class _DecisionInput:
    bias: MarketBias
    score: int
    confidence: float
    liquidity: object
    structure: object
    zones: object
    confluences: list[object]
    recommendation: RecommendationType


class PlaybookNotFoundError(KeyError):
    def __init__(self, setup_id: str):
        super().__init__(setup_id)
        self.setup_id = setup_id


class PlaybookService:
    def __init__(self, repository: PlaybookRepository | None = None, journal_service: JournalService | None = None):
        self._repository = repository or InMemoryPlaybookRepository()
        self._journal_service = journal_service or JournalService()

    def createSetup(self, payload: PlaybookSetupCreate) -> PlaybookSetup:
        setup = PlaybookSetup(
            name=payload.name,
            description=payload.description,
            category=payload.category,
            enabled=payload.enabled,
            conditions=payload.conditions,
        )
        return self._repository.add(setup)

    def updateSetup(self, setup_id: str, payload: PlaybookSetupUpdate) -> PlaybookSetup:
        setup = self.getSetup(setup_id)
        update_data: dict[str, object] = {}

        if payload.name is not None:
            update_data["name"] = payload.name
        if payload.description is not None:
            update_data["description"] = payload.description
        if payload.category is not None:
            update_data["category"] = payload.category
        if payload.enabled is not None:
            update_data["enabled"] = payload.enabled
        if payload.conditions is not None:
            update_data["conditions"] = self._merge_conditions(setup.conditions, payload.conditions)

        if update_data:
            update_data["updatedAt"] = self._utc_now()

        return self._repository.update(setup.model_copy(update=update_data))

    def deleteSetup(self, setup_id: str) -> PlaybookSetup:
        deleted = self._repository.delete(setup_id)
        if deleted is None:
            raise PlaybookNotFoundError(setup_id)
        return deleted

    def getSetup(self, setup_id: str) -> PlaybookSetup:
        setup = self._repository.get(setup_id)
        if setup is None:
            raise PlaybookNotFoundError(setup_id)
        return setup

    def listSetups(self) -> list[PlaybookSetup]:
        return self._repository.list()

    def evaluate(self, request: PlaybookEvaluationRequest) -> PlaybookMatch | list[PlaybookMatch]:
        if request.setupId is not None:
            return self.evaluateSetup(request.setupId, request.decisionReport)
        return self.evaluateAll(request.decisionReport)

    def evaluateSetup(self, setup_id: str, report: DecisionReport) -> PlaybookMatch:
        setup = self.getSetup(setup_id)
        return self._evaluate(setup, self._from_report(report))

    def evaluateAll(self, report: DecisionReport) -> list[PlaybookMatch]:
        decision = self._from_report(report)
        return [self._evaluate(setup, decision) for setup in self.listSetups()]

    def getStatistics(self) -> list[PlaybookSetupStatistics]:
        entries = self._journal_service.listEntries()
        statistics: list[PlaybookSetupStatistics] = []

        for setup in self.listSetups():
            matched_entries = [entry for entry in entries if self._matches_entry(setup, entry)]
            closed_entries = [entry for entry in matched_entries if entry.tradeOutcome != TradeOutcome.PENDING]

            wins = sum(1 for entry in closed_entries if entry.tradeOutcome == TradeOutcome.WIN)
            losses = sum(1 for entry in closed_entries if entry.tradeOutcome == TradeOutcome.LOSS)
            break_even = sum(1 for entry in closed_entries if entry.tradeOutcome == TradeOutcome.BREAK_EVEN)
            cancelled = sum(1 for entry in closed_entries if entry.tradeOutcome == TradeOutcome.CANCELLED)
            total_trades = len(matched_entries)
            realized_rr_values = [entry.realizedRR for entry in matched_entries if entry.realizedRR is not None]
            duration_values = [entry.durationMinutes for entry in matched_entries if entry.durationMinutes is not None]

            statistics.append(
                PlaybookSetupStatistics(
                    setupId=setup.id,
                    setupName=setup.name,
                    totalTrades=total_trades,
                    wins=wins,
                    losses=losses,
                    breakEven=break_even,
                    cancelled=cancelled,
                    winRate=round((wins / total_trades) * 100, 2) if total_trades else 0.0,
                    averageRR=round(mean(realized_rr_values), 2) if realized_rr_values else 0.0,
                    averageDuration=round(mean(duration_values), 2) if duration_values else 0.0,
                )
            )

        return statistics

    def _evaluate(self, setup: PlaybookSetup, decision: _DecisionInput) -> PlaybookMatch:
        if not setup.enabled:
            return PlaybookMatch(
                setupId=setup.id,
                setupName=setup.name,
                matched=False,
                matchPercentage=0,
                matchedConditions=[],
                missingConditions=["Setup disabled"],
                explanation="Setup disabled",
            )

        matched_conditions: list[str] = []
        missing_conditions: list[str] = []
        checks = self._build_checks(setup.conditions, decision)

        for matched, label in checks:
            if matched:
                matched_conditions.append(label)
            else:
                missing_conditions.append(label)

        total_conditions = len(checks)
        matched_count = len(matched_conditions)
        match_percentage = 100 if total_conditions == 0 else round((matched_count / total_conditions) * 100)
        matched = total_conditions == 0 or matched_count == total_conditions

        if total_conditions == 0:
            explanation = f"{setup.name}: no conditions defined; automatic match"
        elif missing_conditions:
            explanation = f"{setup.name}: matched {match_percentage}% - missing {', '.join(missing_conditions)}"
        else:
            explanation = f"{setup.name}: fully matched with {match_percentage}% coverage"

        return PlaybookMatch(
            setupId=setup.id,
            setupName=setup.name,
            matched=matched,
            matchPercentage=match_percentage,
            matchedConditions=matched_conditions,
            missingConditions=missing_conditions,
            explanation=explanation,
        )

    def _build_checks(self, conditions: PlaybookSetupConditions, decision: _DecisionInput) -> list[tuple[bool, str]]:
        checks: list[tuple[bool, str]] = []

        if conditions.bias is not None:
            checks.append((decision.bias == conditions.bias, f"Bias == {conditions.bias.value}"))
        if conditions.minimumInstitutionalScore is not None:
            checks.append((decision.score >= conditions.minimumInstitutionalScore, f"Institutional score >= {conditions.minimumInstitutionalScore}"))
        if conditions.minimumConfidence is not None:
            checks.append((decision.confidence >= conditions.minimumConfidence, f"Confidence >= {conditions.minimumConfidence}"))

        checks.extend(self._build_liquidity_checks(conditions.liquidity, decision))
        checks.extend(self._build_structure_checks(conditions.structure, decision))
        checks.extend(self._build_zone_checks(conditions.institutionalZones, decision))

        for required in conditions.requiredConfluences:
            found = any(
                getattr(confluence, "detected", False) and getattr(confluence, "name", "").strip().lower() == required.strip().lower()
                for confluence in decision.confluences
            )
            checks.append((found, f"Confluence detected: {required}"))

        if conditions.allowedRecommendations:
            allowed = {item for item in conditions.allowedRecommendations}
            checks.append((decision.recommendation in allowed, f"Recommendation in {[item.value for item in conditions.allowedRecommendations]}"))

        return checks

    def _build_liquidity_checks(self, conditions: PlaybookLiquidityCondition, decision: _DecisionInput) -> list[tuple[bool, str]]:
        checks: list[tuple[bool, str]] = []
        if conditions.minBuyLiquidity is not None:
            checks.append((decision.liquidity.buy_liquidity >= conditions.minBuyLiquidity, f"Buy liquidity >= {conditions.minBuyLiquidity}"))
        if conditions.minSellLiquidity is not None:
            checks.append((decision.liquidity.sell_liquidity >= conditions.minSellLiquidity, f"Sell liquidity >= {conditions.minSellLiquidity}"))
        if conditions.minLiquidityTaken is not None:
            checks.append((decision.liquidity.liquidity_taken >= conditions.minLiquidityTaken, f"Liquidity taken >= {conditions.minLiquidityTaken}"))
        if conditions.minPendingLiquidity is not None:
            checks.append((decision.liquidity.pending_liquidity >= conditions.minPendingLiquidity, f"Pending liquidity >= {conditions.minPendingLiquidity}"))
        return checks

    def _build_structure_checks(self, conditions: PlaybookStructureCondition, decision: _DecisionInput) -> list[tuple[bool, str]]:
        checks: list[tuple[bool, str]] = []
        if conditions.trend is not None:
            checks.append((decision.structure.trend.strip().upper() == conditions.trend.strip().upper(), f"Trend == {conditions.trend}"))
        if conditions.bos is not None:
            checks.append((decision.structure.bos == conditions.bos, f"BOS == {conditions.bos}"))
        if conditions.choch is not None:
            checks.append((decision.structure.choch == conditions.choch, f"CHOCH == {conditions.choch}"))
        if conditions.mss is not None:
            checks.append((decision.structure.mss == conditions.mss, f"MSS == {conditions.mss}"))
        return checks

    def _build_zone_checks(self, conditions: PlaybookInstitutionalZonesCondition, decision: _DecisionInput) -> list[tuple[bool, str]]:
        checks: list[tuple[bool, str]] = []
        zone_map = {
            "orderBlock": decision.zones.order_block.active,
            "breaker": decision.zones.breaker.active,
            "mitigation": decision.zones.mitigation.active,
            "fvg": decision.zones.fvg.active,
            "premium": decision.zones.premium.active,
            "discount": decision.zones.discount.active,
        }
        for key, expected in conditions.model_dump(exclude_unset=True).items():
            if expected is None:
                continue
            checks.append((zone_map[key] == expected, f"{key} == {expected}"))
        return checks

    def _matches_entry(self, setup: PlaybookSetup, entry: JournalEntry) -> bool:
        return self._evaluate(setup, self._from_snapshot(entry.decisionSnapshot)).matched

    @staticmethod
    def _from_report(report: DecisionReport) -> _DecisionInput:
        return _DecisionInput(
            bias=report.market_bias.bias,
            score=report.institutional_score.score,
            confidence=report.institutional_score.confidence,
            liquidity=report.liquidity,
            structure=report.market_structure,
            zones=report.institutional_zones,
            confluences=list(report.confluences),
            recommendation=report.final_recommendation.recommendation,
        )

    @staticmethod
    def _from_snapshot(snapshot: JournalDecisionSnapshot) -> _DecisionInput:
        return _DecisionInput(
            bias=snapshot.bias.bias,
            score=snapshot.score,
            confidence=snapshot.confidence,
            liquidity=snapshot.liquidity,
            structure=snapshot.structure,
            zones=snapshot.zones,
            confluences=list(snapshot.confluences),
            recommendation=snapshot.recommendation.recommendation,
        )

    @staticmethod
    def _merge_conditions(current: PlaybookSetupConditions, update: PlaybookSetupConditionsUpdate) -> PlaybookSetupConditions:
        payload = current.model_dump()
        update_data = update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is None:
                continue
            payload[key] = value

        return PlaybookSetupConditions(**payload)

    @staticmethod
    def _utc_now():
        from datetime import datetime, timezone

        return datetime.now(timezone.utc)
