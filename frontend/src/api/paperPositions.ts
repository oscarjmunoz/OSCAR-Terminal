import { api } from "./client";

export type PaperPositionStatus = "OPEN" | "CLOSED";

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

export interface PaperPositionUpdateSummary {
    position: PaperPositionSummary;
    mark_price: number;
    unrealized_pnl: number;
    marked_at: string;
}

export interface PaperPositionCloseSummary {
    position: PaperPositionSummary;
    close_price: number;
    realized_pnl: number;
    realized_rr: number;
    closed_at: string;
    outcome: "WIN" | "LOSS" | "BREAK_EVEN";
    journal_entry_id: string | null;
    already_closed: boolean;
}

export async function updatePaperPosition(positionId: string): Promise<PaperPositionUpdateSummary> {
    const response = await api.post<PaperPositionUpdateSummary>(`/paper/positions/${positionId}/update`);
    return response.data;
}

export async function closePaperPosition(positionId: string): Promise<PaperPositionCloseSummary> {
    const response = await api.post<PaperPositionCloseSummary>(`/paper/positions/${positionId}/close`);
    return response.data;
}