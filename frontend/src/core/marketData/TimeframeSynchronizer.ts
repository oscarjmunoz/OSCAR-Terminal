import { MarketDataEvent } from "./events";
import { MarketDataEventBus } from "./EventBus";
import { ConsoleLogger } from "./logger";
import { Logger, MarketTimeframe } from "./types";

const SUPPORTED_TIMEFRAMES: readonly MarketTimeframe[] = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];

function buildKey(symbol: string): string {
    return symbol;
}

export class TimeframeSynchronizer {
    private unsubscribeCandleClosed: (() => void) | null = null;
    private readonly latestClosedAt = new Map<string, Partial<Record<MarketTimeframe, string>>>();

    constructor(
        private readonly eventBus: MarketDataEventBus,
        private readonly logger: Logger = new ConsoleLogger()
    ) { }

    start(): void {
        if (this.unsubscribeCandleClosed) {
            return;
        }

        this.unsubscribeCandleClosed = this.eventBus.subscribe("CandleClosed", (event) => {
            this.handleCandleClosed(event);
        });

        this.logger.info("TimeframeSynchronizer started");
    }

    stop(): void {
        if (!this.unsubscribeCandleClosed) {
            return;
        }

        this.unsubscribeCandleClosed();
        this.unsubscribeCandleClosed = null;
        this.logger.info("TimeframeSynchronizer stopped");
    }

    private handleCandleClosed(event: MarketDataEvent<"CandleClosed">): void {
        const { symbol, timeframe, candle } = event.payload;
        const key = buildKey(symbol);
        const current = this.latestClosedAt.get(key) ?? {};

        current[timeframe] = candle.time;
        this.latestClosedAt.set(key, current);

        const synchronized = SUPPORTED_TIMEFRAMES.every((frame) => typeof current[frame] === "string");

        this.eventBus.publish("TimeframeUpdated", {
            symbol,
            timeframe,
            candle,
            synchronized,
            latestClosedAt: {
                M1: current.M1 ?? null,
                M5: current.M5 ?? null,
                M15: current.M15 ?? null,
                M30: current.M30 ?? null,
                H1: current.H1 ?? null,
                H4: current.H4 ?? null,
                D1: current.D1 ?? null,
            },
        });
    }
}
