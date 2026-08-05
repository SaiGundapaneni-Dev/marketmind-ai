"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiFetch } from "@/lib/api";

type TimeRange = "1W" | "1M" | "3M" | "6M" | "1Y" | "ALL";

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

type ChartPoint = {
  date: string;
  fullDate: string;
  value: number;
  cost: number;
  profit: number;
  returnPercent: number;
  health: number;
  timestamp: number;
};

const RANGE_DAYS: Record<Exclude<TimeRange, "ALL">, number> = {
  "1W": 7,
  "1M": 30,
  "3M": 90,
  "6M": 180,
  "1Y": 365,
};

const ranges: TimeRange[] = [
  "1W",
  "1M",
  "3M",
  "6M",
  "1Y",
  "ALL",
];

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatCompactMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatDate(value: string) {
  const date = new Date(value);

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(date);
}

function formatFullDate(value: string) {
  const date = new Date(value);

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function getToneClass(value: number) {
  if (value > 0) {
    return "text-emerald-300";
  }

  if (value < 0) {
    return "text-red-300";
  }

  return "text-slate-300";
}

function buildSummary(
  points: ChartPoint[],
  contributors: Contributors | null
) {
  if (points.length === 0) {
    return "Save your first portfolio snapshot to begin visual performance tracking.";
  }

  if (points.length === 1) {
    return (
      "Your first portfolio snapshot is recorded. Save future snapshots to compare " +
      "value, invested cost, profit, and portfolio health over time."
    );
  }

  const first = points[0];
  const latest = points[points.length - 1];
  const change = latest.value - first.value;
  const changePercent =
    first.value > 0 ? (change / first.value) * 100 : 0;

  const top = contributors?.top_contributors?.[0];
  const drag = contributors?.bottom_contributors?.[0];

  const direction =
    change > 0
      ? `gained ${formatMoney(change)} (${changePercent.toFixed(2)}%)`
      : change < 0
        ? `declined ${formatMoney(Math.abs(change))} (${Math.abs(changePercent).toFixed(2)}%)`
        : "remained unchanged";

  const contributorText = top
    ? `${top.symbol} is currently the strongest profit contributor.`
    : "";

  const dragText =
    drag && drag.profit < 0
      ? `${drag.symbol} is the largest drag and deserves thesis review.`
      : "";

  return [
    `Across the selected period, your portfolio ${direction}.`,
    contributorText,
    dragText,
  ]
    .filter(Boolean)
    .join(" ");
}

function PortfolioTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{
    payload: ChartPoint;
  }>;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0].payload;

  return (
    <div className="min-w-56 rounded-xl border border-slate-700 bg-slate-950 p-4 shadow-2xl">
      <p className="text-sm font-semibold text-white">
        {point.fullDate}
      </p>

      <div className="mt-3 space-y-2 text-sm">
        <TooltipRow
          label="Portfolio value"
          value={formatMoney(point.value)}
        />

        <TooltipRow
          label="Invested cost"
          value={formatMoney(point.cost)}
        />

        <TooltipRow
          label="Profit"
          value={formatMoney(point.profit)}
          tone={getToneClass(point.profit)}
        />

        <TooltipRow
          label="Return"
          value={`${point.returnPercent.toFixed(2)}%`}
          tone={getToneClass(point.returnPercent)}
        />

        <TooltipRow
          label="Health"
          value={`${point.health.toFixed(0)}/100`}
        />
      </div>
    </div>
  );
}

