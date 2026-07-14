"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Snapshot = {
  id: number;
  total_cost: number;
  total_value: number;
  total_profit: number;
  total_return_percent: number;
  health_score: number;
  holdings_count: number;
  created_at: string;
};

type Performance = {
  current_value: number;
  previous_value?: number | null;
  change: number;
  change_percent: number;
  highest_value: number;
  lowest_value: number;
  best_day_change: number;
  worst_day_change: number;
  snapshot_count: number;
};

type Contributor = {
  symbol: string;
  name: string;
  profit: number;
  profit_percent: number;
  contribution_percent: number;
};

type Contributors = {
  top_contributors: Contributor[];
  bottom_contributors: Contributor[];
};

type Changes = {
  has_previous_snapshot: boolean;
  value_change: number;
  value_change_percent: number;
  profit_change: number;
  return_change: number;
  health_score_change: number;
  holdings_count_change: number;
  summary: string[];
};

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatDate(value: string) {
  const date = new Date(value);

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(date);
}

export default function PortfolioTimeline() {
  const [history, setHistory] = useState<Snapshot[]>([]);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [contributors, setContributors] = useState<Contributors | null>(null);
  const [changes, setChanges] = useState<Changes | null>(null);
  const [loading, setLoading] = useState(true);
  const [snapshotting, setSnapshotting] = useState(false);
  const [message, setMessage] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  async function loadTimeline() {
    const [historyResponse, performanceResponse, contributorsResponse, changesResponse] =
      await Promise.all([
        fetch(`${apiBaseUrl}/portfolio/history`, { cache: "no-store" }),
        fetch(`${apiBaseUrl}/portfolio/performance`, { cache: "no-store" }),
        fetch(`${apiBaseUrl}/portfolio/contributors`, { cache: "no-store" }),
        fetch(`${apiBaseUrl}/portfolio/changes`, { cache: "no-store" }),
      ]);

    if (
      !historyResponse.ok ||
      !performanceResponse.ok ||
      !contributorsResponse.ok ||
      !changesResponse.ok
    ) {
      throw new Error("Unable to load portfolio timeline.");
    }

    const [historyData, performanceData, contributorsData, changesData] =
      await Promise.all([
        historyResponse.json(),
        performanceResponse.json(),
        contributorsResponse.json(),
        changesResponse.json(),
      ]);

    setHistory(historyData);
    setPerformance(performanceData);
    setContributors(contributorsData);
    setChanges(changesData);
  }

  useEffect(() => {
    async function load() {
      try {
        await loadTimeline();
      } catch (error) {
        console.error(error);
        setMessage("Portfolio timeline is unavailable.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [apiBaseUrl]);

  async function createSnapshot() {
    setSnapshotting(true);
    setMessage("");

    try {
      const response = await fetch(`${apiBaseUrl}/portfolio/snapshot`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Unable to create portfolio snapshot.");
      }

      setMessage("Portfolio snapshot saved.");
      await loadTimeline();
    } catch (error) {
      console.error(error);
      setMessage("Unable to create portfolio snapshot.");
    } finally {
      setSnapshotting(false);
    }
  }

  const chartData = history.map((item) => ({
    date: formatDate(item.created_at),
    value: item.total_value,
    profit: item.total_profit,
    health: item.health_score,
  }));

  return (
    <section className="mt-8 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-400">
            Portfolio Timeline
          </p>
          <h2 className="mt-1 text-2xl font-semibold">
            Performance Intelligence
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Track portfolio value, contributions, and material changes over time.
          </p>
        </div>

        <button
          type="button"
          onClick={createSnapshot}
          disabled={snapshotting}
          className="rounded-xl bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {snapshotting ? "Saving..." : "Save Today’s Snapshot"}
        </button>
      </div>

      {message && (
        <p className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          {message}
        </p>
      )}

      {loading ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-slate-400">
          Loading timeline intelligence...
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              title="Latest Change"
              value={formatMoney(performance?.change ?? 0)}
              subtitle={`${(performance?.change_percent ?? 0).toFixed(2)}%`}
            />
            <MetricCard
              title="Highest Value"
              value={formatMoney(performance?.highest_value ?? 0)}
              subtitle={`${performance?.snapshot_count ?? 0} snapshots`}
            />
            <MetricCard
              title="Best Snapshot Move"
              value={formatMoney(performance?.best_day_change ?? 0)}
              subtitle="Compared with prior snapshot"
            />
            <MetricCard
              title="Worst Snapshot Move"
              value={formatMoney(performance?.worst_day_change ?? 0)}
              subtitle="Compared with prior snapshot"
            />
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-semibold">Portfolio Value History</h3>
                <p className="mt-1 text-sm text-slate-400">
                  Daily portfolio value snapshots.
                </p>
              </div>
            </div>

            {chartData.length === 0 ? (
              <div className="mt-6 rounded-xl border border-dashed border-slate-700 p-8 text-center text-slate-400">
                Save the first snapshot to begin the timeline.
              </div>
            ) : (
              <div className="mt-6 h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip
                      formatter={(value) => formatMoney(Number(value))}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      strokeWidth={3}
                      dot
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ContributorPanel
              title="Top Contributors"
              items={contributors?.top_contributors ?? []}
            />
            <ContributorPanel
              title="Largest Drags"
              items={contributors?.bottom_contributors ?? []}
            />
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm font-medium text-blue-400">What Changed?</p>
            <h3 className="mt-1 text-xl font-semibold">
              Snapshot Comparison
            </h3>

            <div className="mt-5 space-y-3">
              {(changes?.summary ?? []).map((item, index) => (
                <p
                  key={`${item}-${index}`}
                  className="rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-300"
                >
                  • {item}
                </p>
              ))}
            </div>
          </div>
        </>
      )}
    </section>
  );
}

function MetricCard({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
    </div>
  );
}

function ContributorPanel({
  title,
  items,
}: {
  title: string;
  items: Contributor[];
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h3 className="text-xl font-semibold">{title}</h3>

      <div className="mt-5 space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-slate-500">No contributor data available.</p>
        ) : (
          items.map((item) => (
            <div
              key={item.symbol}
              className="flex items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-950 p-4"
            >
              <div>
                <p className="font-semibold">{item.symbol}</p>
                <p className="text-xs text-slate-500">{item.name}</p>
              </div>

              <div className="text-right">
                <p
                  className={
                    item.profit >= 0 ? "text-emerald-300" : "text-red-300"
                  }
                >
                  {formatMoney(item.profit)}
                </p>
                <p className="text-xs text-slate-500">
                  {item.contribution_percent.toFixed(2)}% contribution
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
