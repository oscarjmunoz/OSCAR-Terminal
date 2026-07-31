import { describe, expect, it } from "vitest";

import { runBacktest } from "../BacktestEngine";
import { ValidationRecord } from "../../validation/types";

const baseRecord: ValidationRecord = {
  timestamp: Math.floor(new Date("2026-01-01T00:00:00Z").getTime() / 1000),
  symbol: "USDCHF",
  timeframe: "M5",
  score: 80,
  decision: "BUY",
  confidence: 85,
};

describe("BacktestEngine", () => {
  it("returns one win when TP is hit", () => {
    const result = runBacktest({
      records: [baseRecord],
      candles: [
        { time: "2026-01-01T00:00:00Z", open: 1, high: 1.001, low: 0.999, close: 1, tick_volume: 10 },
        { time: "2026-01-01T00:05:00Z", open: 1, high: 1.0045, low: 0.9998, close: 1.003, tick_volume: 12 },
      ],
    });

    expect(result.totalSignals).toBe(1);
    expect(result.wins).toBe(1);
    expect(result.losses).toBe(0);
    expect(result.equityCurve.length).toBe(1);
  });

  it("returns one loss when SL is hit", () => {
    const result = runBacktest({
      records: [
        {
          ...baseRecord,
          decision: "SELL",
          timestamp: Math.floor(new Date("2026-01-01T01:00:00Z").getTime() / 1000),
        },
      ],
      candles: [
        { time: "2026-01-01T01:00:00Z", open: 1, high: 1.001, low: 0.999, close: 1, tick_volume: 10 },
        { time: "2026-01-01T01:05:00Z", open: 1, high: 1.0025, low: 0.9995, close: 1.002, tick_volume: 12 },
      ],
    });

    expect(result.totalSignals).toBe(1);
    expect(result.wins).toBe(0);
    expect(result.losses).toBe(1);
  });
});