export default function PortfolioTimeline() {
  const [history, setHistory] = useState<Snapshot[]>([]);
  const [performance, setPerformance] =
    useState<Performance | null>(null);
  const [contributors, setContributors] =
    useState<Contributors | null>(null);
  const [changes, setChanges] =
    useState<Changes | null>(null);
  const [range, setRange] = useState<TimeRange>("ALL");
  const [loading, setLoading] = useState(true);
  const [snapshotting, setSnapshotting] = useState(false);
  const [message, setMessage] = useState("");

  async function loadTimeline() {
    const [
      historyResponse,
      performanceResponse,
      contributorsResponse,
      changesResponse,
    ] = await Promise.all([
      apiFetch("/portfolio/history", {
        cache: "no-store",
      }),
      apiFetch("/portfolio/performance", {
        cache: "no-store",
      }),
      apiFetch("/portfolio/contributors", {
        cache: "no-store",
      }),
      apiFetch("/portfolio/changes", {
        cache: "no-store",
      }),
    ]);

    if (
      !historyResponse.ok ||
      !performanceResponse.ok ||
      !contributorsResponse.ok ||
      !changesResponse.ok
    ) {
      throw new Error("Unable to load portfolio timeline.");
    }

    const [
      historyData,
      performanceData,
      contributorsData,
      changesData,
    ] = await Promise.all([
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
        console.error("Portfolio timeline error:", error);
        setMessage("Portfolio timeline is unavailable.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  async function createSnapshot() {
    setSnapshotting(true);
    setMessage("");

    try {
      const response = await apiFetch("/portfolio/snapshot", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Unable to create portfolio snapshot.");
      }

      setMessage("Portfolio snapshot saved.");
      await loadTimeline();
    } catch (error) {
      console.error("Create snapshot error:", error);
      setMessage("Unable to create portfolio snapshot.");
    } finally {
      setSnapshotting(false);
    }
  }

  const allChartData = useMemo<ChartPoint[]>(
    () =>
      history.map((item) => {
        const timestamp = new Date(item.created_at).getTime();

        return {
          date: formatDate(item.created_at),
          fullDate: formatFullDate(item.created_at),
          value: item.total_value,
          cost: item.total_cost,
          profit: item.total_profit,
          returnPercent: item.total_return_percent,
          health: item.health_score,
          timestamp,
        };
      }),
    [history]
  );

  const chartData = useMemo(() => {
    if (range === "ALL" || allChartData.length === 0) {
      return allChartData;
    }

    const latestTimestamp =
      allChartData[allChartData.length - 1].timestamp;
    const minimumTimestamp =
      latestTimestamp -
      RANGE_DAYS[range] * 24 * 60 * 60 * 1000;

    return allChartData.filter(
      (item) => item.timestamp >= minimumTimestamp
    );
  }, [allChartData, range]);

  const periodMetrics = useMemo(() => {
    if (chartData.length === 0) {
      return {
        currentValue: 0,
        change: 0,
        changePercent: 0,
        currentProfit: 0,
      };
    }

    const first = chartData[0];
    const latest = chartData[chartData.length - 1];
    const change = latest.value - first.value;
    const changePercent =
      first.value > 0 ? (change / first.value) * 100 : 0;

    return {
      currentValue: latest.value,
      change,
      changePercent,
      currentProfit: latest.profit,
    };
  }, [chartData]);

  const aiSummary = useMemo(
    () => buildSummary(chartData, contributors),
    [chartData, contributors]
  );

  return (
    <section className="mt-8 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
            Portfolio Performance
          </p>

          <h2 className="mt-2 text-2xl font-bold">
            Value versus invested cost
          </h2>

          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Understand whether your portfolio is growing, how far it is
            above or below invested cost, and what changed across snapshots.
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
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
          Loading portfolio performance...
        </div>
      ) : (
        <>
          <section className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900">
            <div className="p-6 lg:p-8">
              <div className="flex flex-wrap items-start justify-between gap-5">
                <div>
                  <p className="text-sm text-slate-400">
                    Portfolio value
                  </p>

                  <p className="mt-2 text-4xl font-black tracking-tight text-white">
                    {formatMoney(periodMetrics.currentValue)}
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
                    <span className={getToneClass(periodMetrics.change)}>
                      {periodMetrics.change >= 0 ? "+" : ""}
                      {formatMoney(periodMetrics.change)}
                    </span>

                    <span className={getToneClass(periodMetrics.changePercent)}>
                      {periodMetrics.changePercent >= 0 ? "+" : ""}
                      {periodMetrics.changePercent.toFixed(2)}%
                    </span>

                    <span className="text-slate-500">
                      selected period
                    </span>
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 px-5 py-4 text-right">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Unrealized profit
                  </p>

                  <p
                    className={`mt-2 text-2xl font-bold ${getToneClass(
                      periodMetrics.currentProfit
                    )}`}
                  >
                    {formatMoney(periodMetrics.currentProfit)}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex flex-wrap gap-2">
                {ranges.map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => setRange(item)}
                    className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                      range === item
                        ? "bg-blue-600 text-white"
                        : "border border-slate-700 bg-slate-950 text-slate-400 hover:text-white"
                    }`}
                  >
                    {item}
                  </button>
                ))}
              </div>

              {chartData.length === 0 ? (
                <div className="mt-6 rounded-2xl border border-dashed border-slate-700 p-10 text-center">
                  <p className="font-semibold text-white">
                    No portfolio snapshots yet
                  </p>

                  <p className="mt-2 text-sm text-slate-400">
                    Save today&apos;s snapshot to begin tracking portfolio
                    value, invested cost, profit, and health over time.
                  </p>
                </div>
              ) : (
                <div className="mt-7 h-[420px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart
                      data={chartData}
                      margin={{
                        top: 10,
                        right: 20,
                        left: 10,
                        bottom: 0,
                      }}
                    >
                      <defs>
                        <linearGradient
                          id="portfolioValueFill"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor="#3b82f6"
                            stopOpacity={0.35}
                          />
                          <stop
                            offset="95%"
                            stopColor="#3b82f6"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>

                      <CartesianGrid
                        stroke="#1e293b"
                        strokeDasharray="3 3"
                        vertical={false}
                      />

                      <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        tickLine={false}
                        axisLine={false}
                        minTickGap={24}
                      />

                      <YAxis
                        stroke="#64748b"
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={formatCompactMoney}
                        width={78}
                      />

                      <Tooltip
                        content={<PortfolioTooltip />}
                        cursor={{
                          stroke: "#475569",
                          strokeDasharray: "4 4",
                        }}
                      />

                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        fill="url(#portfolioValueFill)"
                        dot={false}
                        activeDot={{
                          r: 5,
                          strokeWidth: 2,
                          fill: "#0f172a",
                        }}
                        name="Portfolio Value"
                      />

                      <Line
                        type="monotone"
                        dataKey="cost"
                        stroke="#94a3b8"
                        strokeWidth={2}
                        strokeDasharray="6 6"
                        dot={false}
                        activeDot={{
                          r: 4,
                        }}
                        name="Invested Cost"
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="mt-5 flex flex-wrap gap-5 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-blue-500" />
                  Portfolio value
                </div>

                <div className="flex items-center gap-2">
                  <span className="h-0.5 w-5 bg-slate-400" />
                  Invested cost
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-blue-500/20 bg-blue-500/5 p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-300">
              Performance Summary
            </p>

            <p className="mt-3 max-w-5xl text-sm leading-7 text-slate-300">
              {aiSummary}
            </p>
          </section>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              title="Latest Change"
              value={formatMoney(performance?.change ?? 0)}
              subtitle={`${(performance?.change_percent ?? 0).toFixed(2)}%`}
              tone={performance?.change ?? 0}
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
              tone={performance?.best_day_change ?? 0}
            />

            <MetricCard
              title="Worst Snapshot Move"
              value={formatMoney(performance?.worst_day_change ?? 0)}
              subtitle="Compared with prior snapshot"
              tone={performance?.worst_day_change ?? 0}
            />
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

          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
              What Changed?
            </p>

            <h3 className="mt-2 text-xl font-semibold">
              Snapshot comparison
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

function TooltipRow({
  label,
  value,
  tone = "text-white",
}: {
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-6">
      <span className="text-slate-400">{label}</span>
      <span className={`font-medium ${tone}`}>{value}</span>
    </div>
  );
}

function MetricCard({
  title,
  value,
  subtitle,
  tone,
}: {
  title: string;
  value: string;
  subtitle: string;
  tone?: number;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>

      <p
        className={`mt-2 text-2xl font-bold ${
          tone === undefined ? "text-white" : getToneClass(tone)
        }`}
      >
        {value}
      </p>

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
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <h3 className="text-xl font-semibold">{title}</h3>

      <div className="mt-5 space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-slate-500">
            No contributor data available.
          </p>
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
                <p className={getToneClass(item.profit)}>
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
