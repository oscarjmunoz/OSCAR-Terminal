import { MarketDataEventBus } from "./EventBus";
import { ConsoleLogger } from "./logger";
import { MarketCache } from "./MarketCache";
import { MT5Connector } from "./MT5Connector";
import { Logger, MarketCandle, MarketTimeframe, TimeSource } from "./types";

const SUPPORTED_TIMEFRAMES: MarketTimeframe[] = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];

export class HistoryLoader {
    constructor(
        private readonly connector: MT5Connector,
        private readonly cache: MarketCache,
        private readonly eventBus: MarketDataEventBus,
        private readonly logger: Logger = new ConsoleLogger(),
        private readonly timeSource: TimeSource = { now: () => performance.now() }
    ) { }

    async loadCandles(symbol: string, timeframe: MarketTimeframe, count: number): Promise<MarketCandle[]> {
        if (!SUPPORTED_TIMEFRAMES.includes(timeframe)) {
            throw new Error(`Unsupported timeframe: ${timeframe}`);
        }

        const cached = this.cache.getCandles(symbol, timeframe, count);
        if (cached) {
            return cached;
        }

        const startedAt = this.timeSource.now();
        const candles = await this.connector.getCandles(symbol, timeframe, count);
        const latencyMs = this.timeSource.now() - startedAt;

        this.cache.setCandles(symbol, timeframe, candles);
        this.eventBus.publish("HistoryLoaded", { symbol, timeframe, count: candles.length, latencyMs });
        this.logger.info("MT5 history loaded", { symbol, timeframe, count: candles.length, latencyMs });

        return candles;
    }
}