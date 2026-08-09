import EmptyState from "../dashboard/EmptyState";
import MetricCard from "../dashboard/MetricCard";
import Panel from "../dashboard/Panel";
import type { OpportunityQueueResponse, OpportunityResult } from "../../api/opportunity";

type Props = {
    opportunities: OpportunityResult[];
    marketSummary: OpportunityQueueResponse["market_summary"] | null;
    selectedOpportunityKey: string | null;
    isLoading?: boolean;
    isRefreshing?: boolean;
    error?: string | null;
    onInspect: (opportunity: OpportunityResult) => void;
    onRefresh: () => void;
};

function opportunityKey(opportunity: OpportunityResult): string {
    return `${opportunity.symbol}:${opportunity.timeframe}`;
}

function toneFromPriority(priority: OpportunityResult["priority"]): "positive" | "warning" | "danger" | "neutral" {
    if (priority === "CRITICAL" || priority === "HIGH") {
        return "positive";
    }

    if (priority === "MEDIUM") {
        return "warning";
    }

    if (priority === "IGNORE") {
        return "danger";
    }

    return "neutral";
}

function toneFromHealth(health: string): "positive" | "warning" | "danger" | "neutral" {
    const normalized = health.trim().toUpperCase();

    if (normalized === "GREEN") {
        return "positive";
    }

    if (normalized === "YELLOW") {
        return "warning";
    }

    if (normalized === "RED") {
        return "danger";
    }

    return "neutral";
}

function formatFreshness(value: string | null | undefined): string {
    if (!value) {
        return "N/A";
    }

    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
        return value;
    }

    return parsed.toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function formatMarketScan(value: string | null | undefined): string {
    if (!value) {
        return "No scan timestamp reported";
    }

    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
        return value;
    }

    return parsed.toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

export default function OpportunityQueuePanel({
    opportunities,
    marketSummary,
    selectedOpportunityKey,
    isLoading = false,
    isRefreshing = false,
    error = null,
    onInspect,
    onRefresh,
}: Props) {
    const hasData = opportunities.length > 0;
    const hasError = Boolean(error);
    const stale = hasError && hasData;

    return (
        <Panel
            eyebrow="Zone 1"
            title="Opportunity Queue"
            subtitle="Backend-ranked opportunities ready for inspection."
            action={(
                <button
                    type="button"
                    className="action-button"
                    onClick={onRefresh}
                    disabled={isLoading || isRefreshing}
                >
                    {isRefreshing ? "Refreshing..." : "Refresh Queue"}
                </button>
            )}
            testId="opportunity-queue-panel"
        >
            {isLoading ? (
                <EmptyState
                    title="Loading opportunity queue"
                    description="Fetching opportunities returned by the backend queue."
                />
            ) : hasError && !hasData ? (
                <div className="row-item" role="alert">
                    <strong>Opportunity queue unavailable</strong>
                    <p className="row-item__meta">{error}</p>
                </div>
            ) : hasData ? (
                <>
                    {marketSummary ? (
                        <>
                            <div className="metric-grid metric-grid--three">
                                <MetricCard label="Total" value={String(marketSummary.total_assets)} detail="Returned by the backend queue." />
                                <MetricCard label="Ready" value={String(marketSummary.ready)} detail="Backend ranked as ready." tone={marketSummary.ready > 0 ? "positive" : "neutral"} />
                                <MetricCard label="Preparing" value={String(marketSummary.preparing)} detail="Backend ranked as preparing." tone={marketSummary.preparing > 0 ? "warning" : "neutral"} />
                            </div>

                            <div className="metric-grid metric-grid--three">
                                <MetricCard label="Watching" value={String(marketSummary.watching)} detail="Backend ranked as watching." />
                                <MetricCard label="Active" value={String(marketSummary.active)} detail="Backend ranked as active." tone={marketSummary.active > 0 ? "positive" : "neutral"} />
                                <MetricCard label="Ignored" value={String(marketSummary.ignored)} detail="Filtered out by backend ranking." tone={marketSummary.ignored > 0 ? "danger" : "neutral"} />
                            </div>
                        </>
                    ) : null}

                    <p className="row-item__meta" style={{ marginBottom: "0.75rem" }}>
                        Last scan: {formatMarketScan(marketSummary?.last_scan ?? null)}
                        {stale ? " · Showing stale queue data until refresh succeeds." : ""}
                    </p>

                    {hasError ? (
                        <div className="row-item" role="alert">
                            <strong>Opportunity queue refresh failed</strong>
                            <p className="row-item__meta">{error}</p>
                            <p className="row-item__meta">Existing queue data remains visible.</p>
                        </div>
                    ) : null}

                    <div className="row-list">
                        {opportunities.map((opportunity) => {
                            const key = opportunityKey(opportunity);
                            const isSelected = key === selectedOpportunityKey;

                            return (
                                <article key={key} className="row-item" data-testid="opportunity-item">
                                    <div className="row-item__top">
                                        <strong className="row-item__title">
                                            {opportunity.symbol} · {opportunity.timeframe}
                                        </strong>
                                        <span className={`status-chip status-chip--${toneFromPriority(opportunity.priority)}`}>
                                            {isSelected ? "INSPECTING" : opportunity.priority}
                                        </span>
                                    </div>

                                    <p className="row-item__meta">
                                        Direction: {opportunity.bias} · Stage: {opportunity.current_stage} · Health: {opportunity.health}
                                    </p>
                                    <p className="row-item__meta">
                                        Score: {opportunity.opportunity_score.toFixed(2)} · Institutional: {opportunity.institutional_score.toFixed(2)} · Execution: {opportunity.execution_quality.toFixed(2)}
                                    </p>
                                    <p className="row-item__meta">
                                        Liquidity target: {opportunity.liquidity_target} · Updated: {formatFreshness(opportunity.last_update)}
                                    </p>
                                    <p className="row-item__meta">{opportunity.decision_summary}</p>

                                    <div className="row-item__top" style={{ marginTop: "0.75rem" }}>
                                        <span className={`status-chip status-chip--${toneFromHealth(opportunity.health)}`}>
                                            {opportunity.health}
                                        </span>
                                        <button
                                            type="button"
                                            className="action-button"
                                            onClick={() => onInspect(opportunity)}
                                            aria-pressed={isSelected}
                                            aria-label={`Inspect ${opportunity.symbol} ${opportunity.timeframe}`}
                                        >
                                            {isSelected ? "Selected" : "Inspect"}
                                        </button>
                                    </div>
                                </article>
                            );
                        })}
                    </div>
                </>
            ) : (
                <EmptyState
                    title="Opportunity queue is empty"
                    description="The backend returned no opportunities to inspect right now."
                />
            )}
        </Panel>
    );
}