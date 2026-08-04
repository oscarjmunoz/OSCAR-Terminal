import { Clock, MarketCandle, MarketStatus, MarketSymbolInfo, MarketTick, MarketTimeframe } from "./types";

type CacheEntry<TValue> = {
    value: TValue;
    expiresAt: number;
};

function buildCandleKey(symbol: string, timeframe: MarketTimeframe): string {
    return `${symbol}:${timeframe}`;
}

export class MarketCache {
    private readonly ticks = new Map<string, CacheEntry<MarketTick[]>>();
    private readonly latestTicks = new Map<string, CacheEntry<MarketTick>>();
    private readonly candles = new Map<string, CacheEntry<MarketCandle[]>>();
    private readonly symbolInfo = new Map<string, CacheEntry<MarketSymbolInfo>>();
    private readonly marketStatus = new Map<string, CacheEntry<MarketStatus>>();

    constructor(
        private readonly ttlMs: number,
        private readonly clock: Clock = { now: () => Date.now() }
    ) { }

    getTicks(symbol: string, count?: number): MarketTick[] | null {
        const entry = this.read(this.ticks, symbol);
        if (!entry) {
            return null;
        }

        return typeof count === "number" ? entry.slice(0, count) : entry;
    }

    setTicks(symbol: string, ticks: MarketTick[]): void {
        this.write(this.ticks, symbol, [...ticks]);
        if (ticks[0]) {
            this.setLatestTick(symbol, ticks[0]);
        }
    }

    getLatestTick(symbol: string): MarketTick | null {
        return this.read(this.latestTicks, symbol) ?? null;
    }

    setLatestTick(symbol: string, tick: MarketTick): void {
        this.write(this.latestTicks, symbol, { ...tick });
    }

    getCandles(symbol: string, timeframe: MarketTimeframe, count?: number): MarketCandle[] | null {
        const entry = this.read(this.candles, buildCandleKey(symbol, timeframe));
        if (!entry) {
            return null;
        }

        if (typeof count === "number" && entry.length < count) {
            return null;
        }

        return typeof count === "number" ? entry.slice(0, count) : entry;
    }

    setCandles(symbol: string, timeframe: MarketTimeframe, candles: MarketCandle[]): void {
        this.write(this.candles, buildCandleKey(symbol, timeframe), candles.map((candle) => ({ ...candle })));
    }

    getSymbolInfo(symbol: string): MarketSymbolInfo | null {
        return this.read(this.symbolInfo, symbol) ?? null;
    }

    setSymbolInfo(symbol: string, info: MarketSymbolInfo): void {
        this.write(this.symbolInfo, symbol, { ...info });
    }

    getMarketStatus(symbol: string): MarketStatus | null {
        return this.read(this.marketStatus, symbol) ?? null;
    }

    setMarketStatus(symbol: string, status: MarketStatus): void {
        this.write(this.marketStatus, symbol, { ...status });
    }

    clear(): void {
        this.ticks.clear();
        this.latestTicks.clear();
        this.candles.clear();
        this.symbolInfo.clear();
        this.marketStatus.clear();
    }

    private read<TValue>(store: Map<string, CacheEntry<TValue>>, key: string): TValue | null {
        const entry = store.get(key);
        if (!entry) {
            return null;
        }

        if (entry.expiresAt <= this.clock.now()) {
            store.delete(key);
            return null;
        }

        return entry.value;
    }

    private write<TValue>(store: Map<string, CacheEntry<TValue>>, key: string, value: TValue): void {
        store.set(key, {
            value,
            expiresAt: this.clock.now() + this.ttlMs,
        });
    }
}