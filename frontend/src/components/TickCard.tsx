// frontend/src/components/TickCard.tsx

type TickCardProps = {
    symbol?: string;
    bid?: number;
    ask?: number;
    spread?: number;
};

export default function TickCard({
    symbol,
    bid,
    ask,
    spread,
}: TickCardProps) {

    const containerStyle: React.CSSProperties = {
        background: "#1e293b",
        borderRadius: 12,
        padding: 20,
        boxShadow: "0 4px 12px rgba(0,0,0,.25)",
    };

    const rowStyle: React.CSSProperties = {
        display: "flex",
        justifyContent: "space-between",
        padding: "8px 0",
        borderBottom: "1px solid #334155",
    };

    const labelStyle: React.CSSProperties = {
        color: "#94a3b8",
        fontWeight: 600,
    };

    const valueStyle: React.CSSProperties = {
        color: "#ffffff",
        fontFamily: "Consolas, monospace",
    };

    return (

        <div style={containerStyle}>

            <h2
                style={{
                    marginTop: 0,
                    marginBottom: 20,
                }}
            >
                Live Market
            </h2>

            <div style={rowStyle}>
                <span style={labelStyle}>Symbol</span>

                <span style={valueStyle}>
                    {symbol ?? "-"}
                </span>
            </div>

            <div style={rowStyle}>
                <span style={labelStyle}>Bid</span>

                <span style={valueStyle}>
                    {bid?.toFixed(5) ?? "-"}
                </span>
            </div>

            <div style={rowStyle}>
                <span style={labelStyle}>Ask</span>

                <span style={valueStyle}>
                    {ask?.toFixed(5) ?? "-"}
                </span>
            </div>

            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    paddingTop: 8,
                }}
            >
                <span style={labelStyle}>Spread</span>

                <span
                    style={{
                        ...valueStyle,
                        color:
                            spread === undefined
                                ? "#ffffff"
                                : spread <= 2
                                    ? "#22c55e"
                                    : spread <= 3
                                        ? "#facc15"
                                        : "#ef4444",
                    }}
                >
                    {spread?.toFixed(1) ?? "-"} pips
                </span>
            </div>

        </div>

    );

}