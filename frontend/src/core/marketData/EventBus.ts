import { createMarketDataEvent, MarketDataEvent, MarketDataEventMap, MarketDataEventType } from "./events";

type EventHandler<TType extends MarketDataEventType> = (event: MarketDataEvent<TType>) => void;

export class MarketDataEventBus {
    private readonly listeners = new Map<MarketDataEventType, Set<EventHandler<MarketDataEventType>>>();

    subscribe<TType extends MarketDataEventType>(type: TType, handler: EventHandler<TType>): () => void {
        const handlers = this.listeners.get(type) ?? new Set<EventHandler<MarketDataEventType>>();
        handlers.add(handler as EventHandler<MarketDataEventType>);
        this.listeners.set(type, handlers);

        return () => {
            handlers.delete(handler as EventHandler<MarketDataEventType>);
            if (handlers.size === 0) {
                this.listeners.delete(type);
            }
        };
    }

    publish<TType extends MarketDataEventType>(type: TType, payload: MarketDataEventMap[TType], occurredAt = Date.now()): MarketDataEvent<TType> {
        const event = createMarketDataEvent(type, payload, occurredAt);
        const handlers = this.listeners.get(type);

        handlers?.forEach((handler) => {
            handler(event as MarketDataEvent<MarketDataEventType>);
        });

        return event;
    }

    clear(): void {
        this.listeners.clear();
    }
}