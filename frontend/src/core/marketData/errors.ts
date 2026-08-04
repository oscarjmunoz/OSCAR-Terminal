type ErrorOptions = {
    code?: string;
    cause?: unknown;
};

export class MT5ConnectorError extends Error {
    readonly code: string;
    override readonly cause: unknown;

    constructor(message: string, options: ErrorOptions = {}) {
        super(message);
        this.name = this.constructor.name;
        this.code = options.code ?? "MT5_CONNECTOR_ERROR";
        this.cause = options.cause;
    }
}

export class MT5InitializeError extends MT5ConnectorError {
    constructor(message = "Failed to initialize MetaTrader 5 connector", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "INITIALIZE_FAILED", cause: options.cause });
    }
}

export class MT5LoginError extends MT5ConnectorError {
    constructor(message = "Invalid MetaTrader 5 login", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "INVALID_LOGIN", cause: options.cause });
    }
}

export class MT5ShutdownError extends MT5ConnectorError {
    constructor(message = "Failed to shutdown MetaTrader 5 connector", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "SHUTDOWN_FAILED", cause: options.cause });
    }
}

export class MT5ReconnectError extends MT5ConnectorError {
    constructor(message = "Failed to reconnect MetaTrader 5 connector", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "RECONNECT_FAILED", cause: options.cause });
    }
}

export class MT5HealthCheckError extends MT5ConnectorError {
    constructor(message = "MetaTrader 5 health check failed", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "HEALTH_CHECK_FAILED", cause: options.cause });
    }
}

export class MT5TimeoutError extends MT5ConnectorError {
    constructor(message = "MetaTrader 5 request timed out", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "TIMEOUT", cause: options.cause });
    }
}

export class MT5DisconnectedError extends MT5ConnectorError {
    constructor(message = "MetaTrader 5 is disconnected", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "DISCONNECTED", cause: options.cause });
    }
}

export class MT5TerminalClosedError extends MT5ConnectorError {
    constructor(message = "MetaTrader 5 terminal is closed", options: ErrorOptions = {}) {
        super(message, { code: options.code ?? "TERMINAL_CLOSED", cause: options.cause });
    }
}

function hasCode(error: unknown, code: string): boolean {
    return typeof error === "object" && error !== null && "code" in error && (error as { code?: string }).code === code;
}

export function mapToTypedConnectorError(operation: string, error: unknown): MT5ConnectorError {
    const message = error instanceof Error ? error.message : `MetaTrader 5 ${operation} failed`;

    if (hasCode(error, "INVALID_LOGIN")) {
        return new MT5LoginError(message, { cause: error });
    }

    if (hasCode(error, "TIMEOUT")) {
        return new MT5TimeoutError(message, { cause: error });
    }

    if (hasCode(error, "DISCONNECTED")) {
        return new MT5DisconnectedError(message, { cause: error });
    }

    if (hasCode(error, "TERMINAL_CLOSED")) {
        return new MT5TerminalClosedError(message, { cause: error });
    }

    if (operation === "initialize") {
        return new MT5InitializeError(message, { cause: error });
    }

    if (operation === "login") {
        return new MT5LoginError(message, { cause: error });
    }

    if (operation === "shutdown") {
        return new MT5ShutdownError(message, { cause: error });
    }

    if (operation === "health_check") {
        return new MT5HealthCheckError(message, { cause: error });
    }

    return new MT5ConnectorError(message, { code: "REQUEST_FAILED", cause: error });
}