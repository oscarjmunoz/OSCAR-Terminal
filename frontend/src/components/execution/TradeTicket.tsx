import type { ExecutionResult } from "../../api/execution";
import type { BridgeAction, DecisionExecutionBridgeResult, DispatchStatus } from "../../api/decisionExecution";

type TradeTicketProps = {
    ticket: ExecutionResult | null;
    bridge: DecisionExecutionBridgeResult | null;
    bridgeError?: string | null;
    canConfirmPaperTrade?: boolean;
    confirmPaperDisabledReason?: string | null;
    isConfirmingPaper?: boolean;
    onConfirmPaperTrade?: () => void;
};

function formatPrice(value: number): string {
    return value.toFixed(5);
}

function formatMoney(value: number): string {
    return `$${value.toFixed(2)}`;
}

function formatNumber(value: number): string {
    return value.toFixed(2);
}

function toneFromBridgeAction(action: BridgeAction): "positive" | "warning" | "danger" | "neutral" {
    if (action === "DISPATCH") {
        return "positive";
    }

    if (action === "PREPARE") {
        return "neutral";
    }

    if (action === "REVIEW") {
        return "warning";
    }

    return "danger";
}

function toneFromDispatchStatus(status: DispatchStatus): "positive" | "warning" | "danger" | "neutral" {
    if (status === "SUCCESS") {
        return "positive";
    }

    if (status === "FAILED") {
        return "danger";
    }

    if (status === "DISABLED" || status === "SKIPPED") {
        return "warning";
    }

    return "neutral";
}

function toneClass(tone: "positive" | "warning" | "danger" | "neutral"): string {
    if (tone === "neutral") {
        return "";
    }

    return ` status-chip--${tone}`;
}

function actionDescription(action: BridgeAction): string {
    if (action === "PREPARE") {
        return "PREPARE only creates a validated ticket. It does not execute a trade.";
    }

    if (action === "REVIEW") {
        return "REVIEW means manual confirmation is still required. It is not approval.";
    }

    if (action === "BLOCK") {
        return "BLOCK stops dispatch until backend safety conditions are satisfied.";
    }

    return "DISPATCH reflects backend dispatch state when safety gate permits it.";
}

