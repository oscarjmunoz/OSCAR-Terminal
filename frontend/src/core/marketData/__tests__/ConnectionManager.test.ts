import { describe, expect, it, vi } from "vitest";

import { ConnectionManager } from "../ConnectionManager";
import { MT5DisconnectedError, MT5LoginError } from "../errors";
import { MarketDataEventBus } from "../EventBus";
import { MT5Connector } from "../MT5Connector";
import { createBridge, createLoggerMock, createSettings } from "./testUtils";

describe("ConnectionManager", () => {
    it("transitions to CONNECTED and publishes ConnectionEstablished", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const eventBus = new MarketDataEventBus();
        const events: string[] = [];
        eventBus.subscribe("ConnectionEstablished", (event) => events.push(event.type));
        const manager = new ConnectionManager(connector, createSettings(), eventBus, createLoggerMock(), { sleep: async () => undefined }, () => 0);

        await manager.connect();

        expect(manager.getState()).toBe("CONNECTED");
        expect(events).toEqual(["ConnectionEstablished"]);
    });

    it("moves to ERROR on invalid login without retrying", async () => {
        const bridge = createBridge({ login: async () => false });
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const manager = new ConnectionManager(connector, createSettings(), new MarketDataEventBus(), createLoggerMock(), { sleep: async () => undefined }, () => 0);

        await expect(manager.connect()).rejects.toBeInstanceOf(MT5LoginError);
        expect(manager.getState()).toBe("ERROR");
    });

    it("reconnects with exponential backoff after a disconnection", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const eventBus = new MarketDataEventBus();
        const sleep = vi.fn().mockResolvedValue(undefined);
        const manager = new ConnectionManager(
            connector,
            createSettings({ reconnectIntervalMs: 10, reconnectMaxAttempts: 3, healthCheckIntervalMs: 0 }),
            eventBus,
            createLoggerMock(),
            { sleep },
            () => 0
        );

        await manager.handleConnectionError(new MT5DisconnectedError("stream closed"));

        expect(sleep).toHaveBeenCalledWith(10);
        expect(bridge.initialize).toHaveBeenCalledOnce();
        expect(bridge.login).toHaveBeenCalledOnce();
        expect(manager.getState()).toBe("CONNECTED");
    });

    it("stops retrying after exhausting reconnect attempts", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());
        const manager = new ConnectionManager(
            connector,
            createSettings({ reconnectIntervalMs: 5, reconnectMaxAttempts: 2 }),
            new MarketDataEventBus(),
            createLoggerMock(),
            { sleep: async () => undefined },
            () => 0
        );

        vi.spyOn(connector, "reconnect").mockRejectedValue(new MT5DisconnectedError("still offline"));

        await expect(manager.handleConnectionError(new MT5DisconnectedError("offline"))).rejects.toBeInstanceOf(MT5DisconnectedError);
        expect(manager.getState()).toBe("ERROR");
    });
});