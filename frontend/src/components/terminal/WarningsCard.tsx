import TerminalCard from "./TerminalCard";

type Props = {
    warnings: string[];
};

export default function WarningsCard({ warnings }: Props) {
    return (
        <TerminalCard title="Warnings" eyebrow="Panel 10">
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
                {warnings.length ? (
                    <ul className="space-y-2 text-sm text-slate-200">
                        {warnings.map((warning) => (
                            <li key={warning} className="flex gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-rose-100">
                                <span className="mt-0.5 text-rose-300">!</span>
                                <span>{warning}</span>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-sm text-slate-400">No warnings.</p>
                )}
            </div>
        </TerminalCard>
    );
}