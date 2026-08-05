import { api } from "./client";

export interface HealthResponse {
    status: string;
    service: string;
    version: string;
}

export interface OperationalReadinessItem {
    key: string;
    label: string;
    status: "GREEN" | "YELLOW" | "RED";
    detail: string;
    observedAt: string | null;
}

export interface OperationalReadinessResponse {
    symbol: string;
    timeframe: string;
    generatedAt: string;
    overallStatus: "GREEN" | "YELLOW" | "RED";
    items: OperationalReadinessItem[];
}

export async function getHealth(): Promise<HealthResponse> {

    const response = await api.get<HealthResponse>(
        "/health"
    );

    return response.data;

}

export async function getOperationalReadiness(symbol: string, timeframe: string): Promise<OperationalReadinessResponse> {

    const response = await api.get<OperationalReadinessResponse>(
        `/health/readiness?symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(timeframe)}`
    );

    return response.data;

}