import {
    MT5ConnectorError,
    MT5DisconnectedError,
    MT5HealthCheckError,
    MT5LoginError,
    MT5TerminalClosedError,
    MT5TimeoutError,
} from "./errors";
import { MarketDataEventBus } from "./EventBus";
import { ConsoleLogger } from "./logger";
import { MT5Connector } from "./MT5Connector";
import { ConnectionState, Logger, MarketDataSettings, Scheduler } from "./types";

class DefaultScheduler implements Scheduler {
    sleep(milliseconds: number): Promise<void> {
        return new Promise((resolve) => {
            setTimeout(resolve, milliseconds);
        });
    }
}

export class ConnectionManager {
    private state: ConnectionState = "DISCONNECTED";
    private lastHealthCheckAt = 0;

    constructor(
        private readonly connector: MT5Connector,
        private readonly settings: MarketDataSettings,
        private readonly eventBus: MarketDataEventBus,
        private readonly logger: Logger = new ConsoleLogger(),
        private readonly scheduler: Scheduler = new DefaultScheduler(),
        private readonly now: () => number = Date.now
    ) { }

    getState(): ConnectionState {
        return this.state;
    }

    async connect(): Promise<void> {
        this.transitionTo("CONNECTING");

        try {
            await this.connector.initialize();
            await this.connector.login();
            const health = await this.connector.health_check();

            this.lastHealthCheckAt = this.now();
            this.transitionTo("CONNECTED");
            this.eventBus.publish("ConnectionEstablished", { state: this.state, latencyMs: health.latencyMs });
            this.logger.info("MT5 connection established", { latencyMs: health.latencyMs });
        } catch (error) {
            await this.failOrReconnect(error);
        }
    }

    async disconnect(): Promise<void> {
        await this.connector.shutdown();
        this.transitionTo("DISCONNECTED");
    }

    async ensureConnection(): Promise<void> {
        if (this.state === "DISCONNECTED" || this.state === "ERROR") {
            await this.connect();
            return;
        }

        if (this.state === "RECONNECTING") {
            return;
        }

        if (this.shouldRunHealthCheck()) {
            try {
                await this.connector.health_check();
                this.lastHealthCheckAt = this.now();
            } catch (error) {
                await this.failOrReconnect(error);
            }
        }
    }

    async handleConnectionError(error: unknown): Promise<void> {
        await this.failOrReconnect(error);
    }

    private shouldRunHealthCheck(): boolean {
        return this.state === "CONNECTED" && this.now() - this.lastHealthCheckAt >= this.settings.healthCheckIntervalMs;
    }

    private async failOrReconnect(error: unknown): Promise<void> {
        if (error instanceof MT5LoginError) {
            this.transitionTo("ERROR");
            this.eventBus.publish("ConnectionLost", { state: this.state, reason: error.message });
            this.logger.error("MT5 login failed", { code: error.code });
            throw error;
        }

        if (
            error instanceof MT5DisconnectedError ||
            error instanceof MT5TerminalClosedError ||
            error instanceof MT5TimeoutError ||
            error instanceof MT5HealthCheckError ||
            error instanceof MT5ConnectorError
        ) {
            await this.reconnectWithBackoff(error);
            return;
        }

        throw error;
    }

    private async reconnectWithBackoff(error: MT5ConnectorError): Promise<void> {
        this.transitionTo("RECONNECTING");

        for (let attempt = 1; attempt <= this.settings.reconnectMaxAttempts; attempt += 1) {
            const delay = Math.min(
                this.settings.reconnectIntervalMs * 2 ** (attempt - 1),
                this.settings.reconnectMaxIntervalMs
            );

            this.eventBus.publish("ConnectionLost", { state: this.state, reason: error.message, retryInMs: delay });
            this.logger.warn("MT5 connection lost", { attempt, retryInMs: delay, code: error.code });
            await this.scheduler.sleep(delay);

            try {
                await this.connector.reconnect();
                const health = await this.connector.health_check();
                this.lastHealthCheckAt = this.now();
                this.transitionTo("CONNECTED");
                this.eventBus.publish("ConnectionEstablished", { state: this.state, latencyMs: health.latencyMs });
                this.logger.info("MT5 reconnection established", { attempt, latencyMs: health.latencyMs });
                return;
            } catch (reconnectError) {
                if (reconnectError instanceof MT5LoginError) {
                    this.transitionTo("ERROR");
                    this.logger.error("MT5 reconnection aborted due to invalid login", { attempt });
                    throw reconnectError;
                }

                if (attempt === this.settings.reconnectMaxAttempts) {
                    this.transitionTo("ERROR");
                    const finalError = reconnectError instanceof MT5ConnectorError ? reconnectError : error;
                    this.logger.error("MT5 reconnection exhausted", { attempt, code: finalError.code });
                    throw finalError;
                }
            }
        }
    }

    private transitionTo(state: ConnectionState): void {
        this.state = state;
    }
}