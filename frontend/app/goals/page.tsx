"use client";

import { FormEvent, useEffect, useState } from "react";

import GoalAllocationCard from "@/components/GoalAllocationCard";
import GoalCard, {
  type Goal,
} from "@/components/GoalCard";
import GoalProgressChart from "@/components/GoalProgressChart";
import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";

type GoalSummary = {
  total_goals: number; completed_goals: number; on_track_goals: number; behind_goals: number;
  total_target_amount: number; total_current_amount: number; overall_progress_percent: number; goals: Goal[];
};
type GoalForm = {
  name: string; category: string; target_amount: string; current_amount: string;
  monthly_contribution: string; target_date: string; priority: string; notes: string;
};

const emptyForm: GoalForm = { name: "", category: "custom", target_amount: "", current_amount: "0", monthly_contribution: "0", target_date: "", priority: "medium", notes: "" };
const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);

export default function GoalsPage() {
  const [summary, setSummary] = useState<GoalSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<GoalForm>(emptyForm);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  async function loadGoals() {
    setLoading(true); setError("");
    try {
      const response = await apiFetch("/goals", { cache: "no-store" });
      if (!response.ok) throw new Error("Unable to load investment goals.");
      setSummary(await response.json());
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to load investment goals.");
    } finally { setLoading(false); }
  }

  useEffect(() => { loadGoals(); }, []);

  function openCreate() { setEditingGoal(null); setForm(emptyForm); setModalOpen(true); }
  function openEdit(goal: Goal) {
    setEditingGoal(goal);
    setForm({
      name: goal.name, category: goal.category, target_amount: String(goal.target_amount),
      current_amount: String(goal.current_amount), monthly_contribution: String(goal.monthly_contribution),
      target_date: goal.target_date, priority: goal.priority, notes: goal.notes || "",
    });
    setModalOpen(true);
  }

  async function saveGoal(event: FormEvent) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      const response = await apiFetch(editingGoal ? `/goals/${editingGoal.id}` : "/goals", {
        method: editingGoal ? "PUT" : "POST",
        body: JSON.stringify({
          name: form.name.trim(), category: form.category,
          target_amount: Number(form.target_amount), current_amount: Number(form.current_amount),
          monthly_contribution: Number(form.monthly_contribution), target_date: form.target_date,
          priority: form.priority, notes: form.notes.trim() || null,
        }),
      });
      if (!response.ok) {
        let message = "Unable to save goal.";
        try { const data = await response.json(); if (typeof data?.detail === "string") message = data.detail; } catch {}
        throw new Error(message);
      }
      setModalOpen(false); setEditingGoal(null); setForm(emptyForm); await loadGoals();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save goal.");
    } finally { setSaving(false); }
  }

  async function deleteGoal(goal: Goal) {
    if (!window.confirm(`Delete "${goal.name}"?`)) return;
    try {
      const response = await apiFetch(`/goals/${goal.id}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Unable to delete goal.");
      await loadGoals();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to delete goal.");
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />
      <section className="min-w-0 flex-1 px-5 py-7 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <header className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">Life-Context Investing</p>
              <h1 className="mt-2 text-3xl font-bold sm:text-4xl">Investment Goals</h1>
              <p className="mt-3 max-w-3xl text-slate-400">Connect investing progress to the outcomes that matter in real life.</p>
            </div>
            <button type="button" onClick={openCreate} className="rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500">Create goal</button>
          </header>

          {error && <p className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">{error}</p>}

          {loading ? <div className="flex min-h-[55vh] items-center justify-center"><p className="text-slate-400">Loading your goals...</p></div> : summary ? <>
            <section className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <SummaryCard label="Total funded" value={money(summary.total_current_amount)} />
              <SummaryCard label="Total target" value={money(summary.total_target_amount)} />
              <SummaryCard label="Overall progress" value={`${summary.overall_progress_percent.toFixed(1)}%`} />
              <SummaryCard label="Needs attention" value={String(summary.behind_goals)} />
            </section>
            <section className="mt-7 grid gap-6 xl:grid-cols-2">
              <GoalProgressChart goals={summary.goals} />
              <GoalAllocationCard goals={summary.goals} />
            </section>
            <section className="mt-7 grid gap-6 xl:grid-cols-2">
              {summary.goals.length ? summary.goals.map((goal) => <GoalCard key={goal.id} goal={goal} onEdit={openEdit} onDelete={deleteGoal} />) : <div className="xl:col-span-2 rounded-3xl border border-dashed border-slate-700 bg-slate-900/50 p-12 text-center"><h2 className="text-xl font-bold">No goals yet</h2><p className="mt-2 text-sm text-slate-500">Create your first goal to start tracking progress and monthly funding needs.</p></div>}
            </section>
          </> : null}
        </div>
      </section>

      {modalOpen && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 py-8 backdrop-blur-sm">
        <form onSubmit={saveGoal} className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl border border-slate-700 bg-slate-900 p-6">
          <div className="flex items-start justify-between gap-4"><div><p className="text-sm text-blue-400">{editingGoal ? "Edit Goal" : "New Goal"}</p><h2 className="mt-1 text-2xl font-bold">{editingGoal ? editingGoal.name : "Create investment goal"}</h2></div><button type="button" onClick={() => setModalOpen(false)} className="rounded-xl border border-slate-700 px-3 py-2 text-sm text-slate-300">Close</button></div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <Field label="Goal name" value={form.name} onChange={(value) => setForm({ ...form, name: value })} required />
            <SelectField label="Category" value={form.category} onChange={(value) => setForm({ ...form, category: value })} options={["retirement","emergency_fund","house","education","travel","car","financial_independence","custom"]} />
            <Field label="Target amount" value={form.target_amount} onChange={(value) => setForm({ ...form, target_amount: value })} type="number" required />
            <Field label="Current amount" value={form.current_amount} onChange={(value) => setForm({ ...form, current_amount: value })} type="number" />
            <Field label="Monthly contribution" value={form.monthly_contribution} onChange={(value) => setForm({ ...form, monthly_contribution: value })} type="number" />
            <Field label="Target date" value={form.target_date} onChange={(value) => setForm({ ...form, target_date: value })} type="date" required />
            <SelectField label="Priority" value={form.priority} onChange={(value) => setForm({ ...form, priority: value })} options={["high","medium","low"]} />
          </div>
          <label className="mt-4 block text-sm text-slate-300">Notes<textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} rows={4} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500" /></label>
          <button type="submit" disabled={saving} className="mt-6 w-full rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500 disabled:opacity-50">{saving ? "Saving..." : editingGoal ? "Update goal" : "Create goal"}</button>
        </form>
      </div>}
    </main>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) { return <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><p className="text-sm text-slate-400">{label}</p><p className="mt-2 text-2xl font-bold">{value}</p></div>; }
function Field({ label, value, onChange, type = "text", required = false }: { label: string; value: string; onChange: (value: string) => void; type?: string; required?: boolean }) { return <label className="text-sm text-slate-300">{label}<input type={type} value={value} required={required} min={type === "number" ? "0" : undefined} step={type === "number" ? "0.01" : undefined} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500" /></label>; }
function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[] }) { return <label className="text-sm text-slate-300">{label}<select value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500">{options.map((option) => <option key={option} value={option}>{option.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())}</option>)}</select></label>; }
