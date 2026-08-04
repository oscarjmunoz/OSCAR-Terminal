import { ConnectionManager } from "./ConnectionManager";
import { MarketDataEventBus } from "./EventBus";
import { HistoryLoader } from "./HistoryLoader";
import { ConsoleLogger } from "./logger";
import { MarketCache } from "./MarketCache";
import { MT5Connector } from "./MT5Connector";
import { Logger, MarketCandle, MarketDataSettings, MarketStatus, MarketSymbolInfo, MarketTick, MarketTimeframe } from "./types";

export class MarketDataService {
    constructor(
        private readonly connectionManager: ConnectionManager,
        private readonly connector: MT5Connector,
        private readonly historyLoader: HistoryLoader,
        private readonly cache: MarketCache,
        private readonly settings: MarketDataSettings,
        private readonly eventBus: MarketDataEventBus,
        private readonly logger: Logger = new ConsoleLogger()
    ) { }

    async get_ticks(symbol: string, count = 1): Promise<MarketTick[]> {
        const cached = this.cache.getTicks(symbol, count);
        if (cached && cached.length >= count) {
            return cached;
        }

        return this.executeWithReconnect(async () => {
            const ticks = await this.connector.getTicks(symbol, count);
            this.cache.setTicks(symbol, ticks);
            if (ticks[0]) {
                this.eventBus.publish("TickReceived", { symbol, tick: ticks[0] });
            }
            this.logger.debug("MT5 ticks loaded", { symbol, count: ticks.length });
            return ticks;
        });
    }

    async get_latest_tick(symbol: string): Promise<MarketTick | null> {
        const cached = this.cache.getLatestTick(symbol);
        if (cached) {
            return cached;
        }

        return this.executeWithReconnect(async () => {
            const tick = await this.connector.getLatestTick(symbol);
            if (tick) {
                this.cache.setLatestTick(symbol, tick);
                this.eventBus.publish("TickReceived", { symbol, tick });
            }
            return tick;
        });
    }

    async get_candles(symbol: string, timeframe: MarketTimeframe, count = this.settings.historySize): Promise<MarketCandle[]> {
        return this.executeWithReconnect(() => this.historyLoader.loadCandles(symbol, timeframe, count));
    }

    async get_last_closed_candle(
        symbol: string,
        timeframe: MarketTimeframe,
        options: { emitEvent?: boolean } = {}
    ): Promise<MarketCandle | null> {
        const candles = await this.get_candles(symbol, timeframe, 2);
        if (candles.length === 0) {
            return null;
        }

        const latest = candles[candles.length - 1];
        const lastClosed = latest.isClosed === false ? candles[candles.length - 2] ?? null : latest;
        const emitEvent = options.emitEvent ?? true;
        if (lastClosed && emitEvent) {
            this.eventBus.publish("CandleClosed", { symbol, timeframe, candle: lastClosed });
        }

        return lastClosed;
    }

    async get_symbol_info(symbol: string): Promise<MarketSymbolInfo | null> {
        const cached = this.cache.getSymbolInfo(symbol);
        if (cached) {
            return cached;
        }

        return this.executeWithReconnect(async () => {
            const info = await this.connector.getSymbolInfo(symbol);
            if (info) {
                this.cache.setSymbolInfo(symbol, info);
            }
            return info;
        });
    }

    async get_market_status(symbol: string): Promise<MarketStatus> {
        const cached = this.cache.getMarketStatus(symbol);
        if (cached) {
            return cached;
        }

        return this.executeWithReconnect(async () => {
            const status = await this.connector.getMarketStatus(symbol);
            this.cache.setMarketStatus(symbol, status);
            this.eventBus.publish("MarketUpdated", { symbol, status });
            return status;
        });
    }

    private async executeWithReconnect<TValue>(operation: () => Promise<TValue>): Promise<TValue> {
        await this.connectionManager.ensureConnection();

        try {
            return await operation();
        } catch (error) {
            await this.connectionManager.handleConnectionError(error);
            return operation();
        }
    }
}