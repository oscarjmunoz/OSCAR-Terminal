import { describe, expect, it } from "vitest";

import { MT5LoginError, MT5TimeoutError } from "../errors";
import { MT5Connector } from "../MT5Connector";
import { createBridge, createLoggerMock, createSettings } from "./testUtils";

describe("MT5Connector", () => {
    it("initializes, logs in and shuts down through the bridge", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());

        await connector.initialize();
        await connector.login();
        await connector.shutdown();

        expect(bridge.initialize).toHaveBeenCalledOnce();
        expect(bridge.login).toHaveBeenCalledOnce();
        expect(bridge.shutdown).toHaveBeenCalledOnce();
    });

    it("throws a typed error on invalid login", async () => {
        const bridge = createBridge({ login: async () => false });
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());

        await expect(connector.login()).rejects.toBeInstanceOf(MT5LoginError);
    });

    it("reconnects by reinitializing the bridge", async () => {
        const bridge = createBridge();
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());

        await connector.initialize();
        await connector.reconnect();

        expect(bridge.shutdown).toHaveBeenCalledOnce();
        expect(bridge.initialize).toHaveBeenCalledTimes(2);
        expect(bridge.login).toHaveBeenCalledOnce();
    });

    it("maps timeout failures during health checks", async () => {
        const bridge = createBridge({
            healthCheck: async () => {
                throw { code: "TIMEOUT", message: "slow response" };
            },
        });
        const connector = new MT5Connector(bridge, createSettings(), createLoggerMock());

        await expect(connector.health_check()).rejects.toBeInstanceOf(MT5TimeoutError);
    });
});