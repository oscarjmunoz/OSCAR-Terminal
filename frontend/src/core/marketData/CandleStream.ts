import { MarketDataEvent } from "./events";
import { MarketDataEventBus } from "./EventBus";
import { ConsoleLogger } from "./logger";
import { MarketDataService } from "./MarketDataService";
import { Logger, MarketTimeframe, MarketTick } from "./types";

const SUPPORTED_TIMEFRAMES: readonly MarketTimeframe[] = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];

const TIMEFRAME_TO_MS: Record<MarketTimeframe, number> = {
    M1: 60_000,
    M5: 300_000,
    M15: 900_000,
    M30: 1_800_000,
    H1: 3_600_000,
    H4: 14_400_000,
    D1: 86_400_000,
};

function buildFrameKey(symbol: string, timeframe: MarketTimeframe): string {
    return `${symbol}:${timeframe}`;
}

function resolveBucketEnd(timestampMs: number, timeframe: MarketTimeframe): number {
    const frameMs = TIMEFRAME_TO_MS[timeframe];
    return Math.floor(timestampMs / frameMs) * frameMs;
}

export class CandleStream {
    private unsubscribeTickReceived: (() => void) | null = null;
    private processingQueue = Promise.resolve();
    private readonly lastPublishedBucket = new Map<string, number>();

    constructor(
        private readonly service: MarketDataService,
        private readonly eventBus: MarketDataEventBus,
        private readonly logger: Logger = new ConsoleLogger()
    ) { }

    start(): void {
        if (this.unsubscribeTickReceived) {
            return;
        }

        this.unsubscribeTickReceived = this.eventBus.subscribe("TickReceived", (event) => {
            this.processingQueue = this.processingQueue.then(async () => {
                await this.processTickEvent(event);
            });
        });

        this.logger.info("CandleStream started", { timeframes: SUPPORTED_TIMEFRAMES.join(",") });
    }

    stop(): void {
        if (!this.unsubscribeTickReceived) {
            return;
        }

        this.unsubscribeTickReceived();
        this.unsubscribeTickReceived = null;
        this.logger.info("CandleStream stopped");
    }

    private async processTickEvent(event: MarketDataEvent<"TickReceived">): Promise<void> {
        const { symbol, tick } = event.payload;

        await Promise.all(
            SUPPORTED_TIMEFRAMES.map((timeframe) => this.tryPublishClosedCandle(symbol, timeframe, tick))
        );
    }

    private async tryPublishClosedCandle(symbol: string, timeframe: MarketTimeframe, tick: MarketTick): Promise<void> {
        const tickTimestampMs = this.normalizeTickTimestamp(tick.timestamp);
        const closedBucket = resolveBucketEnd(tickTimestampMs, timeframe);
        const key = buildFrameKey(symbol, timeframe);
        const previousBucket = this.lastPublishedBucket.get(key) ?? Number.NEGATIVE_INFINITY;

        if (closedBucket <= previousBucket) {
            return;
        }

        const closed = await this.service.get_last_closed_candle(symbol, timeframe, { emitEvent: false });
        if (!closed) {
            return;
        }

        const closedTime = Date.parse(closed.time);
        if (!Number.isFinite(closedTime) || closedTime <= previousBucket) {
            return;
        }

        this.lastPublishedBucket.set(key, closedTime);

        this.eventBus.publish("CandleClosed", {
            symbol,
            timeframe,
            candle: closed,
        });
    }

    private normalizeTickTimestamp(timestamp: number): number {
        if (timestamp > 10_000_000_000) {
            return timestamp;
        }

        return timestamp * 1000;
    }
}
