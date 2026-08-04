import { ReactNode } from "react";

type Props = {
    title: string;
    eyebrow?: string;
    className?: string;
    children: ReactNode;
};

export default function TerminalCard({ title, eyebrow, className = "", children }: Props) {
    return (
        <section className={`rounded-2xl border border-slate-800/80 bg-slate-950/70 p-4 shadow-[0_0_0_1px_rgba(15,23,42,0.24)] backdrop-blur ${className}`}>
            <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                    {eyebrow ? <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">{eyebrow}</p> : null}
                    <h2 className="text-sm font-semibold text-slate-100 sm:text-base">{title}</h2>
                </div>
            </div>
            {children}
        </section>
    );
}