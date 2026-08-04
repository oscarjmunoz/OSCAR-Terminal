export type MarketTimeframe = "M1" | "M5" | "M15" | "M30" | "H1" | "H4" | "D1";

export type ConnectionState = "CONNECTED" | "CONNECTING" | "DISCONNECTED" | "RECONNECTING" | "ERROR";

export interface MarketTick {
    symbol: string;
    bid: number;
    ask: number;
    spread: number;
    timestamp: number;
}

export interface MarketCandle {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    tickVolume: number;
    isClosed?: boolean;
}

export interface MarketSymbolInfo {
    symbol: string;
    digits: number;
    point: number;
    tradeMode: string;
    description?: string;
}

export interface MarketStatus {
    connected: boolean;
    isOpen: boolean;
    session: string;
    serverTime: string;
}

export interface MT5Credentials {
    login: number;
    password: string;
    server: string;
}

export interface MarketDataSettings {
    terminalPath: string;
    credentials: MT5Credentials;
    reconnectIntervalMs: number;
    reconnectMaxIntervalMs: number;
    reconnectMaxAttempts: number;
    cacheTtlMs: number;
    historySize: number;
    healthCheckIntervalMs: number;
    tickPollIntervalMs: number;
    tickBatchMaxSize: number;
    tickBatchFlushIntervalMs: number;
    tickRateLogIntervalMs: number;
    liveDebounceMs: number;
    liveRateLimitMs: number;
}

export interface ConnectionHealth {
    ok: boolean;
    latencyMs: number;
    message?: string;
}

export interface Mt5ApiErrorShape {
    code?: string;
    message?: string;
}

export interface Mt5Bridge {
    initialize(terminalPath: string): Promise<boolean>;
    login(credentials: MT5Credentials): Promise<boolean>;
    shutdown(): Promise<void>;
    healthCheck(): Promise<ConnectionHealth>;
    getTicks(symbol: string, count: number): Promise<MarketTick[]>;
    getLatestTick(symbol: string): Promise<MarketTick | null>;
    getCandles(symbol: string, timeframe: MarketTimeframe, count: number): Promise<MarketCandle[]>;
    getSymbolInfo(symbol: string): Promise<MarketSymbolInfo | null>;
    getMarketStatus(symbol: string): Promise<MarketStatus>;
}

export interface Logger {
    info(message: string, meta?: Record<string, unknown>): void;
    warn(message: string, meta?: Record<string, unknown>): void;
    error(message: string, meta?: Record<string, unknown>): void;
    debug(message: string, meta?: Record<string, unknown>): void;
}

export interface Scheduler {
    sleep(milliseconds: number): Promise<void>;
}

export interface Clock {
    now(): number;
}

export interface TimeSource {
    now(): number;
}