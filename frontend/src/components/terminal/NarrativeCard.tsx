import TerminalCard from "./TerminalCard";

type Props = {
    narrative: string;
};

export default function NarrativeCard({ narrative }: Props) {
    return (
        <TerminalCard title="Narrative" eyebrow="Panel 9" className="h-full">
            <div className="min-h-[220px] rounded-xl border border-slate-800 bg-slate-900/70 p-4">
                <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Institutional report</p>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-200">{narrative}</p>
            </div>
        </TerminalCard>
    );
}