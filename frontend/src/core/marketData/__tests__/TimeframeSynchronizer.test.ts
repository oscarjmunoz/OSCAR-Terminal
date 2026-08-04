import { describe, expect, it } from "vitest";

import { MarketDataEventBus } from "../EventBus";
import { TimeframeSynchronizer } from "../TimeframeSynchronizer";
import { MarketTimeframe } from "../types";
import { baseCandles } from "./testUtils";

const TIMEFRAMES: MarketTimeframe[] = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];

describe("TimeframeSynchronizer", () => {
    it("publishes TimeframeUpdated and marks synchronized after all frames are present", () => {
        const eventBus = new MarketDataEventBus();
        const synchronizer = new TimeframeSynchronizer(eventBus);
        const synchronizedFlags: boolean[] = [];

        eventBus.subscribe("TimeframeUpdated", (event) => {
            synchronizedFlags.push(event.payload.synchronized);
        });

        synchronizer.start();

        TIMEFRAMES.forEach((timeframe, index) => {
            eventBus.publish("CandleClosed", {
                symbol: "EURUSD",
                timeframe,
                candle: {
                    ...baseCandles[0],
                    time: `2026-01-01T00:0${index}:00Z`,
                },
            });
        });

        synchronizer.stop();

        expect(synchronizedFlags[0]).toBe(false);
        expect(synchronizedFlags[synchronizedFlags.length - 1]).toBe(true);
    });
});
