// frontend/src/components/StatusCard.tsx

type StatusCardProps = {
    connected: boolean;
    account?: number;
    company?: string;
    server?: string;
};

export default function StatusCard({
    connected,
    account,
    company,
    server,
}: StatusCardProps) {

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
    };

    return (

        <div style={containerStyle}>

            <h2
                style={{
                    marginTop: 0,
                    marginBottom: 20,
                }}
            >
                MetaTrader 5
            </h2>

            <div style={rowStyle}>
                <span style={labelStyle}>Status</span>

                <span style={valueStyle}>
                    {connected
                        ? "🟢 Connected"
                        : "🔴 Offline"}
                </span>
            </div>

            <div style={rowStyle}>
                <span style={labelStyle}>Account</span>

                <span style={valueStyle}>
                    {account ?? "-"}
                </span>
            </div>

            <div style={rowStyle}>
                <span style={labelStyle}>Broker</span>

                <span style={valueStyle}>
                    {company ?? "-"}
                </span>
            </div>

            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    paddingTop: 8,
                }}
            >
                <span style={labelStyle}>Server</span>

                <span style={valueStyle}>
                    {server ?? "-"}
                </span>
            </div>

        </div>

    );

}