import { describe, expect, it } from "vitest";

import { MarketCache } from "../MarketCache";
import { baseCandles, baseStatus, baseSymbolInfo, baseTick } from "./testUtils";

describe("MarketCache", () => {
    it("stores and expires ticks by TTL", () => {
        let now = 0;
        const cache = new MarketCache(100, { now: () => now });

        cache.setTicks("EURUSD", [baseTick]);
        expect(cache.getLatestTick("EURUSD")).toEqual(baseTick);

        now = 101;
        expect(cache.getTicks("EURUSD")).toBeNull();
        expect(cache.getLatestTick("EURUSD")).toBeNull();
    });

    it("returns cached candle slices when enough history is available", () => {
        const cache = new MarketCache(100, { now: () => 0 });
        cache.setCandles("EURUSD", "M5", [...baseCandles, { ...baseCandles[0], time: "2026-01-01T00:10:00Z" }]);

        expect(cache.getCandles("EURUSD", "M5", 2)).toHaveLength(2);
        expect(cache.getCandles("EURUSD", "M5", 4)).toBeNull();
    });

    it("separates symbol info and market status entries", () => {
        const cache = new MarketCache(100, { now: () => 0 });
        cache.setSymbolInfo("EURUSD", baseSymbolInfo);
        cache.setMarketStatus("EURUSD", baseStatus);

        expect(cache.getSymbolInfo("EURUSD")).toEqual(baseSymbolInfo);
        expect(cache.getMarketStatus("EURUSD")).toEqual(baseStatus);
    });
});