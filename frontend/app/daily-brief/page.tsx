"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";

type BriefItem = {
  category: string;
  severity: "high" | "medium" | "low" | "info";
  title: string;
  message: string;
  suggested_action?: string | null;
  symbols: string[];
};

type DailyBrief = {
  generated_at: string;
  greeting: string;
  headline: string;
  action: "HOLD" | "MONITOR" | "REVIEW";
  action_reason: string;
  portfolio_snapshot: {
    total_value: number;
    total_profit: number;
    total_return_percent: number;
    holdings_count: number;
    health_score: number;
    health_rating: string;
    concentration_risk: string;
  };
  priorities: BriefItem[];
  positive_signals: string[];
  risks: string[];
  recent_changes: string[];
  holdings_to_watch: string[];
  recommended_questions: string[];
  disclaimer: string;
};

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function percent(value: number) {
  return `${value.toFixed(2)}%`;
}

function actionStyle(
  action: DailyBrief["action"]
) {
  if (action === "REVIEW") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (action === "MONITOR") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
}

function severityStyle(
  severity: BriefItem["severity"]
) {
  if (severity === "high") {
    return "border-red-500/20 bg-red-500/5";
  }

  if (severity === "medium") {
    return "border-amber-500/20 bg-amber-500/5";
  }

  if (severity === "low") {
    return "border-emerald-500/20 bg-emerald-500/5";
  }

  return "border-slate-800 bg-slate-950";
}

export default function DailyBriefPage() {
  const [brief, setBrief] =
    useState<DailyBrief | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadBrief() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(
        "/portfolio/daily-brief",
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to generate the daily brief."
        );
      }

      setBrief(await response.json());
    } catch (requestError) {
      console.error(
        "Daily brief error:",
        requestError
      );

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load the daily brief."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadBrief();
  }, []);

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-7 lg:px-8">
        <div className="mx-auto max-w-6xl">
          {loading ? (
            <div className="flex min-h-[70vh] items-center justify-center">
              <div className="text-center">
                <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-slate-700 border-t-blue-400" />
                <p className="mt-4 text-slate-400">
                  Preparing your daily brief...
                </p>
              </div>
            </div>
          ) : error || !brief ? (
            <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-8 text-center">
              <h1 className="text-2xl font-bold">
                Daily brief unavailable
              </h1>
              <p className="mt-3 text-red-100/80">
                {error}
              </p>
              <button
                type="button"
                onClick={loadBrief}
                className="mt-5 rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500"
              >
                Try again
              </button>
            </div>
          ) : (
            <>
              <header className="flex flex-wrap items-start justify-between gap-5">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                    MarketMind Daily Brief
                  </p>
                  <h1 className="mt-2 text-3xl font-bold sm:text-4xl">
                    {brief.greeting}.
                  </h1>
                  <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-400">
                    {brief.headline}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={loadBrief}
                  className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-slate-300 hover:border-blue-500 hover:text-white"
                >
                  Refresh brief
                </button>
              </header>

              <section className="mt-7 overflow-hidden rounded-3xl border border-slate-800 bg-slate-900">
                <div className="p-6 sm:p-8">
                  <p className="text-sm text-slate-400">
                    Today&apos;s action
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-4">
                    <span
                      className={`rounded-full border px-5 py-2 text-xl font-black ${actionStyle(
                        brief.action
                      )}`}
                    >
                      {brief.action}
                    </span>

                    <p className="max-w-2xl text-lg font-semibold leading-8 text-white">
                      {brief.action_reason}
                    </p>
                  </div>
                </div>

                <div className="grid border-t border-slate-800 bg-slate-950/40 sm:grid-cols-2 lg:grid-cols-4">
                  <Metric
                    label="Portfolio value"
                    value={money(
                      brief.portfolio_snapshot.total_value
                    )}
                  />
                  <Metric
                    label="Total return"
                    value={percent(
                      brief.portfolio_snapshot.total_return_percent
                    )}
                  />
                  <Metric
                    label="Health"
                    value={`${brief.portfolio_snapshot.health_score.toFixed(
                      0
                    )}/100`}
                  />
                  <Metric
                    label="Concentration"
                    value={
                      brief.portfolio_snapshot.concentration_risk
                    }
                  />
                </div>
              </section>

              <section className="mt-7 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
                <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
                    Priorities
                  </p>
                  <h2 className="mt-2 text-2xl font-bold">
                    What deserves attention
                  </h2>

                  <div className="mt-5 space-y-3">
                    {brief.priorities.length > 0 ? (
                      brief.priorities.map(
                        (item, index) => (
                          <article
                            key={`${item.title}-${index}`}
                            className={`rounded-2xl border p-5 ${severityStyle(
                              item.severity
                            )}`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <h3 className="font-semibold text-white">
                                {item.title}
                              </h3>
                              <span className="rounded-full border border-current/20 px-2 py-1 text-xs uppercase text-slate-300">
                                {item.severity}
                              </span>
                            </div>

                            <p className="mt-2 text-sm leading-6 text-slate-400">
                              {item.message}
                            </p>

                            {item.suggested_action && (
                              <p className="mt-3 text-sm leading-6 text-slate-200">
                                {item.suggested_action}
                              </p>
                            )}
                          </article>
                        )
                      )
                    ) : (
                      <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
                        <p className="font-semibold text-emerald-300">
                          No urgent priorities
                        </p>
                        <p className="mt-2 text-sm text-slate-400">
                          Continue monitoring without reacting to ordinary noise.
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-6">
                  <ListCard
                    title="Positive signals"
                    items={brief.positive_signals}
                    empty="No positive signals available."
                  />
                  <ListCard
                    title="Risks"
                    items={brief.risks}
                    empty="No major risks detected."
                  />
                </div>
              </section>

              <section className="mt-7 grid gap-6 lg:grid-cols-2">
                <ListCard
                  title="Recent changes"
                  items={brief.recent_changes}
                  empty="Create another portfolio snapshot to compare changes."
                />

                <ListCard
                  title="Holdings to watch"
                  items={brief.holdings_to_watch}
                  empty="No individual holding needs special attention."
                />
              </section>

              <section className="mt-7 rounded-3xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
                  Continue with Copilot
                </p>
                <h2 className="mt-2 text-xl font-bold">
                  Questions worth asking
                </h2>

                <div className="mt-4 flex flex-wrap gap-2">
                  {brief.recommended_questions.map(
                    (question) => (
                      <span
                        key={question}
                        className="rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-slate-300"
                      >
                        {question}
                      </span>
                    )
                  )}
                </div>
              </section>

              <p className="mt-7 text-center text-xs leading-5 text-slate-500">
                {brief.disclaimer}
              </p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border-slate-800 p-5 sm:border-r last:border-r-0">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-xl font-bold capitalize text-white">
        {value}
      </p>
    </div>
  );
}

function ListCard({
  title,
  items,
  empty,
}: {
  title: string;
  items: string[];
  empty: string;
}) {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="text-lg font-semibold text-white">
        {title}
      </h2>

      <div className="mt-4 space-y-3">
        {(items.length > 0 ? items : [empty]).map(
          (item, index) => (
            <div
              key={`${item}-${index}`}
              className="flex items-start gap-3"
            >
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
              <p className="text-sm leading-6 text-slate-400">
                {item}
              </p>
            </div>
          )
        )}
      </div>
    </section>
  );
}
