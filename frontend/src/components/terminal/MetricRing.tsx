type Props = {
    value: number;
    label: string;
    tone: "emerald" | "sky" | "amber" | "rose";
    suffix?: string;
};

const RING_TONES = {
    emerald: { ring: "stroke-emerald-400", glow: "text-emerald-300" },
    sky: { ring: "stroke-sky-400", glow: "text-sky-300" },
    amber: { ring: "stroke-amber-400", glow: "text-amber-300" },
    rose: { ring: "stroke-rose-400", glow: "text-rose-300" },
} as const;

export default function MetricRing({ value, label, tone, suffix = "" }: Props) {
    const safeValue = Math.max(0, Math.min(100, value));
    const strokeDashoffset = 282.6 - (282.6 * safeValue) / 100;
    const toneClass = RING_TONES[tone];

    return (
        <div className="flex items-center gap-4">
            <div className="relative h-24 w-24 shrink-0 sm:h-28 sm:w-28">
                <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
                    <circle cx="60" cy="60" r="45" className="fill-none stroke-slate-800" strokeWidth="10" />
                    <circle
                        cx="60"
                        cy="60"
                        r="45"
                        className={`fill-none ${toneClass.ring}`}
                        strokeWidth="10"
                        strokeLinecap="round"
                        strokeDasharray="282.6"
                        strokeDashoffset={strokeDashoffset}
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <span className={`text-2xl font-black tracking-tight ${toneClass.glow}`}>{safeValue}</span>
                    {suffix ? <span className="text-[10px] uppercase tracking-[0.24em] text-slate-500">{suffix}</span> : null}
                </div>
            </div>
            <div>
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{label}</p>
                <p className="mt-1 text-sm text-slate-300">Institutional terminal metric</p>
            </div>
        </div>
    );
}