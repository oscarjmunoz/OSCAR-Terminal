import { DecisionContext } from "../../contracts/DecisionContext";
import MetricRing from "./MetricRing";
import TerminalCard from "./TerminalCard";

type Props = {
    value: DecisionContext["score"]["institutionalScore"];
};

function tone(value: number): "emerald" | "sky" | "amber" | "rose" {
    if (value >= 80) return "emerald";
    if (value >= 60) return "sky";
    if (value >= 40) return "amber";
    return "rose";
}

export default function ScoreCard({ value }: Props) {
    return (
        <TerminalCard title="Institutional Score" eyebrow="Panel 1">
            <MetricRing value={value} label="Oscar Score" tone={tone(value)} suffix="/100" />
        </TerminalCard>
    );
}