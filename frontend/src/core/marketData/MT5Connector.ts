import {
    mapToTypedConnectorError,
    MT5HealthCheckError,
    MT5LoginError,
    MT5ReconnectError,
} from "./errors";
import { ConsoleLogger } from "./logger";
import { Logger, MarketCandle, MarketDataSettings, MarketStatus, MarketSymbolInfo, MarketTick, MarketTimeframe, Mt5Bridge, ConnectionHealth } from "./types";

export class MT5Connector {
    private readonly logger: Logger;
    private initialized = false;

    constructor(
        private readonly bridge: Mt5Bridge,
        private readonly settings: MarketDataSettings,
        logger: Logger = new ConsoleLogger()
    ) {
        this.logger = logger;
    }

    async initialize(): Promise<void> {
        try {
            const ready = await this.bridge.initialize(this.settings.terminalPath);
            if (!ready) {
                throw new Error("MT5 initialize returned false");
            }

            this.initialized = true;
            this.logger.info("MT5 initialized", { terminalPath: this.settings.terminalPath });
        } catch (error) {
            throw mapToTypedConnectorError("initialize", error);
        }
    }

    async login(): Promise<void> {
        try {
            const authenticated = await this.bridge.login(this.settings.credentials);
            if (!authenticated) {
                throw new MT5LoginError();
            }

            this.logger.info("MT5 login succeeded", { login: this.settings.credentials.login, server: this.settings.credentials.server });
        } catch (error) {
            throw mapToTypedConnectorError("login", error);
        }
    }

    async shutdown(): Promise<void> {
        try {
            await this.bridge.shutdown();
            this.initialized = false;
            this.logger.info("MT5 shutdown completed");
        } catch (error) {
            throw mapToTypedConnectorError("shutdown", error);
        }
    }

    async reconnect(): Promise<void> {
        try {
            if (this.initialized) {
                await this.bridge.shutdown();
            }

            this.initialized = false;
            await this.initialize();
            await this.login();
            this.logger.info("MT5 reconnect succeeded");
        } catch (error) {
            throw new MT5ReconnectError(error instanceof Error ? error.message : "MT5 reconnect failed", { cause: error });
        }
    }

    async health_check(): Promise<ConnectionHealth> {
        try {
            const health = await this.bridge.healthCheck();
            if (!health.ok) {
                throw new MT5HealthCheckError(health.message ?? "MT5 health check failed");
            }

            this.logger.debug("MT5 health check succeeded", { latencyMs: health.latencyMs });
            return health;
        } catch (error) {
            throw mapToTypedConnectorError("health_check", error);
        }
    }

    async getTicks(symbol: string, count: number): Promise<MarketTick[]> {
        try {
            return await this.bridge.getTicks(symbol, count);
        } catch (error) {
            throw mapToTypedConnectorError("get_ticks", error);
        }
    }

    async getLatestTick(symbol: string): Promise<MarketTick | null> {
        try {
            return await this.bridge.getLatestTick(symbol);
        } catch (error) {
            throw mapToTypedConnectorError("get_latest_tick", error);
        }
    }

    async getCandles(symbol: string, timeframe: MarketTimeframe, count: number): Promise<MarketCandle[]> {
        try {
            return await this.bridge.getCandles(symbol, timeframe, count);
        } catch (error) {
            throw mapToTypedConnectorError("get_candles", error);
        }
    }

    async getSymbolInfo(symbol: string): Promise<MarketSymbolInfo | null> {
        try {
            return await this.bridge.getSymbolInfo(symbol);
        } catch (error) {
            throw mapToTypedConnectorError("get_symbol_info", error);
        }
    }

    async getMarketStatus(symbol: string): Promise<MarketStatus> {
        try {
            return await this.bridge.getMarketStatus(symbol);
        } catch (error) {
            throw mapToTypedConnectorError("get_market_status", error);
        }
    }
}