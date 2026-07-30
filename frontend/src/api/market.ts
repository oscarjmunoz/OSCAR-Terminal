// frontend/src/api/market.ts

import { api } from "./client";

export interface TerminalStatus {
    connected: boolean;
    account: number;
    company: string;
    server: string;
}

export interface TickResponse {
    symbol: string;
    bid: number;
    ask: number;
    spread: number;
}

export interface CandleResponse {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    tick_volume: number;
}

export async function getStatus(): Promise<TerminalStatus> {

    const response = await api.get<TerminalStatus>(
        "/market/status"
    );

    return response.data;

}

export async function getTick(): Promise<TickResponse> {

    const response = await api.get<TickResponse>(
        "/market/tick/USDCHF"
    );

    return response.data;

}

export async function getCandles(
    timeframe: string = "M5",
    count: number = 200,
): Promise<CandleResponse[]> {

    const response = await api.get<CandleResponse[]>(
        `/market/candles/USDCHF/${timeframe}?count=${count}`
    );

    return response.data;

}