import { api } from "./client";

export type OpportunityStage =
    | "CONTEXT_BUILDING"
    | "WAITING_LIQUIDITY"
    | "WAITING_SWEEP"
    | "WAITING_MSS"
    | "WAITING_DISPLACEMENT"
    | "WAITING_ENTRY_ZONE"
    | "EXECUTION_WINDOW"
    | "TRADE_ACTIVE";

export type RecommendedAction = "IGNORE" | "MONITOR" | "WATCH" | "PREPARE" | "READY" | "ACTIVE";
export type OpportunityPriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "IGNORE";
export type EstimatedEta = "NOW" | "<15_MIN" | "15_30_MIN" | "30_60_MIN" | ">60_MIN" | "UNKNOWN";

export interface OpportunityResult {
    symbol: string;
    timeframe: string;
    bias: string;
    structure: string;
    liquidity_target: string;
    current_stage: OpportunityStage;
    opportunity_score: number;
    institutional_score: number;
    execution_quality: number;
    priority: OpportunityPriority;
    estimated_eta: EstimatedEta;
    decision_summary: string;
    recommended_action: RecommendedAction;
    last_update: string;
}

export interface MarketSummary {
    total_assets: number;
    ignored: number;
    watching: number;
    preparing: number;
    ready: number;
    active: number;
    last_scan: string | null;
}

export interface OpportunityQueueResponse {
    market_summary: MarketSummary;
    opportunity_queue: OpportunityResult[];
}

export async function getOpportunityQueue(): Promise<OpportunityQueueResponse> {
    const response = await api.get<OpportunityQueueResponse>("/opportunity/queue");
    return response.data;
}
