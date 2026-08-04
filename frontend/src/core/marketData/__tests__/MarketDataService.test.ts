import { describe, expect, it, vi } from "vitest";

import { MT5DisconnectedError } from "../errors";
import { baseCandles, baseStatus, baseSymbolInfo, baseTick, createBridge, createLoggerMock, createServiceHarness } from "./testUtils";

describe("MarketDataService", () => {
    it("returns the cached latest tick before hitting MT5 again", async () => {
        const harness = createServiceHarness();

        const first = await harness.service.get_latest_tick("EURUSD");
        const second = await harness.service.get_latest_tick("EURUSD");

        expect(first).toEqual(baseTick);
        expect(second).toEqual(baseTick);
        expect(harness.bridge.getLatestTick).toHaveBeenCalledTimes(1);
    });

    it("returns the last closed candle when the latest candle is still open", async () => {
        const harness = createServiceHarness();

        const candle = await harness.service.get_last_closed_candle("EURUSD", "M5");

        expect(candle).toEqual(baseCandles[0]);
    });

    it("caches symbol info and market status", async () => {
        const harness = createServiceHarness();

        const info = await harness.service.get_symbol_info("EURUSD");
        const status = await harness.service.get_market_status("EURUSD");
        await harness.service.get_symbol_info("EURUSD");
        await harness.service.get_market_status("EURUSD");

        expect(info).toEqual(baseSymbolInfo);
        expect(status).toEqual(baseStatus);
        expect(harness.bridge.getSymbolInfo).toHaveBeenCalledTimes(1);
        expect(harness.bridge.getMarketStatus).toHaveBeenCalledTimes(1);
    });

    it("retries the operation after reconnecting from a disconnection", async () => {
        const bridge = createBridge({
            getLatestTick: vi
                .fn()
                .mockRejectedValueOnce(new MT5DisconnectedError("feed dropped"))
                .mockResolvedValueOnce(baseTick),
        });
        const harness = createServiceHarness({ bridge });

        const tick = await harness.service.get_latest_tick("EURUSD");

        expect(tick).toEqual(baseTick);
        expect(harness.bridge.getLatestTick).toHaveBeenCalledTimes(2);
    });

    it("loads ticks from MT5 when cache is empty", async () => {
        const harness = createServiceHarness({ bridge: createBridge({ getTicks: vi.fn().mockResolvedValue([baseTick]) }) });

        const ticks = await harness.service.get_ticks("EURUSD", 1);

        expect(ticks).toEqual([baseTick]);
    });
});