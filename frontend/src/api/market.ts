import { api } from "./client";

export async function getStatus() {

    const response = await api.get("/market/status");

    return response.data;

}

export async function getTick() {

    const response = await api.get("/market/tick/USDCHF");

    return response.data;

}