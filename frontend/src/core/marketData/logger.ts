import { Logger } from "./types";

function write(method: "info" | "warn" | "error" | "debug", message: string, meta?: Record<string, unknown>): void {
    const payload = meta ? { message, ...meta } : message;
    console[method](payload);
}

export class ConsoleLogger implements Logger {
    info(message: string, meta?: Record<string, unknown>): void {
        write("info", message, meta);
    }

    warn(message: string, meta?: Record<string, unknown>): void {
        write("warn", message, meta);
    }

    error(message: string, meta?: Record<string, unknown>): void {
        write("error", message, meta);
    }

    debug(message: string, meta?: Record<string, unknown>): void {
        write("debug", message, meta);
    }
}