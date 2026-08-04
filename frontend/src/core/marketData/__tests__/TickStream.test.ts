import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { ConnectionManager } from "../ConnectionManager";
import { MarketDataEventBus } from "../EventBus";
import { MarketDataService } from "../MarketDataService";
import { TickStream } from "../TickStream";
import { createLoggerMock, createSettings, baseTick } from "./testUtils";

describe("TickStream", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it("publishes TickReceived and TickBatchReceived while running", async () => {
        const service = {
            get_latest_tick: vi.fn().mockResolvedValue(baseTick),
        } as unknown as MarketDataService;

        const connectionManager = {
            ensureConnection: vi.fn().mockResolvedValue(undefined),
            handleConnectionError: vi.fn().mockResolvedValue(undefined),
        } as unknown as ConnectionManager;

        const eventBus = new MarketDataEventBus();
        const settings = createSettings({
            tickPollIntervalMs: 10,
            tickBatchMaxSize: 2,
            tickBatchFlushIntervalMs: 50,
            tickRateLogIntervalMs: 100,
        });

        const ticks: number[] = [];
        const batches: number[] = [];

        eventBus.subscribe("TickReceived", () => ticks.push(1));
        eventBus.subscribe("TickBatchReceived", (event) => batches.push(event.payload.ticks.length));

        const stream = new TickStream(service, connectionManager, eventBus, settings, createLoggerMock(), () => Date.now());

        await stream.start("EURUSD");
        await vi.advanceTimersByTimeAsync(45);
        stream.stop();

        expect(connectionManager.ensureConnection).toHaveBeenCalledOnce();
        expect(ticks.length).toBeGreaterThanOrEqual(2);
        expect(batches.length).toBeGreaterThanOrEqual(1);
    });

    it("tries reconnection flow when polling fails", async () => {
        const service = {
            get_latest_tick: vi.fn().mockRejectedValue(new Error("feed down")),
        } as unknown as MarketDataService;

        const connectionManager = {
            ensureConnection: vi.fn().mockResolvedValue(undefined),
            handleConnectionError: vi.fn().mockResolvedValue(undefined),
        } as unknown as ConnectionManager;

        const stream = new TickStream(
            service,
            connectionManager,
            new MarketDataEventBus(),
            createSettings({ tickPollIntervalMs: 10 }),
            createLoggerMock(),
            () => Date.now()
        );

        await stream.start("EURUSD");
        await vi.advanceTimersByTimeAsync(15);
        stream.stop();

        expect(connectionManager.handleConnectionError).toHaveBeenCalled();
    });
});
