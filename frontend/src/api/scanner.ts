import { api } from "./client";

export interface OpportunitySnapshot {
    symbol: string;
    timeframe: string;
    bias: string;
    structure: string;
    liquidity_target: string;
    stage: string;
    institutional_score: number;
    execution_quality: number;
    last_update: string;
    health: string;
    decision_summary: string;
}

export interface ScannerOpportunitiesResponse {
    opportunities: OpportunitySnapshot[];
}

export async function getScannerOpportunities(): Promise<ScannerOpportunitiesResponse> {
    const response = await api.get<ScannerOpportunitiesResponse>("/scanner/opportunities");
    return response.data;
}
