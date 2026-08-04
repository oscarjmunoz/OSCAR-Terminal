import { ConnectionManager } from "./ConnectionManager";
import { MarketDataEventBus } from "./EventBus";
import { ConsoleLogger } from "./logger";
import { MarketDataService } from "./MarketDataService";
import { Logger, MarketDataSettings, MarketTick } from "./types";

interface TimerPort {
    setTimeout(handler: () => void, timeoutMs: number): ReturnType<typeof setTimeout>;
    clearTimeout(handle: ReturnType<typeof setTimeout>): void;
}

const DEFAULT_TIMER_PORT: TimerPort = {
    setTimeout(handler, timeoutMs) {
        return setTimeout(handler, timeoutMs);
    },
    clearTimeout(handle) {
        clearTimeout(handle);
    },
};

export class TickStream {
    private running = false;
    private symbol: string | null = null;
    private loopHandle: ReturnType<typeof setTimeout> | null = null;
    private flushHandle: ReturnType<typeof setTimeout> | null = null;
    private readonly tickBatch: MarketTick[] = [];
    private lastRateWindowStartedAt = 0;
    private rateWindowTicks = 0;
    private reconnects = 0;

    constructor(
        private readonly service: MarketDataService,
        private readonly connectionManager: ConnectionManager,
        private readonly eventBus: MarketDataEventBus,
        private readonly settings: MarketDataSettings,
        private readonly logger: Logger = new ConsoleLogger(),
        private readonly now: () => number = Date.now,
        private readonly timer: TimerPort = DEFAULT_TIMER_PORT
    ) { }

    async start(symbol: string): Promise<void> {
        if (this.running) {
            return;
        }

        this.running = true;
        this.symbol = symbol;
        this.lastRateWindowStartedAt = this.now();
        this.rateWindowTicks = 0;
        this.reconnects = 0;

        await this.connectionManager.ensureConnection();
        this.logger.info("TickStream started", { symbol });
        this.scheduleNextTickPoll(0);
    }

    stop(): void {
        if (!this.running) {
            return;
        }

        this.running = false;
        this.symbol = null;

        if (this.loopHandle) {
            this.timer.clearTimeout(this.loopHandle);
            this.loopHandle = null;
        }

        if (this.flushHandle) {
            this.timer.clearTimeout(this.flushHandle);
            this.flushHandle = null;
        }

        this.flushTickBatch();
        this.logger.info("TickStream stopped");
    }

    private scheduleNextTickPoll(delayMs: number): void {
        if (!this.running) {
            return;
        }

        this.loopHandle = this.timer.setTimeout(() => {
            void this.pollOnce();
        }, Math.max(0, delayMs));
    }

    private scheduleBatchFlush(): void {
        if (this.flushHandle) {
            return;
        }

        this.flushHandle = this.timer.setTimeout(() => {
            this.flushHandle = null;
            this.flushTickBatch();
        }, this.settings.tickBatchFlushIntervalMs);
    }

    private logTickRateIfWindowEnded(): void {
        const elapsedMs = this.now() - this.lastRateWindowStartedAt;
        if (elapsedMs < this.settings.tickRateLogIntervalMs) {
            return;
        }

        const seconds = elapsedMs / 1000;
        const tickRate = seconds > 0 ? this.rateWindowTicks / seconds : 0;
        this.logger.info("TickStream rate", {
            tickRate,
            ticks: this.rateWindowTicks,
            elapsedMs,
            reconnects: this.reconnects,
        });

        this.lastRateWindowStartedAt = this.now();
        this.rateWindowTicks = 0;
    }

    private async pollOnce(): Promise<void> {
        const activeSymbol = this.symbol;
        if (!this.running || !activeSymbol) {
            return;
        }

        try {
            const tick = await this.service.get_latest_tick(activeSymbol);

            if (tick) {
                this.rateWindowTicks += 1;
                this.eventBus.publish("TickReceived", { symbol: activeSymbol, tick });
                this.pushTickToBatch(activeSymbol, tick);
                this.logTickRateIfWindowEnded();
            }
        } catch (error) {
            this.reconnects += 1;
            this.logger.warn("TickStream polling failed", {
                symbol: activeSymbol,
                reconnects: this.reconnects,
                reason: error instanceof Error ? error.message : "unknown",
            });

            await this.connectionManager.handleConnectionError(error);
        } finally {
            this.scheduleNextTickPoll(this.settings.tickPollIntervalMs);
        }
    }

    private pushTickToBatch(symbol: string, tick: MarketTick): void {
        this.tickBatch.push({ ...tick });
        if (this.tickBatch.length >= this.settings.tickBatchMaxSize) {
            this.flushTickBatch(symbol);
            return;
        }

        this.scheduleBatchFlush();
    }

    private flushTickBatch(symbol?: string): void {
        if (this.tickBatch.length === 0) {
            return;
        }

        const activeSymbol = symbol ?? this.symbol;
        if (!activeSymbol) {
            this.tickBatch.length = 0;
            return;
        }

        const ticks = this.tickBatch.splice(0, this.tickBatch.length);

        this.eventBus.publish("TickBatchReceived", {
            symbol: activeSymbol,
            ticks,
        });
    }
}
