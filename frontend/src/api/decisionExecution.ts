import { api } from "./client";
import type { DecisionSide } from "./contracts";
import type { LiveDecisionReport } from "./decision";
import type { ExecutionRequest, ExecutionResult } from "./execution";
import type { PlaybookMatch } from "./playbook";

export type BridgeAction = "PREPARE" | "REVIEW" | "BLOCK" | "DISPATCH";
export type DecisionSource = "REPORT" | "CONTEXT";
export type DispatchStatus = "NOT_REQUESTED" | "DISABLED" | "SKIPPED" | "SUCCESS" | "FAILED";
export type ExecutionMode = "LIVE" | "PAPER";
export type PaperPositionStatus = "OPEN" | "CLOSED";

export interface DecisionExecutionBridgeRequest {
    decisionContext?: {
        symbol: string;
        side: DecisionSide;
        volume: number;
        sl?: number | null;
        tp?: number | null;
        comment?: string | null;
        ticket?: number | null;
        price?: number | null;
    };
    decisionReport?: LiveDecisionReport;
    executionMode?: ExecutionMode;
    confirmed?: boolean;
    dispatch?: boolean;
    timeframe?: string | null;
    session?: string | null;
    accountBalance?: number | null;
    notes?: string;
    tags?: string[];
}

export interface BridgeDecisionPayload {
    source: DecisionSource;
    report: LiveDecisionReport;
}

export interface PlaybookEvaluationSummary {
    totalPlaybooks: number;
    matches: PlaybookMatch[];
    matchedPlaybooks: PlaybookMatch[];
    bestMatch: PlaybookMatch | null;
    bestMatchScore: number;
    requirementsSatisfied: boolean;
    permitsContinuation: boolean;
    reasons: string[];
}

export interface ExecutionPreparationSummary {
    request: ExecutionRequest | null;
    result: ExecutionResult | null;
    missingRequiredFields: string[];
    validationFailures: string[];
    validationWarnings: string[];
}

export interface SafetyGateSummary {
    dispatchRequested: boolean;
    dispatchEnabled: boolean;
    passed: boolean;
    action: BridgeAction;
    reasons: string[];
}

export interface TradeOrder {
    action: number;
    symbol: string;
    volume: number;
    orderType: number;
    price: number;
    sl: number | null;
    tp: number | null;
    deviation: number;
    magicNumber: number;
    comment: string | null;
    position: number | null;
    order: number | null;
}

export interface TradeResult {
    success: boolean;
    ticket: number | null;
    order: TradeOrder | null;
    price: number | null;
    volume: number | null;
    sl: number | null;
    tp: number | null;
    brokerMessage: string | null;
    executionTime: number | null;
    error: string | null;
}

export interface JournalDecisionSnapshot {
    bias: {
        bias: string;
        explanation: string;
    };
    score: number;
    confidence: number;
    liquidity: {
        buy_liquidity: number;
        sell_liquidity: number;
        liquidity_taken: number;
        pending_liquidity: number;
        explanation: string;
    };
    structure: {
        trend: string;
        bos: boolean;
        choch: boolean;
        mss: boolean;
        explanation: string;
    };
    zones: {
        order_block: { active: boolean; explanation: string };
        breaker: { active: boolean; explanation: string };
        mitigation: { active: boolean; explanation: string };
        fvg: { active: boolean; explanation: string };
        premium: { active: boolean; explanation: string };
        discount: { active: boolean; explanation: string };
    };
    confluences: Array<{
        name: string;
        detected: boolean;
        importance: "HIGH" | "MEDIUM" | "LOW";
        explanation: string;
    }>;
    checklist: Array<{
        label: string;
        checked: boolean;
        explanation: string;
    }>;
    recommendation: {
        recommendation: string;
        explanation: string;
    };
    narrative: string;
}

export interface JournalEntry {
    id: string;
    createdAt: string;
    symbol: string;
    timeframe: string;
    session: string;
    entryPrice: number;
    stopLoss: number;
    takeProfit: number;
    positionSize: number;
    riskPercent: number;
    expectedRR: number;
    decisionSnapshot: JournalDecisionSnapshot;
    traderDecision: string;
    tradeOutcome: string;
    profitLoss: number | null;
    realizedRR: number | null;
    durationMinutes: number | null;
    closeReason: string | null;
    personalNotes: string;
    tags: string[];
}

export interface PaperOrderSummary {
    order_id: string;
    symbol: string;
    side: string;
    requested_volume: number;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    status: "PREPARED" | "SUBMITTED" | "FILLED" | "REJECTED";
    created_at: string;
    filled_at: string | null;
    decision_reference_id: string | null;
}

export interface PaperPositionSummary {
    position_id: string;
    symbol: string;
    side: string;
    volume: number;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    status: PaperPositionStatus;
    opened_at: string;
    updated_at: string;
    originating_order_id: string;
    close_price: number | null;
    closed_at: string | null;
    realized_pnl: number | null;
    realized_rr: number | null;
    last_mark_price: number | null;
    last_marked_at: string | null;
    unrealized_pnl: number | null;
    journal_entry_id: string | null;
}

export interface PaperExecutionSummary {
    order: PaperOrderSummary;
    position: PaperPositionSummary;
    deterministic_fill_price: number;
    order_status_flow: Array<"PREPARED" | "SUBMITTED" | "FILLED" | "REJECTED">;
}

export interface DispatchSummary {
    executionMode?: ExecutionMode;
    attempted: boolean;
    status: DispatchStatus;
    tradeResult: TradeResult | null;
    journalEntry: JournalEntry | null;
    paperExecution?: PaperExecutionSummary | null;
}

export interface DecisionExecutionBridgeResult {
    decision: BridgeDecisionPayload;
    playbookResult: PlaybookEvaluationSummary;
    executionPreparation: ExecutionPreparationSummary;
    safetyGate: SafetyGateSummary;
    executionBoundary: DispatchSummary;
    finalAction: BridgeAction;
    finalStatus: string;
}

export async function executeDecisionBridge(payload: DecisionExecutionBridgeRequest): Promise<DecisionExecutionBridgeResult> {

    const response = await api.post<DecisionExecutionBridgeResult>(
        "/decision/execute",
        payload
    );

    return response.data;

}