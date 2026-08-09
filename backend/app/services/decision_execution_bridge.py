from __future__ import annotations

from app.config.settings import settings
from app.execution.schemas import ExecutionRequest
from app.execution.schemas import ExecutionStatus
from app.execution.schemas import TradeSide as ExecutionTradeSide
from app.execution.service import ExecutionService
from app.journal.models import JournalEntryCreate
from app.journal.models import TraderDecision
from app.journal.service import JournalService
from app.playbook.service import PlaybookService
from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide as DecisionTradeSide
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_center import RecommendationType
from app.schemas.decision_execution_bridge import BridgeAction
from app.schemas.decision_execution_bridge import BridgeDecisionPayload
from app.schemas.decision_execution_bridge import DecisionExecutionBridgeRequest
from app.schemas.decision_execution_bridge import DecisionExecutionBridgeResult
from app.schemas.decision_execution_bridge import DecisionSource
from app.schemas.decision_execution_bridge import DispatchStatus
from app.schemas.decision_execution_bridge import DispatchSummary
from app.schemas.decision_execution_bridge import ExecutionMode
from app.schemas.decision_execution_bridge import ExecutionPreparationSummary
from app.schemas.decision_execution_bridge import PlaybookEvaluationSummary
from app.schemas.decision_execution_bridge import SafetyGateSummary
from app.services.decision_center import DecisionCenter
from app.services.paper_execution_service import PaperExecutionService
from app.services.trade_executor import TradeExecutor


