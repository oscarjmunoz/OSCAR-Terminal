import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    risk: DecisionContext["risk"];
};

function tone(grade: Props["risk"]["grade"]): string {
    if (grade === "LOW") return "text-emerald-300";
    if (grade === "MEDIUM") return "text-amber-300";
    return "text-rose-300";
}

export default function RiskCard({ risk }: Props) {
    const rows = [
        { label: "Risk Grade", value: risk.grade },
        { label: "RR", value: risk.rr },
        { label: "Capital Risk", value: risk.capitalRisk },
        { label: "Stop Distance", value: risk.stopDistance },
    ];

    return (
        <TerminalCard title="Risk" eyebrow="Panel 5">
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {rows.map((row) => (
                    <div key={row.label} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{row.label}</p>
                        <p className={`mt-2 text-sm font-semibold ${tone(risk.grade)}`}>{row.value}</p>
                    </div>
                ))}
            </div>
        </TerminalCard>
    );
}