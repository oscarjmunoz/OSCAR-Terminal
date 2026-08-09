from __future__ import annotations

from datetime import datetime

from app.opportunity.models import EstimatedEta
from app.opportunity.models import OpportunityPriority
from app.opportunity.models import OpportunityResult
from app.opportunity.models import OpportunityStage
from app.opportunity.models import RecommendedAction
from app.scanner.models import OpportunityStage as ScannerStage
from app.scanner.schemas import OpportunitySnapshotSchema

OPPORTUNITY_CONTEXT_WEIGHT = 30.0
OPPORTUNITY_LIQUIDITY_WEIGHT = 20.0
OPPORTUNITY_STRUCTURE_WEIGHT = 20.0
OPPORTUNITY_SESSION_WEIGHT = 10.0
OPPORTUNITY_CONFLUENCE_WEIGHT = 20.0

INSTITUTIONAL_HTF_BIAS_WEIGHT = 22.0
INSTITUTIONAL_LIQUIDITY_WEIGHT = 20.0
INSTITUTIONAL_MARKET_STRUCTURE_WEIGHT = 22.0
INSTITUTIONAL_ORDER_FLOW_WEIGHT = 18.0
INSTITUTIONAL_NARRATIVE_QUALITY_WEIGHT = 18.0

EXECUTION_RR_WEIGHT = 20.0
EXECUTION_SPREAD_WEIGHT = 20.0
EXECUTION_SL_SIZE_WEIGHT = 20.0
EXECUTION_RISK_PERCENT_WEIGHT = 20.0
EXECUTION_CONDITIONS_WEIGHT = 20.0


