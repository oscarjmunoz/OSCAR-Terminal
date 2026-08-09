import { api } from "./client";
import type { DecisionSide } from "./contracts";

export type TradeSide = DecisionSide;
export type ExecutionStatus = "READY" | "REVIEW" | "BLOCKED";

export interface ExecutionRequest {
    symbol: string;
    side: TradeSide;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    risk_percent: number;
    account_balance?: number;
    spread?: number;
    pip_value?: number;
    tick_value?: number;
    leverage?: number;
    contract_size?: number;
    min_rr?: number;
    max_risk_percent?: number;
    max_spread?: number;
    min_lot?: number;
    max_lot?: number;
    margin_buffer?: number;
}

export interface ValidationResult {
    status: string;
    message: string;
    severity: string;
}

export interface ExecutionResult {
    symbol: string;
    side: TradeSide;
    entry: number;
    stop_loss: number;
    take_profit: number;
    lot_size: number;
    risk_percent: number;
    risk_money: number;
    reward_money: number;
    risk_pips: number;
    reward_pips: number;
    rr: number;
    pip_value: number;
    tick_value: number;
    margin_required: number;
    spread: number;
    validation_results: ValidationResult[];
    institutional_score: number;
    execution_status: ExecutionStatus;
}

export async function prepareExecution(request: ExecutionRequest): Promise<ExecutionResult> {
    const response = await api.post<ExecutionResult>("/execution/prepare", request);
    return response.data;
}
