import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { LiveDataOrchestrator } from "../LiveDataOrchestrator";
import { MarketDataEventBus } from "../marketData/EventBus";
import { MarketDataService } from "../marketData/MarketDataService";
import { TickStream } from "../marketData/TickStream";
import { CandleStream } from "../marketData/CandleStream";
import { TimeframeSynchronizer } from "../marketData/TimeframeSynchronizer";
import { ConnectionManager } from "../marketData/ConnectionManager";
import { createLoggerMock } from "../marketData/__tests__/testUtils";

const mockStructure = {
    trend: "RANGE" as const,
    last_high: 1.2,
    last_low: 1.1,
    bos: false,
    choch: false,
    mss: false,
};

const mockCandle = {
    time: "2026-01-01T00:00:00Z",
    open: 1.1,
    high: 1.2,
    low: 1.05,
    close: 1.15,
    tickVolume: 100,
    isClosed: true,
};

describe("LiveDataOrchestrator live mode", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it("executes pipeline from CandleClosed events and publishes DecisionContextUpdated", async () => {
        const eventBus = new MarketDataEventBus();
        const service = {
            get_latest_tick: vi.fn().mockResolvedValue({ symbol: "EURUSD", bid: 1.1, ask: 1.1002, spread: 0.0002, timestamp: 1000 }),
            get_market_status: vi.fn().mockResolvedValue({ connected: true, isOpen: true, session: "LONDON", serverTime: "2026-01-01T00:00:00Z" }),
            get_candles: vi.fn().mockResolvedValue([mockCandle, { ...mockCandle, time: "2026-01-01T00:05:00Z" }]),
        } as unknown as MarketDataService;

        const dataSource = {
            fetchTick: vi.fn(),
            fetchStatus: vi.fn(),
            fetchCandles: vi.fn(),
            fetchStructure: vi.fn().mockResolvedValue(mockStructure),
        };

        const orchestrator = new LiveDataOrchestrator(dataSource, { candleCount: 2 }, createLoggerMock());

        const tickStream = {
            start: vi.fn().mockResolvedValue(undefined),
            stop: vi.fn(),
        } as unknown as TickStream;

        const candleStream = {
            start: vi.fn(),
            stop: vi.fn(),
        } as unknown as CandleStream;

        const timeframeSynchronizer = {
            start: vi.fn(),
            stop: vi.fn(),
        } as unknown as TimeframeSynchronizer;

        orchestrator.attachLiveEngine({
            eventBus,
            marketDataService: service,
            connectionManager: {} as ConnectionManager,
            settings: { liveDebounceMs: 10, liveRateLimitMs: 50 },
            tickStream,
            candleStream,
            timeframeSynchronizer,
        });

        let pipelineExecutions = 0;
        let contexts = 0;

        eventBus.subscribe("PipelineExecuted", () => {
            pipelineExecutions += 1;
        });

        eventBus.subscribe("DecisionContextUpdated", () => {
            contexts += 1;
        });

        await orchestrator.startLive("EURUSD");

        eventBus.publish("CandleClosed", {
            symbol: "EURUSD",
            timeframe: "M5",
            candle: { ...mockCandle },
        });

        await vi.advanceTimersByTimeAsync(20);
        await Promise.resolve();

        orchestrator.stopLive();

        expect(pipelineExecutions).toBe(1);
        expect(contexts).toBe(1);
        expect(orchestrator.getDecisionContext("EURUSD")).not.toBeNull();
    });

    it("applies debounce and rate limit when candle events burst", async () => {
        const eventBus = new MarketDataEventBus();
        const service = {
            get_latest_tick: vi.fn().mockResolvedValue({ symbol: "EURUSD", bid: 1.1, ask: 1.1002, spread: 0.0002, timestamp: 1000 }),
            get_market_status: vi.fn().mockResolvedValue({ connected: true, isOpen: true, session: "LONDON", serverTime: "2026-01-01T00:00:00Z" }),
            get_candles: vi.fn().mockResolvedValue([mockCandle, { ...mockCandle, time: "2026-01-01T00:05:00Z" }]),
        } as unknown as MarketDataService;

        const orchestrator = new LiveDataOrchestrator(
            {
                fetchTick: vi.fn(),
                fetchStatus: vi.fn(),
                fetchCandles: vi.fn(),
                fetchStructure: vi.fn().mockResolvedValue(mockStructure),
            },
            { candleCount: 2 },
            createLoggerMock()
        );

        orchestrator.attachLiveEngine({
            eventBus,
            marketDataService: service,
            connectionManager: {} as ConnectionManager,
            settings: { liveDebounceMs: 10, liveRateLimitMs: 100 },
            tickStream: { start: vi.fn().mockResolvedValue(undefined), stop: vi.fn() } as unknown as TickStream,
            candleStream: { start: vi.fn(), stop: vi.fn() } as unknown as CandleStream,
            timeframeSynchronizer: { start: vi.fn(), stop: vi.fn() } as unknown as TimeframeSynchronizer,
        });

        let pipelineExecutions = 0;
        eventBus.subscribe("PipelineExecuted", () => {
            pipelineExecutions += 1;
        });

        await orchestrator.startLive("EURUSD");

        eventBus.publish("CandleClosed", { symbol: "EURUSD", timeframe: "M5", candle: { ...mockCandle } });
        eventBus.publish("CandleClosed", { symbol: "EURUSD", timeframe: "M15", candle: { ...mockCandle } });
        eventBus.publish("CandleClosed", { symbol: "EURUSD", timeframe: "H1", candle: { ...mockCandle } });

        await vi.advanceTimersByTimeAsync(25);
        await Promise.resolve();

        eventBus.publish("CandleClosed", { symbol: "EURUSD", timeframe: "M30", candle: { ...mockCandle } });
        await vi.advanceTimersByTimeAsync(25);
        await Promise.resolve();

        expect(pipelineExecutions).toBe(1);

        await vi.advanceTimersByTimeAsync(100);
        await Promise.resolve();

        orchestrator.stopLive();

        expect(pipelineExecutions).toBe(2);
    });
});
