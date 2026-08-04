import { describe, expect, it } from "vitest";

import { MarketDataEventBus } from "../EventBus";
import { baseTick } from "./testUtils";

describe("MarketDataEventBus", () => {
    it("publishes typed immutable events", () => {
        const bus = new MarketDataEventBus();
        let capturedSpread = 0;

        bus.subscribe("TickReceived", (event) => {
            capturedSpread = event.payload.tick.spread;
            expect(Object.isFrozen(event)).toBe(true);
            expect(Object.isFrozen(event.payload)).toBe(true);
            expect(() => {
                (event.payload.tick as { spread: number }).spread = 999;
            }).toThrow();
        });

        bus.publish("TickReceived", { symbol: "EURUSD", tick: baseTick });
        expect(capturedSpread).toBe(baseTick.spread);
    });

    it("removes handlers through the unsubscribe callback", () => {
        const bus = new MarketDataEventBus();
        let calls = 0;
        const unsubscribe = bus.subscribe("ConnectionLost", () => {
            calls += 1;
        });

        unsubscribe();
        bus.publish("ConnectionLost", { state: "RECONNECTING", reason: "offline" });

        expect(calls).toBe(0);
    });

    it("publishes immutable DecisionContextUpdated events", () => {
        const bus = new MarketDataEventBus();
        let captured = "";

        bus.subscribe("DecisionContextUpdated", (event) => {
            captured = event.payload.context.source;
            expect(Object.isFrozen(event)).toBe(true);
            expect(Object.isFrozen(event.payload)).toBe(true);
            expect(() => {
                (event.payload.context as { source: string }).source = "MUTATED";
            }).toThrow();
        });

        bus.publish("DecisionContextUpdated", {
            symbol: "EURUSD",
            timeframe: "M5",
            context: {
                header: {
                    symbol: "EURUSD",
                    timeframe: "M5",
                    date: "2026-01-01",
                    session: "LONDON",
                    connection: "LIVE",
                    latencyMs: 1,
                },
                score: {
                    institutionalScore: 80,
                    confidence: 70,
                    bias: "LONG",
                    recommendation: "BUY",
                },
                risk: {
                    grade: "LOW",
                    rr: "1:2",
                    capitalRisk: "0.5%",
                    stopDistance: "0.001",
                },
                liquidity: {
                    sweep: "yes",
                    internal: "yes",
                    external: "yes",
                    levels: ["BSL @ 1.10000"],
                },
                structure: {
                    bos: "yes",
                    choch: "no",
                    mss: "no",
                    trend: "BULLISH",
                },
                context: {
                    orderBlocks: [],
                    fvg: [],
                    breaker: "n/a",
                    mitigation: "n/a",
                    premium: "n/a",
                    discount: "n/a",
                },
                narrative: "test",
                warnings: [],
                execution: null,
                confluences: {
                    liquidity: 0,
                    structure: 0,
                    risk: 0,
                    context: 0,
                },
                source: "INSTITUTIONAL_PIPELINE",
            },
            latencyMs: 1,
            pipelineLatencyMs: 2,
            updatedAt: Date.now(),
        });

        expect(captured).toBe("INSTITUTIONAL_PIPELINE");
    });
});