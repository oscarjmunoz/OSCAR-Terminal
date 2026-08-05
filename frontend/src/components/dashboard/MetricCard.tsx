type Tone = "neutral" | "positive" | "warning" | "danger";

type Props = {
    label: string;
    value: string;
    detail?: string;
    tone?: Tone;
    testId?: string;
};

export default function MetricCard({
    label,
    value,
    detail,
    tone = "neutral",
    testId,
}: Props) {

    return (
        <div className={`metric-card metric-card--${tone}`} data-testid={testId}>
            <span className="metric-card__label">{label}</span>
            <strong className="metric-card__value">{value}</strong>
            {detail ? <span className="metric-card__detail">{detail}</span> : null}
        </div>
    );
}