export default function TradeTicket({
    ticket,
    bridge,
    bridgeError,
    canConfirmPaperTrade = false,
    confirmPaperDisabledReason = null,
    isConfirmingPaper = false,
    onConfirmPaperTrade,
}: TradeTicketProps) {
    if (!ticket && !bridge) {
        return (
            <section className="panel" aria-label="Institutional Trade Ticket">
                <header className="panel__header">
                    <div>
                        <span className="panel__eyebrow">Execution Bridge</span>
                        <h2 className="panel__title">Institutional Trade Ticket</h2>
                        <p className="panel__subtitle">No bridge result yet.</p>
                    </div>
                </header>

                {bridgeError ? (
                    <div className="row-item" role="alert">
                        <strong>Bridge API Error</strong>
                        <p className="row-item__meta">{bridgeError}</p>
                    </div>
                ) : null}
            </section>
        );
    }

    if (ticket && !bridge && !bridgeError) {
        return (
            <section className="panel" aria-label="Institutional Trade Ticket">
                <header className="panel__header">
                    <div>
                        <span className="panel__eyebrow">Execution Bridge</span>
                        <h2 className="panel__title">Institutional Trade Ticket</h2>
                    </div>
                </header>

                <div className="panel__body">
                    <div className="row-item"><strong>Symbol</strong><span>{ticket.symbol}</span></div>
                    <div className="row-item"><strong>Side</strong><span>{ticket.side}</span></div>
                    <div className="row-item"><strong>Entry</strong><span>{formatPrice(ticket.entry)}</span></div>
                    <div className="row-item"><strong>Stop Loss</strong><span>{formatPrice(ticket.stop_loss)}</span></div>
                    <div className="row-item"><strong>Take Profit</strong><span>{formatPrice(ticket.take_profit)}</span></div>
                    <div className="row-item"><strong>Risk %</strong><span>{formatNumber(ticket.risk_percent)}%</span></div>
                    <div className="row-item"><strong>Risk $</strong><span>{formatMoney(ticket.risk_money)}</span></div>
                    <div className="row-item"><strong>Reward $</strong><span>{formatMoney(ticket.reward_money)}</span></div>
                    <div className="row-item"><strong>Lot</strong><span>{formatNumber(ticket.lot_size)}</span></div>
                    <div className="row-item"><strong>RR</strong><span>{formatNumber(ticket.rr)}</span></div>
                    <div className="row-item"><strong>Spread</strong><span>{formatNumber(ticket.spread)}</span></div>
                    <div className="row-item"><strong>Margin</strong><span>{formatMoney(ticket.margin_required)}</span></div>
                    <div className="row-item"><strong>Institutional Score</strong><span>{formatNumber(ticket.institutional_score)}</span></div>
                    <div className="row-item"><strong>Execution Status</strong><span>{ticket.execution_status}</span></div>
                </div>
            </section>
        );
    }

    const finalAction = bridge?.finalAction ?? "PREPARE";
    const safetyAction = bridge?.safetyGate.action ?? "PREPARE";
    const dispatchStatus = bridge?.executionBoundary.status ?? "NOT_REQUESTED";
    const preparationResult = ticket ?? bridge?.executionPreparation.result ?? null;
    const bestMatch = bridge?.playbookResult.bestMatch ?? null;
    const paperExecution = bridge?.executionBoundary.paperExecution ?? null;

    return (
        <section className="panel" aria-label="Institutional Trade Ticket">
            <header className="panel__header">
                <div>
                    <span className="panel__eyebrow">Execution Bridge</span>
                    <h2 className="panel__title">Institutional Trade Ticket</h2>
                    <p className="panel__subtitle">{actionDescription(finalAction)}</p>
                </div>
            </header>

            <div className="panel__body">
                <div className="row-item" data-testid="bridge-status-row">
                    <div className="row-item__top">
                        <strong className="row-item__title">Decision Recommendation</strong>
                        <span className={`status-chip${toneClass(toneFromBridgeAction(finalAction))}`}>{bridge?.decision.report.final_recommendation.recommendation ?? "N/A"}</span>
                    </div>
                    <p className="row-item__meta">{bridge?.decision.report.final_recommendation.explanation ?? "No recommendation provided by backend."}</p>
                </div>

                <div className="row-item">
                    <div className="row-item__top">
                        <strong className="row-item__title">Safety Gate</strong>
                        <span className={`status-chip${toneClass(toneFromBridgeAction(safetyAction))}`}>{safetyAction}</span>
                    </div>
                    <p className="row-item__meta">
                        Gate passed: {bridge?.safetyGate.passed ? "YES" : "NO"} · Dispatch requested: {bridge?.safetyGate.dispatchRequested ? "YES" : "NO"} · Dispatch enabled: {bridge?.safetyGate.dispatchEnabled ? "YES" : "NO"}
                    </p>
                    {bridge?.safetyGate.reasons.length ? (
                        <p className="row-item__meta">{bridge.safetyGate.reasons.join(" · ")}</p>
                    ) : (
                        <p className="row-item__meta">No safety restrictions reported.</p>
                    )}
                </div>

                <div className="row-item">
                    <div className="row-item__top">
                        <strong className="row-item__title">Dispatch Status</strong>
                        <span className={`status-chip${toneClass(toneFromDispatchStatus(dispatchStatus))}`}>{dispatchStatus}</span>
                    </div>
                    <p className="row-item__meta">Final action: {finalAction} · Final status: {bridge?.finalStatus ?? "N/A"}</p>
                    {bridge?.executionBoundary.tradeResult?.error ? <p className="row-item__meta">Dispatch error: {bridge.executionBoundary.tradeResult.error}</p> : null}
                    {bridge?.executionBoundary.journalEntry?.id ? <p className="row-item__meta">Journal entry recorded: {bridge.executionBoundary.journalEntry.id}</p> : null}
                </div>

                <div className="row-item">
                    <div className="row-item__top">
                        <strong className="row-item__title">Playbook Match</strong>
                        <span className={`status-chip${toneClass(bridge?.playbookResult.permitsContinuation ? "positive" : "warning")}`}>
                            {bridge?.playbookResult.permitsContinuation ? "CONTINUE" : "REVIEW"}
                        </span>
                    </div>
                    {bestMatch ? (
                        <p className="row-item__meta">{bestMatch.setupName} · Match {bestMatch.matchPercentage}% · {bestMatch.explanation}</p>
                    ) : (
                        <p className="row-item__meta">No matching playbook provided.</p>
                    )}
                </div>

                <div className="row-item">
                    <div className="row-item__top">
                        <strong className="row-item__title">Execution Preparation</strong>
                        <span className="status-chip">{preparationResult?.execution_status ?? "N/A"}</span>
                    </div>

                    {bridge?.executionPreparation.missingRequiredFields.length ? (
                        <p className="row-item__meta">Missing fields: {bridge.executionPreparation.missingRequiredFields.join(", ")}</p>
                    ) : null}
                    {bridge?.executionPreparation.validationFailures.length ? (
                        <p className="row-item__meta">Validation failures: {bridge.executionPreparation.validationFailures.join(" · ")}</p>
                    ) : null}
                    {bridge?.executionPreparation.validationWarnings.length ? (
                        <p className="row-item__meta">Validation warnings: {bridge.executionPreparation.validationWarnings.join(" · ")}</p>
                    ) : null}
                </div>

                {preparationResult ? (
                    <>
                        <div className="row-item" data-testid="paper-confirmation-row">
                            <div className="row-item__top">
                                <strong className="row-item__title">Human Confirmation</strong>
                                <span className="status-chip">PAPER ONLY</span>
                            </div>
                            <p className="row-item__meta">Selecting opportunities, opening tickets, and generating decisions never executes a paper trade.</p>
                            <button
                                type="button"
                                className="action-button"
                                data-testid="confirm-paper-trade-button"
                                onClick={onConfirmPaperTrade}
                                disabled={!canConfirmPaperTrade || isConfirmingPaper}
                            >
                                {isConfirmingPaper ? "Submitting PAPER confirmation..." : "CONFIRM PAPER TRADE"}
                            </button>
                            {!canConfirmPaperTrade && confirmPaperDisabledReason ? (
                                <p className="row-item__meta">{confirmPaperDisabledReason}</p>
                            ) : null}
                        </div>

                        <div className="row-item"><strong>Symbol</strong><span>{preparationResult.symbol}</span></div>
                        <div className="row-item"><strong>Side</strong><span>{preparationResult.side}</span></div>
                        <div className="row-item"><strong>Entry</strong><span>{formatPrice(preparationResult.entry)}</span></div>
                        <div className="row-item"><strong>Stop Loss</strong><span>{formatPrice(preparationResult.stop_loss)}</span></div>
                        <div className="row-item"><strong>Take Profit</strong><span>{formatPrice(preparationResult.take_profit)}</span></div>
                        <div className="row-item"><strong>Risk %</strong><span>{formatNumber(preparationResult.risk_percent)}%</span></div>
                        <div className="row-item"><strong>Risk $</strong><span>{formatMoney(preparationResult.risk_money)}</span></div>
                        <div className="row-item"><strong>Reward $</strong><span>{formatMoney(preparationResult.reward_money)}</span></div>
                        <div className="row-item"><strong>Lot</strong><span>{formatNumber(preparationResult.lot_size)}</span></div>
                        <div className="row-item"><strong>RR</strong><span>{formatNumber(preparationResult.rr)}</span></div>
                        <div className="row-item"><strong>Spread</strong><span>{formatNumber(preparationResult.spread)}</span></div>
                        <div className="row-item"><strong>Margin</strong><span>{formatMoney(preparationResult.margin_required)}</span></div>
                        <div className="row-item"><strong>Institutional Score</strong><span>{formatNumber(preparationResult.institutional_score)}</span></div>
                        <div className="row-item"><strong>Execution Status</strong><span>{preparationResult.execution_status}</span></div>

                        {paperExecution ? (
                            <div className="row-item" data-testid="paper-execution-result">
                                <div className="row-item__top">
                                    <strong className="row-item__title">Paper Execution Result</strong>
                                    <span className="status-chip status-chip--positive">{bridge?.executionBoundary.status ?? "SUCCESS"}</span>
                                </div>
                                <p className="row-item__meta">Order ID: {paperExecution.order.order_id} · Status: {paperExecution.order.status}</p>
                                <p className="row-item__meta">Open Position ID: {paperExecution.position.position_id} · Status: {paperExecution.position.status}</p>
                                <p className="row-item__meta">Symbol: {paperExecution.position.symbol} · Side: {paperExecution.position.side} · Volume: {formatNumber(paperExecution.position.volume)}</p>
                            </div>
                        ) : null}
                    </>
                ) : (
                    <div className="row-item">
                        <strong>Execution preparation is not available for this response.</strong>
                    </div>
                )}

                {bridgeError ? (
                    <div className="row-item" role="alert">
                        <strong>Bridge API Error</strong>
                        <p className="row-item__meta">{bridgeError}</p>
                    </div>
                ) : null}
            </div>
        </section>
    );
}
