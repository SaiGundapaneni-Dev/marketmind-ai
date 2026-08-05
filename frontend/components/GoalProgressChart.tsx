type Goal = { id: number; name: string; progress_percent: number };

export default function GoalProgressChart({ goals }: { goals: Goal[] }) {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">Goal Progress</p>
      <h2 className="mt-2 text-xl font-bold text-white">Progress by goal</h2>
      <div className="mt-6 space-y-5">
        {goals.length ? goals.map((goal) => {
          const progress = Math.min(Math.max(goal.progress_percent, 0), 100);
          return <div key={goal.id}><div className="flex items-center justify-between gap-4"><p className="truncate text-sm font-medium text-slate-200">{goal.name}</p><p className="text-sm font-semibold text-white">{progress.toFixed(1)}%</p></div><div className="mt-2 h-2.5 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-blue-500" style={{ width: `${progress}%` }} /></div></div>;
        }) : <p className="text-sm text-slate-500">Goal progress will appear after you create a goal.</p>}
      </div>
    </section>
  );
}
