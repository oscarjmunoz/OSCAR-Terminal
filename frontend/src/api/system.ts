import { api } from "./client";

export interface SystemResponse {
    database: string;
    database_url: string;
    engine_url: string;
    database_file: string;
    exception?: string;
}

export interface OperationalSettings {
    defaultSymbol: string;
    defaultTimeframe: string;
    availableSymbols: string[];
    availableTimeframes: string[];
}

export async function getSystem(): Promise<SystemResponse> {

    const response = await api.get<SystemResponse>(
        "/system"
    );

    return response.data;

}

export async function getOperationalSettings(): Promise<OperationalSettings> {

    const response = await api.get<OperationalSettings>(
        "/system/settings"
    );

    return response.data;

}