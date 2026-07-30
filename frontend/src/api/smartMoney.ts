// frontend/src/api/smartMoney.ts

import { api } from "./client";

export interface Swing {

    index: number;

    time: string;

    price: number;

    kind: "HIGH" | "LOW";

    structure: "HH" | "HL" | "LH" | "LL";

}

export interface MarketStructure {

    trend: "BULLISH" | "BEARISH" | "RANGE" | "UNKNOWN";

    last_high: number | null;

    last_low: number | null;

    bos: boolean;

    choch: boolean;

    mss: boolean;

}

export async function getSwings(

    symbol: string = "USDCHF.pro",

    timeframe: string = "M5",

    candles: number = 300,

    left: number = 3,

    right: number = 3,

): Promise<Swing[]> {

    const response = await api.get<Swing[]>(

        `/smart-money/swings/${symbol}`,

        {

            params: {

                timeframe,

                candles,

                left,

                right,

            },

        }

    );

    return response.data;

}

export async function getStructure(

    symbol: string = "USDCHF.pro",

    timeframe: string = "M5",

    candles: number = 300,

    left: number = 3,

    right: number = 3,

): Promise<MarketStructure> {

    const response = await api.get<MarketStructure>(

        `/smart-money/structure/${symbol}`,

        {

            params: {

                timeframe,

                candles,

                left,

                right,

            },

        }

    );

    return response.data;

}
