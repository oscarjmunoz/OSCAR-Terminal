import { ExplainableDecisionOutput } from "../core/types";

type Props = {
  data: ExplainableDecisionOutput;
};

function getDecisionTone(decision: ExplainableDecisionOutput["decision"]): string {
  if (decision === "BUY") return "text-emerald-300";
  if (decision === "SELL") return "text-rose-300";
  return "text-amber-300";
}

function getRiskTone(risk: ExplainableDecisionOutput["risk"]): string {
  if (risk === "Low") return "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
  if (risk === "Medium") return "border-amber-500/40 bg-amber-500/10 text-amber-300";
  return "border-rose-500/40 bg-rose-500/10 text-rose-300";
}

function getScoreWidthClass(score: number): string {
  if (score >= 95) return "w-full";
  if (score >= 90) return "w-11/12";
  if (score >= 80) return "w-10/12";
  if (score >= 70) return "w-9/12";
  if (score >= 60) return "w-8/12";
  if (score >= 50) return "w-7/12";
  if (score >= 40) return "w-6/12";
  if (score >= 30) return "w-5/12";
  if (score >= 20) return "w-4/12";
  if (score >= 10) return "w-3/12";
  return "w-2/12";
}

export default function DecisionExplanationCard({ data }: Props) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
      <div className="mb-6 flex items-center justify-between">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Decision Center</p>
        <span className="rounded-full border border-slate-700 bg-slate-950/70 px-3 py-1 text-xs font-semibold text-slate-300">
          {data.strategy}
        </span>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Decision</p>
        <p className={`mt-3 text-6xl font-black tracking-tight sm:text-7xl ${getDecisionTone(data.decision)}`}>{data.decision}</p>

        <div className="mt-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Confidence</p>
          <p className="mt-2 text-3xl font-bold text-white">{data.confidence}%</p>
        </div>

        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Oscar Score</p>
            <p className="text-sm font-semibold text-slate-200">{data.score}/100</p>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800">
            <div className={`h-3 rounded-full bg-gradient-to-r from-sky-500 via-emerald-400 to-emerald-300 ${getScoreWidthClass(data.score)}`} />
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-400">Risk</p>
            <span className={`mt-2 inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${getRiskTone(data.risk)}`}>
              {data.risk}
            </span>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 sm:col-span-2">
            <p className="text-xs uppercase tracking-wide text-slate-400">Expected RR</p>
            <p className="mt-2 text-sm font-semibold text-slate-200">{data.expectedRR}</p>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900/80 p-3">
          <p className="text-xs uppercase tracking-wide text-slate-400">Invalidation</p>
          <p className="mt-2 text-sm text-slate-200">{data.invalidation}</p>
        </div>

        <div className="mt-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Reasons</p>
          <ol className="space-y-2">
            {data.reasons.map((item, index) => (
              <li key={`${item}-${index}`} className="rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2 text-sm text-slate-200">
                <span className="mr-2 text-emerald-300">✓</span>
                {item}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
