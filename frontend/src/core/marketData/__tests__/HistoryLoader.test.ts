import { describe, expect, it } from "vitest";

import { MarketDataEventBus } from "../EventBus";
import { HistoryLoader } from "../HistoryLoader";
import { MarketCache } from "../MarketCache";
import { MT5Connector } from "../MT5Connector";
import { MarketTimeframe } from "../types";
import { createBridge, createLoggerMock, createSettings } from "./testUtils";

describe("HistoryLoader", () => {
    it("loads historical candles, caches them and publishes HistoryLoaded", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const cache = new MarketCache(1_000, { now: () => 0 });
        const eventBus = new MarketDataEventBus();
        const events: string[] = [];
        eventBus.subscribe("HistoryLoaded", (event) => events.push(`${event.payload.symbol}:${event.payload.timeframe}`));
        const loader = new HistoryLoader(connector, cache, eventBus, createLoggerMock(), { now: () => 15 });

        const candles = await loader.loadCandles("EURUSD", "M5", 2);

        expect(candles).toHaveLength(2);
        expect(cache.getCandles("EURUSD", "M5", 2)).toHaveLength(2);
        expect(events).toEqual(["EURUSD:M5"]);
    });

    it("reuses cached history for repeated requests", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const loader = new HistoryLoader(connector, new MarketCache(1_000, { now: () => 0 }), new MarketDataEventBus(), createLoggerMock(), { now: () => 1 });

        await loader.loadCandles("EURUSD", "H1", 2);
        await loader.loadCandles("EURUSD", "H1", 2);

        expect(bridge.getCandles).toHaveBeenCalledTimes(1);
    });

    it("rejects unsupported timeframes", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const loader = new HistoryLoader(connector, new MarketCache(1_000, { now: () => 0 }), new MarketDataEventBus(), createLoggerMock(), { now: () => 1 });

        await expect(loader.loadCandles("EURUSD", "W1" as MarketTimeframe, 2)).rejects.toThrow("Unsupported timeframe");
    });
});