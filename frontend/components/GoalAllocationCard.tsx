type Goal = { id: number; name: string; current_amount: number };
const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);

export default function GoalAllocationCard({ goals }: { goals: Goal[] }) {
  const total = goals.reduce((sum, goal) => sum + goal.current_amount, 0);
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">Goal Allocation</p>
      <h2 className="mt-2 text-xl font-bold text-white">Funding distribution</h2>
      <div className="mt-6 space-y-4">
        {goals.length ? goals.map((goal) => {
          const allocation = total > 0 ? goal.current_amount / total * 100 : 0;
          return <div key={goal.id} className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="flex items-center justify-between gap-4"><div><p className="font-medium text-white">{goal.name}</p><p className="mt-1 text-xs text-slate-500">{money(goal.current_amount)}</p></div><p className="text-sm font-semibold text-blue-300">{allocation.toFixed(1)}%</p></div></div>;
        }) : <p className="text-sm text-slate-500">Funding distribution will appear after you create a goal.</p>}
      </div>
    </section>
  );
}
