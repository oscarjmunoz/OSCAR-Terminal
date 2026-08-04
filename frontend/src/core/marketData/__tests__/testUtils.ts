import { vi } from "vitest";

import { MarketDataEventBus } from "../EventBus";
import { HistoryLoader } from "../HistoryLoader";
import { ConsoleLogger } from "../logger";
import { MarketCache } from "../MarketCache";
import { MarketDataService } from "../MarketDataService";
import { MT5Connector } from "../MT5Connector";
import { DEFAULT_MARKET_DATA_SETTINGS } from "../settings";
import {
    ConnectionHealth,
    Logger,
    MarketCandle,
    MarketDataSettings,
    MarketStatus,
    MarketSymbolInfo,
    MarketTick,
    Mt5Bridge,
} from "../types";
import { ConnectionManager } from "../ConnectionManager";

export const baseTick: MarketTick = {
    symbol: "EURUSD",
    bid: 1.1,
    ask: 1.1002,
    spread: 0.0002,
    timestamp: 1_721_000_000,
};

export const baseCandles: MarketCandle[] = [
    { time: "2026-01-01T00:00:00Z", open: 1.1, high: 1.2, low: 1.05, close: 1.15, tickVolume: 100, isClosed: true },
    { time: "2026-01-01T00:05:00Z", open: 1.15, high: 1.22, low: 1.14, close: 1.21, tickVolume: 120, isClosed: false },
];

export const baseStatus: MarketStatus = {
    connected: true,
    isOpen: true,
    session: "LONDON",
    serverTime: "2026-01-01T00:05:00Z",
};

export const baseSymbolInfo: MarketSymbolInfo = {
    symbol: "EURUSD",
    digits: 5,
    point: 0.00001,
    tradeMode: "FULL",
    description: "Euro vs US Dollar",
};

export function createLoggerMock(): Logger {
    return {
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
        debug: vi.fn(),
    };
}

export function createBridge(overrides: Partial<Mt5Bridge> = {}): Mt5Bridge {
    const health: ConnectionHealth = { ok: true, latencyMs: 12 };

    return {
        initialize: vi.fn().mockResolvedValue(true),
        login: vi.fn().mockResolvedValue(true),
        shutdown: vi.fn().mockResolvedValue(undefined),
        healthCheck: vi.fn().mockResolvedValue(health),
        getTicks: vi.fn().mockResolvedValue([baseTick]),
        getLatestTick: vi.fn().mockResolvedValue(baseTick),
        getCandles: vi.fn().mockResolvedValue(baseCandles),
        getSymbolInfo: vi.fn().mockResolvedValue(baseSymbolInfo),
        getMarketStatus: vi.fn().mockResolvedValue(baseStatus),
        ...overrides,
    };
}

export function createSettings(overrides: Partial<MarketDataSettings> = {}): MarketDataSettings {
    return {
        ...DEFAULT_MARKET_DATA_SETTINGS,
        credentials: {
            ...DEFAULT_MARKET_DATA_SETTINGS.credentials,
            ...overrides.credentials,
        },
        ...overrides,
    };
}

export function createServiceHarness(options: {
    bridge?: Mt5Bridge;
    settings?: MarketDataSettings;
    logger?: Logger;
    now?: () => number;
} = {}) {
    const bridge = options.bridge ?? createBridge();
    const settings = options.settings ?? createSettings({ historySize: 2, healthCheckIntervalMs: 0 });
    const logger = options.logger ?? createLoggerMock();
    const eventBus = new MarketDataEventBus();
    const connector = new MT5Connector(bridge, settings, logger);
    const cache = new MarketCache(settings.cacheTtlMs, { now: options.now ?? (() => 0) });
    const historyLoader = new HistoryLoader(connector, cache, eventBus, logger, { now: () => 0 });
    const sleepCalls: number[] = [];
    const connectionManager = new ConnectionManager(
        connector,
        settings,
        eventBus,
        logger,
        { sleep: async (milliseconds: number) => void sleepCalls.push(milliseconds) },
        options.now ?? (() => 0)
    );
    const service = new MarketDataService(connectionManager, connector, historyLoader, cache, settings, eventBus, logger);

    return {
        bridge,
        cache,
        connectionManager,
        connector,
        eventBus,
        historyLoader,
        logger,
        service,
        settings,
        sleepCalls,
    };
}

export { ConsoleLogger };