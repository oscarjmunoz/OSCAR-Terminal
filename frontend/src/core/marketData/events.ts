import { ConnectionState, MarketCandle, MarketStatus, MarketTick, MarketTimeframe } from "./types";
import { DecisionContext } from "../../contracts/DecisionContext";

export interface MarketDataEventMap {
    ConnectionEstablished: {
        state: ConnectionState;
        latencyMs: number | null;
    };
    ConnectionLost: {
        state: ConnectionState;
        reason: string;
        retryInMs?: number;
    };
    HistoryLoaded: {
        symbol: string;
        timeframe: MarketTimeframe;
        count: number;
        latencyMs: number;
    };
    MarketUpdated: {
        symbol: string;
        status: MarketStatus;
    };
    TickReceived: {
        symbol: string;
        tick: MarketTick;
    };
    TickBatchReceived: {
        symbol: string;
        ticks: MarketTick[];
    };
    CandleClosed: {
        symbol: string;
        timeframe: MarketTimeframe;
        candle: MarketCandle;
    };
    TimeframeUpdated: {
        symbol: string;
        timeframe: MarketTimeframe;
        candle: MarketCandle;
        synchronized: boolean;
        latestClosedAt: Readonly<Record<MarketTimeframe, string | null>>;
    };
    PipelineExecuted: {
        symbol: string;
        timeframe: string;
        latencyMs: number;
        droppedEvents: number;
        executedAt: number;
    };
    DecisionContextUpdated: {
        symbol: string;
        timeframe: string;
        context: DecisionContext;
        latencyMs: number;
        pipelineLatencyMs: number;
        updatedAt: number;
    };
}

export type MarketDataEventType = keyof MarketDataEventMap;

export type MarketDataEvent<TType extends MarketDataEventType = MarketDataEventType> = Readonly<{
    type: TType;
    payload: Readonly<MarketDataEventMap[TType]>;
    occurredAt: number;
}>;

function clonePayload<T>(payload: T): T {
    if (Array.isArray(payload)) {
        return payload.map((entry) => clonePayload(entry)) as T;
    }

    if (payload && typeof payload === "object") {
        const clonedEntries = Object.entries(payload as Record<string, unknown>).map(([key, value]) => [key, clonePayload(value)]);
        return Object.fromEntries(clonedEntries) as T;
    }

    return payload;
}

function deepFreeze<T>(value: T): T {
    if (value && typeof value === "object") {
        Object.values(value as Record<string, unknown>).forEach((nestedValue) => deepFreeze(nestedValue));
        Object.freeze(value);
    }

    return value;
}

export function createMarketDataEvent<TType extends MarketDataEventType>(
    type: TType,
    payload: MarketDataEventMap[TType],
    occurredAt = Date.now()
): MarketDataEvent<TType> {
    return deepFreeze({
        type,
        payload: clonePayload(payload),
        occurredAt,
    });
}