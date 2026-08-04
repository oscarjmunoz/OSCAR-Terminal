import { MarketDataSettings } from "./types";

const DEFAULT_MARKET_DATA_SETTINGS: MarketDataSettings = {
    terminalPath: "",
    credentials: {
        login: 0,
        password: "",
        server: "",
    },
    reconnectIntervalMs: 1_000,
    reconnectMaxIntervalMs: 30_000,
    reconnectMaxAttempts: 5,
    cacheTtlMs: 5_000,
    historySize: 500,
    healthCheckIntervalMs: 5_000,
    tickPollIntervalMs: 250,
    tickBatchMaxSize: 20,
    tickBatchFlushIntervalMs: 1_000,
    tickRateLogIntervalMs: 1_000,
    liveDebounceMs: 200,
    liveRateLimitMs: 1_000,
};

function readNumber(value: string | undefined, fallback: number): number {
    if (!value) {
        return fallback;
    }

    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
}

function readString(value: string | undefined, fallback: string): string {
    return value ?? fallback;
}

export function resolveMarketDataSettings(overrides: Partial<MarketDataSettings> = {}): MarketDataSettings {
    const env = typeof import.meta !== "undefined" ? import.meta.env : undefined;

    const resolved: MarketDataSettings = {
        terminalPath: readString(env?.VITE_MT5_TERMINAL_PATH, DEFAULT_MARKET_DATA_SETTINGS.terminalPath),
        credentials: {
            login: readNumber(env?.VITE_MT5_LOGIN, DEFAULT_MARKET_DATA_SETTINGS.credentials.login),
            password: readString(env?.VITE_MT5_PASSWORD, DEFAULT_MARKET_DATA_SETTINGS.credentials.password),
            server: readString(env?.VITE_MT5_SERVER, DEFAULT_MARKET_DATA_SETTINGS.credentials.server),
        },
        reconnectIntervalMs: readNumber(env?.VITE_MT5_RECONNECT_INTERVAL_MS, DEFAULT_MARKET_DATA_SETTINGS.reconnectIntervalMs),
        reconnectMaxIntervalMs: readNumber(env?.VITE_MT5_RECONNECT_MAX_INTERVAL_MS, DEFAULT_MARKET_DATA_SETTINGS.reconnectMaxIntervalMs),
        reconnectMaxAttempts: readNumber(env?.VITE_MT5_RECONNECT_MAX_ATTEMPTS, DEFAULT_MARKET_DATA_SETTINGS.reconnectMaxAttempts),
        cacheTtlMs: readNumber(env?.VITE_MT5_CACHE_TTL_MS, DEFAULT_MARKET_DATA_SETTINGS.cacheTtlMs),
        historySize: readNumber(env?.VITE_MT5_HISTORY_SIZE, DEFAULT_MARKET_DATA_SETTINGS.historySize),
        healthCheckIntervalMs: readNumber(env?.VITE_MT5_HEALTH_CHECK_INTERVAL_MS, DEFAULT_MARKET_DATA_SETTINGS.healthCheckIntervalMs),
        tickPollIntervalMs: readNumber(env?.VITE_MT5_TICK_POLL_INTERVAL_MS, DEFAULT_MARKET_DATA_SETTINGS.tickPollIntervalMs),
        tickBatchMaxSize: readNumber(env?.VITE_MT5_TICK_BATCH_MAX_SIZE, DEFAULT_MARKET_DATA_SETTINGS.tickBatchMaxSize),
        tickBatchFlushIntervalMs: readNumber(env?.VITE_MT5_TICK_BATCH_FLUSH_INTERVAL_MS, DEFAULT_MARKET_DATA_SETTINGS.tickBatchFlushIntervalMs),
        tickRateLogIntervalMs: readNumber(env?.VITE_MT5_TICK_RATE_LOG_INTERVAL_MS, DEFAULT_MARKET_DATA_SETTINGS.tickRateLogIntervalMs),
        liveDebounceMs: readNumber(env?.VITE_MT5_LIVE_DEBOUNCE_MS, DEFAULT_MARKET_DATA_SETTINGS.liveDebounceMs),
        liveRateLimitMs: readNumber(env?.VITE_MT5_LIVE_RATE_LIMIT_MS, DEFAULT_MARKET_DATA_SETTINGS.liveRateLimitMs),
    };

    return {
        ...resolved,
        ...overrides,
        credentials: {
            ...resolved.credentials,
            ...overrides.credentials,
        },
    };
}

export { DEFAULT_MARKET_DATA_SETTINGS };