class DecisionExecutionBridge:
    def __init__(
        self,
        playbook_service: PlaybookService | None = None,
        journal_service: JournalService | None = None,
        trade_executor: TradeExecutor | None = None,
        paper_execution_service: PaperExecutionService | None = None,
        dispatch_enabled: bool | None = None,
    ):
        self._playbook_service = playbook_service or PlaybookService()
        self._journal_service = journal_service or JournalService()
        self._trade_executor = trade_executor or TradeExecutor()
        self._paper_execution_service = paper_execution_service or PaperExecutionService()
        self._dispatch_enabled = settings.DECISION_EXECUTION_DISPATCH_ENABLED if dispatch_enabled is None else dispatch_enabled

    def execute(self, payload: DecisionExecutionBridgeRequest) -> DecisionExecutionBridgeResult:
        report, source = self._resolve_report(payload)
        execution_mode = payload.executionMode
        playbook_result = self._evaluate_playbooks(report)
        preparation = self._prepare_execution(report, payload, execution_mode)
        safety_gate = self._build_safety_gate(report, playbook_result, preparation, payload, execution_mode)
        execution_boundary = self._dispatch_if_allowed(report, preparation, safety_gate, payload, execution_mode)

        final_action = execution_boundary.status == DispatchStatus.SUCCESS and BridgeAction.DISPATCH or safety_gate.action
        final_status = self._final_status(final_action, execution_boundary)

        return DecisionExecutionBridgeResult(
            decision=BridgeDecisionPayload(source=source, report=report),
            playbookResult=playbook_result,
            executionPreparation=preparation,
            safetyGate=safety_gate,
            executionBoundary=execution_boundary,
            finalAction=final_action,
            finalStatus=final_status,
        )

    def _resolve_report(self, payload: DecisionExecutionBridgeRequest) -> tuple[DecisionReport, DecisionSource]:
        if payload.decisionReport is not None:
            return payload.decisionReport, DecisionSource.REPORT

        assert payload.decisionContext is not None
        return DecisionCenter.build_report(payload.decisionContext), DecisionSource.CONTEXT

    def _evaluate_playbooks(self, report: DecisionReport) -> PlaybookEvaluationSummary:
        matches = self._playbook_service.evaluateAll(report)
        matched_playbooks = [match for match in matches if match.matched]
        best_match = max(matches, key=lambda match: match.matchPercentage) if matches else None
        reasons: list[str] = []

        if not matches:
            reasons.append("No playbooks configured")
        elif not matched_playbooks:
            reasons.append("No playbook fully matched the decision report")

        permits_continuation = bool(matched_playbooks)

        return PlaybookEvaluationSummary(
            totalPlaybooks=len(matches),
            matches=matches,
            matchedPlaybooks=matched_playbooks,
            bestMatch=best_match,
            bestMatchScore=best_match.matchPercentage if best_match is not None else 0,
            requirementsSatisfied=permits_continuation,
            permitsContinuation=permits_continuation,
            reasons=reasons,
        )

    def _prepare_execution(
        self,
        report: DecisionReport,
        payload: DecisionExecutionBridgeRequest,
        execution_mode: ExecutionMode,
    ) -> ExecutionPreparationSummary:
        missing_required_fields = self._missing_required_fields(report)

        if missing_required_fields:
            return ExecutionPreparationSummary(missingRequiredFields=missing_required_fields)

        request = self._build_execution_request(report, payload, execution_mode)
        result = ExecutionService.prepare(request)

        validation_failures = [
            item.message for item in result.validation_results if item.status == "FAIL"
        ]
        validation_warnings = [
            item.message for item in result.validation_results if item.status == "WARN"
        ]

        return ExecutionPreparationSummary(
            request=request,
            result=result,
            missingRequiredFields=[],
            validationFailures=validation_failures,
            validationWarnings=validation_warnings,
        )

    def _build_safety_gate(
        self,
        report: DecisionReport,
        playbook_result: PlaybookEvaluationSummary,
        preparation: ExecutionPreparationSummary,
        payload: DecisionExecutionBridgeRequest,
        execution_mode: ExecutionMode,
    ) -> SafetyGateSummary:
        blocking_reasons: list[str] = []
        review_reasons: list[str] = []
        recommendation = report.final_recommendation.recommendation

        if recommendation == RecommendationType.NO_TRADE:
            blocking_reasons.append("Recommendation is NO_TRADE")
        elif recommendation == RecommendationType.WAIT:
            review_reasons.append("Recommendation is WAIT")

        if report.institutional_score.score < settings.DECISION_EXECUTION_MIN_INSTITUTIONAL_SCORE:
            blocking_reasons.append(
                f"Institutional score {report.institutional_score.score} is below minimum {settings.DECISION_EXECUTION_MIN_INSTITUTIONAL_SCORE}"
            )

        if report.risk_assessment.rr_expected < settings.DECISION_EXECUTION_MIN_RR:
            blocking_reasons.append(
                f"Decision RR {report.risk_assessment.rr_expected} is below minimum {settings.DECISION_EXECUTION_MIN_RR}"
            )

        if preparation.missingRequiredFields:
            review_reasons.append(
                "Missing required execution values: " + ", ".join(preparation.missingRequiredFields)
            )

        if not playbook_result.permitsContinuation:
            review_reasons.extend(playbook_result.reasons or ["Playbook requirements are not satisfied"])

        if report.context.side.value != recommendation.value if recommendation in {RecommendationType.BUY, RecommendationType.SELL} else False:
            blocking_reasons.append("Decision side does not match final recommendation")

        if preparation.result is not None:
            if preparation.result.rr < settings.DECISION_EXECUTION_MIN_RR:
                blocking_reasons.append(
                    f"Prepared RR {preparation.result.rr} is below minimum {settings.DECISION_EXECUTION_MIN_RR}"
                )

            if preparation.result.execution_status == ExecutionStatus.BLOCKED:
                blocking_reasons.append("Execution preparation is BLOCKED")

            if preparation.validationFailures:
                blocking_reasons.append("Execution validation contains failures")

            if preparation.result.execution_status == ExecutionStatus.REVIEW and not preparation.validationFailures:
                review_reasons.append("Execution preparation requires review")

            if preparation.validationWarnings:
                review_reasons.append("Execution preparation contains warnings")

        if blocking_reasons:
            return SafetyGateSummary(
                dispatchRequested=payload.dispatch,
                dispatchEnabled=self._dispatch_enabled,
                passed=False,
                action=BridgeAction.BLOCK,
                reasons=blocking_reasons + review_reasons,
            )

        if review_reasons:
            return SafetyGateSummary(
                dispatchRequested=payload.dispatch,
                dispatchEnabled=self._dispatch_enabled,
                passed=False,
                action=BridgeAction.REVIEW,
                reasons=review_reasons,
            )

        if execution_mode == ExecutionMode.PAPER:
            if not payload.confirmed:
                return SafetyGateSummary(
                    dispatchRequested=False,
                    dispatchEnabled=False,
                    passed=False,
                    action=BridgeAction.REVIEW,
                    reasons=["Explicit user confirmation is required for PAPER execution"],
                )

            return SafetyGateSummary(
                dispatchRequested=False,
                dispatchEnabled=False,
                passed=True,
                action=BridgeAction.DISPATCH,
                reasons=[],
            )

        if payload.dispatch and self._dispatch_enabled:
            return SafetyGateSummary(
                dispatchRequested=True,
                dispatchEnabled=True,
                passed=True,
                action=BridgeAction.DISPATCH,
                reasons=[],
            )

        reasons = []
        if payload.dispatch and not self._dispatch_enabled:
            reasons.append("Live dispatch is disabled by configuration")

        return SafetyGateSummary(
            dispatchRequested=payload.dispatch,
            dispatchEnabled=self._dispatch_enabled,
            passed=False,
            action=BridgeAction.PREPARE,
            reasons=reasons,
        )

    def _dispatch_if_allowed(
        self,
        report: DecisionReport,
        preparation: ExecutionPreparationSummary,
        safety_gate: SafetyGateSummary,
        payload: DecisionExecutionBridgeRequest,
        execution_mode: ExecutionMode,
    ) -> DispatchSummary:
        if execution_mode == ExecutionMode.PAPER:
            if safety_gate.action != BridgeAction.DISPATCH or preparation.result is None:
                return DispatchSummary(
                    executionMode=ExecutionMode.PAPER,
                    attempted=False,
                    status=DispatchStatus.SKIPPED,
                )

            paper_execution = self._paper_execution_service.execute(
                decision=report.context,
                lot_size=preparation.result.lot_size,
                entry_price=preparation.result.entry,
                stop_loss=preparation.result.stop_loss,
                take_profit=preparation.result.take_profit,
                decision_reference_id=report.context.ticket,
                decision_report=report,
                journal_service=self._journal_service,
                timeframe=payload.timeframe or settings.defaultTimeframe,
                session=payload.session or "UNSPECIFIED",
                risk_percent=preparation.result.risk_percent,
                expected_rr=preparation.result.rr,
                notes=payload.notes,
                tags=self._journal_tags(payload.tags),
            )

            return DispatchSummary(
                executionMode=ExecutionMode.PAPER,
                attempted=True,
                status=DispatchStatus.SUCCESS,
                paperExecution=paper_execution,
            )

        if not payload.dispatch:
            return DispatchSummary(
                executionMode=ExecutionMode.LIVE,
                attempted=False,
                status=DispatchStatus.NOT_REQUESTED,
            )

        if not self._dispatch_enabled:
            return DispatchSummary(
                executionMode=ExecutionMode.LIVE,
                attempted=False,
                status=DispatchStatus.DISABLED,
            )

        if safety_gate.action != BridgeAction.DISPATCH or preparation.result is None:
            return DispatchSummary(
                executionMode=ExecutionMode.LIVE,
                attempted=False,
                status=DispatchStatus.SKIPPED,
            )

        dispatch_context = self._build_dispatch_context(report, preparation.result)

        if dispatch_context.side == DecisionTradeSide.BUY:
            trade_result = self._trade_executor.executeBuy(dispatch_context)
        else:
            trade_result = self._trade_executor.executeSell(dispatch_context)

        if not trade_result.success:
            return DispatchSummary(
                executionMode=ExecutionMode.LIVE,
                attempted=True,
                status=DispatchStatus.FAILED,
                tradeResult=trade_result,
            )

        journal_entry = self._journal_service.createEntry(
            JournalEntryCreate(
                symbol=dispatch_context.symbol,
                timeframe=payload.timeframe or settings.defaultTimeframe,
                session=payload.session or "UNSPECIFIED",
                entryPrice=preparation.result.entry,
                stopLoss=preparation.result.stop_loss,
                takeProfit=preparation.result.take_profit,
                positionSize=dispatch_context.volume,
                riskPercent=preparation.result.risk_percent,
                expectedRR=preparation.result.rr,
                traderDecision=TraderDecision.FOLLOWED_OSCAR,
                decisionReport=report,
                personalNotes=payload.notes,
                tags=self._journal_tags(payload.tags),
            )
        )

        return DispatchSummary(
            executionMode=ExecutionMode.LIVE,
            attempted=True,
            status=DispatchStatus.SUCCESS,
            tradeResult=trade_result,
            journalEntry=journal_entry,
        )

    @staticmethod
    def _missing_required_fields(report: DecisionReport) -> list[str]:
        missing: list[str] = []
        context = report.context

        if context.price is None or context.price <= 0:
            missing.append("price")
        if context.sl is None or context.sl <= 0:
            missing.append("stop_loss")
        if context.tp is None or context.tp <= 0:
            missing.append("take_profit")
        if context.volume <= 0:
            missing.append("volume")
        if report.risk_assessment.risk_percent <= 0:
            missing.append("risk_percent")

        recommendation = report.final_recommendation.recommendation
        if recommendation not in {RecommendationType.BUY, RecommendationType.SELL}:
            return missing

        return missing

    @staticmethod
    def _build_execution_request(
        report: DecisionReport,
        payload: DecisionExecutionBridgeRequest,
        execution_mode: ExecutionMode,
    ) -> ExecutionRequest:
        if execution_mode == ExecutionMode.PAPER:
            # Provide canonical values so preparation remains deterministic and MT5-free.
            return ExecutionRequest(
                symbol=report.context.symbol,
                side=ExecutionTradeSide(report.context.side.value),
                entry_price=float(report.context.price),
                stop_loss=float(report.context.sl),
                take_profit=float(report.context.tp),
                risk_percent=report.risk_assessment.risk_percent,
                account_balance=payload.accountBalance or 10000.0,
                spread=0.0,
                pip_value=10.0,
                tick_value=10.0,
                leverage=100.0,
                contract_size=100000.0,
                min_rr=settings.DECISION_EXECUTION_MIN_RR,
            )

        return ExecutionRequest(
            symbol=report.context.symbol,
            side=ExecutionTradeSide(report.context.side.value),
            entry_price=float(report.context.price),
            stop_loss=float(report.context.sl),
            take_profit=float(report.context.tp),
            risk_percent=report.risk_assessment.risk_percent,
            account_balance=payload.accountBalance,
            min_rr=settings.DECISION_EXECUTION_MIN_RR,
        )

    @staticmethod
    def _build_dispatch_context(report: DecisionReport, result) -> DecisionContext:
        return DecisionContext(
            symbol=report.context.symbol,
            side=DecisionTradeSide(report.context.side.value),
            volume=result.lot_size,
            sl=result.stop_loss,
            tp=result.take_profit,
            comment=report.context.comment,
            ticket=report.context.ticket,
            price=result.entry,
        )

    @staticmethod
    def _journal_tags(tags: list[str]) -> list[str]:
        normalized = list(tags)
        if "decision-execution-bridge" not in normalized:
            normalized.append("decision-execution-bridge")
        return normalized

    @staticmethod
    def _final_status(action: BridgeAction, boundary: DispatchSummary) -> str:
        if boundary.executionMode == ExecutionMode.PAPER and boundary.status == DispatchStatus.SUCCESS:
            return "PAPER_EXECUTED"
        if action == BridgeAction.DISPATCH and boundary.status == DispatchStatus.SUCCESS:
            return "DISPATCHED"
        if action == BridgeAction.DISPATCH and boundary.status == DispatchStatus.FAILED:
            return "DISPATCH_FAILED"
        if action == BridgeAction.PREPARE:
            return "PREPARED"
        if action == BridgeAction.REVIEW:
            return "REVIEW_REQUIRED"
        return "BLOCKED"