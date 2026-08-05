type StatusTone = "positive" | "warning" | "danger" | "neutral";

type Props = {
    label: string;
    value: string;
    tone?: StatusTone;
};

export default function StatusPill({
    label,
    value,
    tone = "neutral",
}: Props) {

    return (
        <div className={`status-pill status-pill--${tone}`}>
            <span className="status-pill__label">{label}</span>
            <strong className="status-pill__value">{value}</strong>
        </div>
    );
}