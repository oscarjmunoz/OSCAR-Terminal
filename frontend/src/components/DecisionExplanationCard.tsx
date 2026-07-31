import { ExplainableDecisionOutput } from "../core/types";

export type MockDecisionPlan = {
  qualityScore: number;
  entry: string;
  stopLoss: string;
  rr: string;
  tp1: string;
  runner: string;
  breakEven: string;
  partialExit: string;
  strategy: string;
};

type Props = {
  data: ExplainableDecisionOutput;
  plan: MockDecisionPlan;
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

export default function DecisionExplanationCard({ data, plan }: Props) {
  const planItems = [
    { label: "Quality Score", value: `${plan.qualityScore}` },
    { label: "Entry", value: plan.entry },
    { label: "Stop Loss", value: plan.stopLoss },
    { label: "RR", value: plan.rr },
    { label: "TP1", value: plan.tp1 },
    { label: "Runner", value: plan.runner },
    { label: "Break Even", value: plan.breakEven },
    { label: "Partial Exit", value: plan.partialExit },
    { label: "Strategy", value: plan.strategy },
  ];

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 sm:p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Decision Center</p>
        <span className="rounded-full border border-slate-700 bg-slate-950/70 px-3 py-1 text-xs font-semibold text-slate-300">
          {plan.strategy}
        </span>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 sm:p-5">
        <div className="grid gap-4 xl:grid-cols-12">
          <div className="xl:col-span-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Decision</p>
            <p className={`mt-2 text-4xl font-black tracking-tight sm:text-5xl ${getDecisionTone(data.decision)}`}>{data.decision}</p>

            <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
              <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-2.5">
                <p className="text-[11px] uppercase tracking-wide text-slate-400">Confidence</p>
                <p className="mt-1 text-base font-semibold text-white">{data.confidence}%</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-2.5">
                <p className="text-[11px] uppercase tracking-wide text-slate-400">Risk</p>
                <span className={`mt-1 inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold ${getRiskTone(data.risk)}`}>
                  {data.risk}
                </span>
              </div>
            </div>
          </div>

          <div className="xl:col-span-8">
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {planItems.map((item) => (
                <div key={item.label} className="rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2">
                  <p className="text-[11px] uppercase tracking-wide text-slate-400">{item.label}</p>
                  <p className="mt-1 text-sm font-semibold text-slate-100">{item.value}</p>
                </div>
              ))}
            </div>

            <div className="mt-3">
              <div className="mb-1.5 flex items-center justify-between">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Oscar Score</p>
                <p className="text-xs font-semibold text-slate-200">{data.score}/100</p>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div className={`h-2.5 rounded-full bg-gradient-to-r from-sky-500 via-emerald-400 to-emerald-300 ${getScoreWidthClass(data.score)}`} />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-3 rounded-xl border border-slate-800 bg-slate-900/80 p-2.5">
          <p className="text-[11px] uppercase tracking-wide text-slate-400">Invalidation</p>
          <p className="mt-1 text-xs text-slate-200">{data.invalidation}</p>
        </div>

        <div className="mt-3">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">Reasons</p>
          <ol className="grid gap-2 sm:grid-cols-2">
            {data.reasons.map((item, index) => (
              <li key={`${item}-${index}`} className="rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2 text-xs text-slate-200">
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
