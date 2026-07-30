// frontend/src/components/CandleTable.tsx

export type Candle = {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    tick_volume: number;
};

type CandleTableProps = {
    candles: Candle[];
};

export default function CandleTable({
    candles,
}: CandleTableProps) {

    const tableStyle: React.CSSProperties = {
        width: "100%",
        borderCollapse: "collapse",
    };

    const headerStyle: React.CSSProperties = {
        background: "#334155",
        color: "#ffffff",
        padding: "10px",
        fontWeight: 600,
        textAlign: "right",
    };

    const timeHeaderStyle: React.CSSProperties = {
        ...headerStyle,
        textAlign: "left",
    };

    const cellStyle: React.CSSProperties = {
        padding: "8px 10px",
        borderBottom: "1px solid #334155",
        textAlign: "right",
        fontFamily: "Consolas, monospace",
    };

    const timeCellStyle: React.CSSProperties = {
        ...cellStyle,
        textAlign: "left",
        fontFamily: "Segoe UI",
    };

    return (

        <div
            style={{
                background: "#1e293b",
                borderRadius: 12,
                padding: 20,
                boxShadow: "0 4px 12px rgba(0,0,0,.25)",
            }}
        >

            <h2
                style={{
                    marginTop: 0,
                    marginBottom: 20,
                }}
            >
                Latest Candles
            </h2>

            <table style={tableStyle}>

                <thead>

                    <tr>

                        <th style={timeHeaderStyle}>
                            Time
                        </th>

                        <th style={headerStyle}>
                            Open
                        </th>

                        <th style={headerStyle}>
                            High
                        </th>

                        <th style={headerStyle}>
                            Low
                        </th>

                        <th style={headerStyle}>
                            Close
                        </th>

                        <th style={headerStyle}>
                            Volume
                        </th>

                    </tr>

                </thead>

                <tbody>

                    {

                        candles
                            .slice(-10)
                            .reverse()
                            .map((candle) => {

                                const bullish =
                                    candle.close >= candle.open;

                                return (

                                    <tr key={candle.time}>

                                        <td style={timeCellStyle}>
                                            {candle.time}
                                        </td>

                                        <td style={cellStyle}>
                                            {candle.open.toFixed(5)}
                                        </td>

                                        <td style={cellStyle}>
                                            {candle.high.toFixed(5)}
                                        </td>

                                        <td style={cellStyle}>
                                            {candle.low.toFixed(5)}
                                        </td>

                                        <td
                                            style={{
                                                ...cellStyle,
                                                color: bullish
                                                    ? "#22c55e"
                                                    : "#ef4444",
                                                fontWeight: 700,
                                            }}
                                        >
                                            {candle.close.toFixed(5)}
                                        </td>

                                        <td style={cellStyle}>
                                            {candle.tick_volume}
                                        </td>

                                    </tr>

                                );

                            })

                    }

                </tbody>

            </table>

        </div>

    );

}