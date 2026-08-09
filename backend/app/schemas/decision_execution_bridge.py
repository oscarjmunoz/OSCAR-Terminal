from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator

from app.execution.schemas import ExecutionRequest
from app.execution.schemas import ExecutionResult
from app.journal.models import JournalEntry
from app.playbook.models import PlaybookMatch
from app.schemas.decision import DecisionContext
from app.schemas.decision_center import DecisionReport
from app.schemas.trade import TradeResult


class BridgeAction(str, Enum):
    PREPARE = "PREPARE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    DISPATCH = "DISPATCH"


class DecisionSource(str, Enum):
    REPORT = "REPORT"
    CONTEXT = "CONTEXT"


class DispatchStatus(str, Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    DISABLED = "DISABLED"
    SKIPPED = "SKIPPED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ExecutionMode(str, Enum):
    LIVE = "LIVE"
    PAPER = "PAPER"


class DecisionExecutionBridgeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisionContext: DecisionContext | None = None
    decisionReport: DecisionReport | None = None
    executionMode: ExecutionMode = ExecutionMode.LIVE
    confirmed: bool = False
    dispatch: bool = False
    timeframe: str | None = None
    session: str | None = None
    accountBalance: float | None = Field(default=None, gt=0)
    notes: str = ""
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_decision_input(self) -> DecisionExecutionBridgeRequest:
        if self.decisionContext is None and self.decisionReport is None:
            raise ValueError("decisionContext or decisionReport is required")
        return self


class BridgeDecisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: DecisionSource
    report: DecisionReport


class PlaybookEvaluationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    totalPlaybooks: int
    matches: list[PlaybookMatch] = Field(default_factory=list)
    matchedPlaybooks: list[PlaybookMatch] = Field(default_factory=list)
    bestMatch: PlaybookMatch | None = None
    bestMatchScore: int = 0
    requirementsSatisfied: bool = False
    permitsContinuation: bool = False
    reasons: list[str] = Field(default_factory=list)


class ExecutionPreparationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: ExecutionRequest | None = None
    result: ExecutionResult | None = None
    missingRequiredFields: list[str] = Field(default_factory=list)
    validationFailures: list[str] = Field(default_factory=list)
    validationWarnings: list[str] = Field(default_factory=list)


class SafetyGateSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dispatchRequested: bool
    dispatchEnabled: bool
    passed: bool
    action: BridgeAction
    reasons: list[str] = Field(default_factory=list)


class PaperOrderStatus(str, Enum):
    PREPARED = "PREPARED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


class PaperPositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PaperOrderSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str
    symbol: str
    side: str
    requested_volume: float
    entry_price: float
    stop_loss: float
    take_profit: float
    status: PaperOrderStatus
    created_at: str
    filled_at: str | None = None
    decision_reference_id: str | None = None


class PaperPositionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position_id: str
    symbol: str
    side: str
    volume: float
    entry_price: float
    stop_loss: float
    take_profit: float
    status: PaperPositionStatus
    opened_at: str
    updated_at: str
    originating_order_id: str
    close_price: float | None = None
    closed_at: str | None = None
    realized_pnl: float | None = None
    realized_rr: float | None = None
    last_mark_price: float | None = None
    last_marked_at: str | None = None
    unrealized_pnl: float | None = None
    journal_entry_id: str | None = None


class PaperExecutionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: PaperOrderSummary
    position: PaperPositionSummary
    deterministic_fill_price: float
    order_status_flow: list[PaperOrderStatus] = Field(default_factory=list)


class PaperPositionUpdateSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position: PaperPositionSummary
    mark_price: float
    unrealized_pnl: float
    marked_at: str


class PaperPositionCloseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position: PaperPositionSummary
    close_price: float
    realized_pnl: float
    realized_rr: float
    closed_at: str
    outcome: str
    journal_entry_id: str | None = None
    already_closed: bool = False


class DispatchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executionMode: ExecutionMode = ExecutionMode.LIVE
    attempted: bool = False
    status: DispatchStatus = DispatchStatus.NOT_REQUESTED
    tradeResult: TradeResult | None = None
    journalEntry: JournalEntry | None = None
    paperExecution: PaperExecutionSummary | None = None


class DecisionExecutionBridgeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: BridgeDecisionPayload
    playbookResult: PlaybookEvaluationSummary
    executionPreparation: ExecutionPreparationSummary
    safetyGate: SafetyGateSummary
    executionBoundary: DispatchSummary
    finalAction: BridgeAction
    finalStatus: str