class OpportunityEngine:

    def evaluate(self, snapshot: OpportunitySnapshotSchema) -> OpportunityResult:
        stage = self._map_stage(snapshot)

        opportunity_score = self._opportunity_score(snapshot, stage)
        institutional_score = self._institutional_score(snapshot)
        execution_quality = self._execution_quality(snapshot, stage)

        recommended_action = self._recommended_action(stage, snapshot, opportunity_score)
        priority = self._priority(recommended_action, stage, opportunity_score, institutional_score, execution_quality)
        estimated_eta = self._estimated_eta(stage)

        return OpportunityResult(
            symbol=snapshot.symbol,
            timeframe=snapshot.timeframe,
            bias=snapshot.bias,
            structure=snapshot.structure,
            liquidity_target=snapshot.liquidity_target,
            current_stage=stage,
            opportunity_score=round(opportunity_score, 2),
            institutional_score=round(institutional_score, 2),
            execution_quality=round(execution_quality, 2),
            priority=priority,
            estimated_eta=estimated_eta,
            decision_summary=snapshot.decision_summary,
            recommended_action=recommended_action,
            last_update=snapshot.last_update,
        )

    def evaluate_many(self, snapshots: list[OpportunitySnapshotSchema]) -> list[OpportunityResult]:
        return [self.evaluate(item) for item in snapshots]

    def _opportunity_score(self, snapshot: OpportunitySnapshotSchema, stage: OpportunityStage) -> float:
        context_factor = 1.0 if snapshot.bias in {"BULLISH", "BEARISH"} else 0.35
        liquidity_factor = 1.0 if snapshot.liquidity_target != "MIXED_LIQUIDITY" else 0.45
        structure_factor = self._structure_factor(snapshot.structure)
        session_factor = self._session_factor(snapshot.last_update)
        confluence_factor = min(max((snapshot.institutional_score + snapshot.execution_quality) / 200.0, 0.0), 1.0)

        # Stage multiplier keeps score aligned with execution maturity.
        stage_factor = self._stage_opportunity_factor(stage)

        base = (
            context_factor * OPPORTUNITY_CONTEXT_WEIGHT
            + liquidity_factor * OPPORTUNITY_LIQUIDITY_WEIGHT
            + structure_factor * OPPORTUNITY_STRUCTURE_WEIGHT
            + session_factor * OPPORTUNITY_SESSION_WEIGHT
            + confluence_factor * OPPORTUNITY_CONFLUENCE_WEIGHT
        )

        return min(max(base * stage_factor, 0.0), 100.0)

    def _institutional_score(self, snapshot: OpportunitySnapshotSchema) -> float:
        htf_bias_factor = 1.0 if snapshot.bias in {"BULLISH", "BEARISH"} else 0.25
        liquidity_factor = 1.0 if snapshot.liquidity_target != "MIXED_LIQUIDITY" else 0.4
        structure_factor = self._structure_factor(snapshot.structure)
        order_flow_factor = 1.0 if snapshot.health == "GREEN" else 0.55 if snapshot.health == "YELLOW" else 0.25
        narrative_quality_factor = self._narrative_quality_factor(snapshot.decision_summary)

        score = (
            htf_bias_factor * INSTITUTIONAL_HTF_BIAS_WEIGHT
            + liquidity_factor * INSTITUTIONAL_LIQUIDITY_WEIGHT
            + structure_factor * INSTITUTIONAL_MARKET_STRUCTURE_WEIGHT
            + order_flow_factor * INSTITUTIONAL_ORDER_FLOW_WEIGHT
            + narrative_quality_factor * INSTITUTIONAL_NARRATIVE_QUALITY_WEIGHT
        )

        return min(max(score, 0.0), 100.0)

    def _execution_quality(self, snapshot: OpportunitySnapshotSchema, stage: OpportunityStage) -> float:
        rr_factor = self._stage_execution_rr_factor(stage)
        spread_factor = 1.0 if snapshot.health == "GREEN" else 0.6 if snapshot.health == "YELLOW" else 0.2
        sl_size_factor = self._structure_factor(snapshot.structure)
        risk_percent_factor = self._stage_risk_factor(stage)
        execution_conditions_factor = self._execution_conditions_factor(snapshot, stage)

        score = (
            rr_factor * EXECUTION_RR_WEIGHT
            + spread_factor * EXECUTION_SPREAD_WEIGHT
            + sl_size_factor * EXECUTION_SL_SIZE_WEIGHT
            + risk_percent_factor * EXECUTION_RISK_PERCENT_WEIGHT
            + execution_conditions_factor * EXECUTION_CONDITIONS_WEIGHT
        )

        return min(max(score, 0.0), 100.0)

    @staticmethod
    def _map_stage(snapshot: OpportunitySnapshotSchema) -> OpportunityStage:
        if snapshot.stage == ScannerStage.BUILDING_CONTEXT:
            return OpportunityStage.CONTEXT_BUILDING

        if snapshot.stage == ScannerStage.WAITING_LIQUIDITY:
            return OpportunityStage.WAITING_LIQUIDITY

        if snapshot.stage == ScannerStage.WAITING_SWEEP:
            return OpportunityStage.WAITING_SWEEP

        if snapshot.stage == ScannerStage.WAITING_MSS:
            return OpportunityStage.WAITING_MSS

        if snapshot.stage == ScannerStage.WAITING_DISPLACEMENT:
            return OpportunityStage.WAITING_DISPLACEMENT

        if snapshot.stage == ScannerStage.ENTRY_READY:
            if snapshot.health == "GREEN":
                return OpportunityStage.EXECUTION_WINDOW
            return OpportunityStage.WAITING_ENTRY_ZONE

        return OpportunityStage.TRADE_ACTIVE

    @staticmethod
    def _recommended_action(
        stage: OpportunityStage,
        snapshot: OpportunitySnapshotSchema,
        opportunity_score: float,
    ) -> RecommendedAction:
        if snapshot.health == "RED" or opportunity_score < 35:
            return RecommendedAction.IGNORE

        if stage == OpportunityStage.CONTEXT_BUILDING:
            return RecommendedAction.MONITOR

        if stage in {OpportunityStage.WAITING_LIQUIDITY, OpportunityStage.WAITING_SWEEP, OpportunityStage.WAITING_MSS}:
            return RecommendedAction.WATCH

        if stage in {OpportunityStage.WAITING_DISPLACEMENT, OpportunityStage.WAITING_ENTRY_ZONE}:
            return RecommendedAction.PREPARE

        if stage == OpportunityStage.EXECUTION_WINDOW:
            return RecommendedAction.READY

        return RecommendedAction.ACTIVE

    @staticmethod
    def _priority(
        action: RecommendedAction,
        stage: OpportunityStage,
        opportunity_score: float,
        institutional_score: float,
        execution_quality: float,
    ) -> OpportunityPriority:
        if action == RecommendedAction.IGNORE:
            return OpportunityPriority.IGNORE

        if stage == OpportunityStage.TRADE_ACTIVE:
            return OpportunityPriority.CRITICAL

        if action == RecommendedAction.READY and min(opportunity_score, institutional_score, execution_quality) >= 70:
            return OpportunityPriority.HIGH

        if min(opportunity_score, institutional_score) >= 60:
            return OpportunityPriority.MEDIUM

        return OpportunityPriority.LOW

    @staticmethod
    def _estimated_eta(stage: OpportunityStage) -> EstimatedEta:
        if stage in {OpportunityStage.EXECUTION_WINDOW, OpportunityStage.TRADE_ACTIVE}:
            return EstimatedEta.NOW

        if stage == OpportunityStage.WAITING_ENTRY_ZONE:
            return EstimatedEta.LESS_THAN_15_MIN

        if stage == OpportunityStage.WAITING_DISPLACEMENT:
            return EstimatedEta.MIN_15_30

        if stage == OpportunityStage.WAITING_MSS:
            return EstimatedEta.MIN_30_60

        if stage in {OpportunityStage.WAITING_SWEEP, OpportunityStage.WAITING_LIQUIDITY}:
            return EstimatedEta.GREATER_THAN_60

        return EstimatedEta.UNKNOWN

    @staticmethod
    def _structure_factor(structure: str) -> float:
        if not structure or structure == "UNKNOWN":
            return 0.2

        marker = structure.upper()
        points = 0.0
        points += 0.34 if "BOS=1" in marker else 0.0
        points += 0.33 if "CHOCH=1" in marker else 0.0
        points += 0.33 if "MSS=1" in marker else 0.0

        return min(max(points, 0.2), 1.0)

    @staticmethod
    def _narrative_quality_factor(summary: str) -> float:
        length = len(summary.strip())

        if length >= 120:
            return 1.0

        if length >= 70:
            return 0.75

        if length >= 35:
            return 0.5

        return 0.3

    @staticmethod
    def _session_factor(last_update: datetime) -> float:
        hour = last_update.hour

        if 6 <= hour <= 19:
            return 1.0

        if 20 <= hour <= 22 or 3 <= hour < 6:
            return 0.65

        return 0.4

    @staticmethod
    def _stage_opportunity_factor(stage: OpportunityStage) -> float:
        if stage == OpportunityStage.EXECUTION_WINDOW:
            return 1.0

        if stage == OpportunityStage.WAITING_ENTRY_ZONE:
            return 0.95

        if stage == OpportunityStage.WAITING_DISPLACEMENT:
            return 0.85

        if stage == OpportunityStage.WAITING_MSS:
            return 0.75

        if stage in {OpportunityStage.WAITING_SWEEP, OpportunityStage.WAITING_LIQUIDITY}:
            return 0.65

        if stage == OpportunityStage.TRADE_ACTIVE:
            return 1.0

        return 0.5

    @staticmethod
    def _stage_execution_rr_factor(stage: OpportunityStage) -> float:
        if stage == OpportunityStage.EXECUTION_WINDOW:
            return 1.0

        if stage == OpportunityStage.WAITING_ENTRY_ZONE:
            return 0.85

        if stage == OpportunityStage.WAITING_DISPLACEMENT:
            return 0.7

        if stage == OpportunityStage.WAITING_MSS:
            return 0.55

        if stage in {OpportunityStage.WAITING_SWEEP, OpportunityStage.WAITING_LIQUIDITY}:
            return 0.45

        if stage == OpportunityStage.TRADE_ACTIVE:
            return 1.0

        return 0.35

    @staticmethod
    def _stage_risk_factor(stage: OpportunityStage) -> float:
        if stage in {OpportunityStage.EXECUTION_WINDOW, OpportunityStage.TRADE_ACTIVE}:
            return 1.0

        if stage in {OpportunityStage.WAITING_ENTRY_ZONE, OpportunityStage.WAITING_DISPLACEMENT}:
            return 0.75

        if stage in {OpportunityStage.WAITING_MSS, OpportunityStage.WAITING_SWEEP}:
            return 0.6

        if stage == OpportunityStage.WAITING_LIQUIDITY:
            return 0.5

        return 0.3

    @staticmethod
    def _execution_conditions_factor(snapshot: OpportunitySnapshotSchema, stage: OpportunityStage) -> float:
        base = 1.0 if snapshot.health == "GREEN" else 0.6 if snapshot.health == "YELLOW" else 0.25

        if stage == OpportunityStage.EXECUTION_WINDOW:
            return min(base, 1.0)

        if stage == OpportunityStage.TRADE_ACTIVE:
            return min(base, 1.0)

        if stage == OpportunityStage.WAITING_ENTRY_ZONE:
            return min(base * 0.9, 1.0)

        return min(base * 0.75, 1.0)
