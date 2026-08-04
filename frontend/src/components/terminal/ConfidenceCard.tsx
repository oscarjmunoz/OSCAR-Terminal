import MetricRing from "./MetricRing";
import TerminalCard from "./TerminalCard";

type Props = {
    value: number;
};

function tone(value: number): "emerald" | "sky" | "amber" | "rose" {
    if (value >= 80) return "emerald";
    if (value >= 65) return "sky";
    if (value >= 50) return "amber";
    return "rose";
}

export default function ConfidenceCard({ value }: Props) {
    return (
        <TerminalCard title="Confidence" eyebrow="Panel 2">
            <MetricRing value={value} label="Decision Confidence" tone={tone(value)} suffix="%" />
        </TerminalCard>
    );
}