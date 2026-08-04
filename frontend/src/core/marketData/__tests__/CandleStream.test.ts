import { describe, expect, it, vi } from "vitest";

import { MarketDataEventBus } from "../EventBus";
import { MarketDataService } from "../MarketDataService";
import { CandleStream } from "../CandleStream";
import { baseCandles, baseTick, createLoggerMock } from "./testUtils";

describe("CandleStream", () => {
    it("publishes CandleClosed for all supported timeframes", async () => {
        const service = {
            get_last_closed_candle: vi.fn().mockResolvedValue(baseCandles[0]),
        } as unknown as MarketDataService;

        const eventBus = new MarketDataEventBus();
        const events: string[] = [];

        eventBus.subscribe("CandleClosed", (event) => {
            events.push(`${event.payload.symbol}:${event.payload.timeframe}`);
        });

        const stream = new CandleStream(service, eventBus, createLoggerMock());
        stream.start();

        eventBus.publish("TickReceived", { symbol: "EURUSD", tick: baseTick });
        await Promise.resolve();
        await Promise.resolve();

        stream.stop();

        expect(events).toHaveLength(7);
    });

    it("does not republish when bucket is already processed", async () => {
        const service = {
            get_last_closed_candle: vi.fn().mockResolvedValue(baseCandles[0]),
        } as unknown as MarketDataService;

        const eventBus = new MarketDataEventBus();
        let calls = 0;
        eventBus.subscribe("CandleClosed", () => {
            calls += 1;
        });

        const stream = new CandleStream(service, eventBus, createLoggerMock());
        stream.start();

        eventBus.publish("TickReceived", { symbol: "EURUSD", tick: baseTick });
        await Promise.resolve();
        await Promise.resolve();
        eventBus.publish("TickReceived", { symbol: "EURUSD", tick: baseTick });
        await Promise.resolve();
        await Promise.resolve();

        stream.stop();

        expect(calls).toBe(7);
    });
});
