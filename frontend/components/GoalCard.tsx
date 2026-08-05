export type Goal = {
  id: number;
  user_id: number;
  name: string;
  category: string;
  target_amount: number;
  current_amount: number;
  monthly_contribution: number;
  target_date: string;
  priority: string;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  remaining_amount: number;
  progress_percent: number;
  months_remaining: number;
  projected_completion_date?: string | null;
  required_monthly_contribution: number;
  contribution_gap: number;
  health_score: number;
  status:
    | "completed"
    | "on_track"
    | "slightly_behind"
    | "off_track";
  coach_message: string;
};

const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
const label = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

function statusClass(status: Goal["status"]) {
  if (status === "completed" || status === "on_track") return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  if (status === "slightly_behind") return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  return "border-red-500/30 bg-red-500/10 text-red-300";
}

export default function GoalCard({ goal, onEdit, onDelete }: { goal: Goal; onEdit: (goal: Goal) => void; onDelete: (goal: Goal) => void }) {
  const progress = Math.min(Math.max(goal.progress_percent, 0), 100);

  return (
    <article className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-blue-400">{label(goal.category)}</p>
          <h2 className="mt-2 text-2xl font-bold text-white">{goal.name}</h2>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(goal.status)}`}>{label(goal.status)}</span>
      </div>

      <div className="mt-6">
        <div className="flex items-end justify-between">
          <div><p className="text-sm text-slate-400">Progress</p><p className="mt-1 text-3xl font-black text-white">{progress.toFixed(1)}%</p></div>
          <div className="text-right"><p className="text-sm text-slate-500">{money(goal.current_amount)}</p><p className="mt-1 text-xs text-slate-500">of {money(goal.target_amount)}</p></div>
        </div>
        <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-blue-500" style={{ width: `${progress}%` }} /></div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <Metric label="Remaining" value={money(goal.remaining_amount)} />
        <Metric label="Monthly contribution" value={money(goal.monthly_contribution)} />
        <Metric label="Required monthly" value={money(goal.required_monthly_contribution)} />
        <Metric label="Health score" value={`${goal.health_score.toFixed(0)}/100`} />
      </div>

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
        <p className="text-sm font-semibold text-white">AI Goal Coach</p>
        <p className="mt-2 text-sm leading-6 text-slate-400">{goal.coach_message}</p>
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 pt-5">
        <p className="text-xs text-slate-500">Target: {goal.target_date}</p>
        <div className="flex gap-2">
          <button type="button" onClick={() => onEdit(goal)} className="rounded-xl border border-blue-500/30 px-4 py-2 text-sm text-blue-300 hover:bg-blue-500/10">Edit</button>
          <button type="button" onClick={() => onDelete(goal)} className="rounded-xl border border-red-500/30 px-4 py-2 text-sm text-red-300 hover:bg-red-500/10">Delete</button>
        </div>
      </div>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><p className="text-xs uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 font-semibold text-white">{value}</p></div>;
}
