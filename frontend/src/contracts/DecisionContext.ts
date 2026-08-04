import { MarketBias, MarketSession, MarketTrend } from "../engine/context/types";
import { DecisionType, InstitutionalAnalysis } from "../engine/pipeline/types";

export type DecisionRecommendation = DecisionType;
export type DecisionConnectionState = "LIVE" | "OFFLINE" | "DEGRADED";

export interface DecisionHeaderContext {
    symbol: string;
    timeframe: string;
    date: string;
    session: MarketSession | "UNKNOWN";
    connection: DecisionConnectionState;
    latencyMs: number | null;
}

export interface DecisionScoreContext {
    institutionalScore: number;
    confidence: number;
    bias: MarketBias | "UNKNOWN";
    recommendation: DecisionRecommendation;
}

export interface DecisionRiskContext {
    grade: "LOW" | "MEDIUM" | "HIGH";
    rr: string;
    capitalRisk: string;
    stopDistance: string;
}

export interface DecisionLiquidityContext {
    sweep: string;
    internal: string;
    external: string;
    levels: string[];
}

export interface DecisionStructureContext {
    bos: string;
    choch: string;
    mss: string;
    trend: MarketTrend | "UNKNOWN";
}

export interface DecisionExecutionContext {
    entry: string | null;
    stop: string | null;
    tp1: string | null;
    tp2: string | null;
    rr: string | null;
}

export interface DecisionConfluenceContext {
    liquidity: number;
    structure: number;
    risk: number;
    context: number;
}

export interface DecisionContext {
    header: DecisionHeaderContext;
    score: DecisionScoreContext;
    risk: DecisionRiskContext;
    liquidity: DecisionLiquidityContext;
    structure: DecisionStructureContext;
    context: {
        orderBlocks: string[];
        fvg: string[];
        breaker: string;
        mitigation: string;
        premium: string;
        discount: string;
    };
    narrative: string;
    warnings: string[];
    execution: DecisionExecutionContext | null;
    confluences: DecisionConfluenceContext;
    source: "INSTITUTIONAL_PIPELINE";
}

export interface DecisionContextInput {
    symbol: string;
    timeframe: string;
    timestamp: number;
    analysis: InstitutionalAnalysis;
    latencyMs?: number | null;
}