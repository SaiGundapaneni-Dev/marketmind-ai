"use client";

import { useEffect, useMemo, useState } from "react";

import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";

type Severity =
  | "critical"
  | "important"
  | "informational"
  | "noise";

type Alert = {
  symbol: string;
  company_name?: string | null;
  source_type: "portfolio" | "watchlist" | "both";
  severity: Severity;
  event_type: string;
  title: string;
  summary?: string | null;
  publisher?: string | null;
  link?: string | null;
  published_at?: string | null;
  sentiment: string;
  relevance_score: number;
  materiality_score: number;
  portfolio_owned: boolean;
  portfolio_allocation_percent: number;
  thesis_exists: boolean;
  thesis_impact:
    | "supports"
    | "contradicts"
    | "neutral"
    | "unknown";
  why_it_matters: string;
  suggested_action: string;
};

type WatchtowerResponse = {
  generated_at: string;
  monitored_symbols: number;
  critical_count: number;
  important_count: number;
  informational_count: number;
  noise_count: number;
  silence_filter_active: boolean;
  silence_message: string;
  alerts: Alert[];
  disclaimer: string;
};

const severityOrder: Severity[] = [
  "critical",
  "important",
  "informational",
  "noise",
];

function severityClass(
  severity: Severity
) {
  if (severity === "critical") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (severity === "important") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  if (severity === "informational") {
    return "border-blue-500/30 bg-blue-500/10 text-blue-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

function thesisClass(
  impact: Alert["thesis_impact"]
) {
  if (impact === "contradicts") {
    return "text-red-300";
  }

  if (impact === "supports") {
    return "text-emerald-300";
  }

  return "text-slate-400";
}

function formatTime(value?: string | null) {
  if (!value) {
    return "Time unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export default function WatchtowerPage() {
  const [data, setData] =
    useState<WatchtowerResponse | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [filter, setFilter] =
    useState<Severity | "all">("all");

  const [source, setSource] =
    useState<"all" | "portfolio" | "watchlist">(
      "all"
    );

  const [includeNoise, setIncludeNoise] =
    useState(false);

  async function loadWatchtower(
    noise = includeNoise
  ) {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(
        `/watchtower?include_noise=${noise}`,
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to load AI Watchtower."
        );
      }

      setData(await response.json());
    } catch (requestError) {
      console.error(
        "Watchtower error:",
        requestError
      );

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load AI Watchtower."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadWatchtower(false);
  }, []);

  const alerts = useMemo(() => {
    if (!data) {
      return [];
    }

    return data.alerts.filter(
      (item) => {
        const matchesSeverity =
          filter === "all" ||
          item.severity === filter;

        const matchesSource =
          source === "all" ||
          item.source_type === source ||
          item.source_type === "both";

        return (
          matchesSeverity &&
          matchesSource
        );
      }
    );
  }, [data, filter, source]);

  function toggleNoise() {
    const next = !includeNoise;
    setIncludeNoise(next);
    setFilter("all");
    loadWatchtower(next);
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-7 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <header className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                Material Event Intelligence
              </p>

              <h1 className="mt-2 text-3xl font-bold sm:text-4xl">
                AI Watchtower
              </h1>

              <p className="mt-3 max-w-3xl text-slate-400">
                Focus on events that may affect your portfolio,
                watchlist, or saved investment theses.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                loadWatchtower(
                  includeNoise
                )
              }
              disabled={loading}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-semibold text-slate-300 hover:border-blue-500 hover:text-white disabled:opacity-50"
            >
              {loading
                ? "Scanning..."
                : "Refresh scan"}
            </button>
          </header>

          {loading ? (
            <div className="flex min-h-[55vh] items-center justify-center">
              <div className="text-center">
                <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-slate-700 border-t-blue-400" />

                <p className="mt-4 text-slate-400">
                  Scanning monitored symbols...
                </p>
              </div>
            </div>
          ) : error || !data ? (
            <div className="mt-7 rounded-2xl border border-red-500/20 bg-red-500/10 p-7 text-center">
              <p className="font-semibold text-red-300">
                Watchtower unavailable
              </p>

              <p className="mt-2 text-sm text-slate-400">
                {error}
              </p>
            </div>
          ) : (
            <>
              <section
                className={`mt-7 rounded-3xl border p-6 ${
                  data.silence_filter_active
                    ? "border-emerald-500/20 bg-emerald-500/5"
                    : "border-amber-500/20 bg-amber-500/5"
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Silence Filter
                    </p>

                    <h2 className="mt-2 text-2xl font-bold">
                      {data.silence_filter_active
                        ? "No material event requires attention"
                        : "Material events detected"}
                    </h2>

                    <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-300">
                      {data.silence_message}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={toggleNoise}
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-300 hover:border-blue-500"
                  >
                    {includeNoise
                      ? "Hide noise"
                      : "Show filtered noise"}
                  </button>
                </div>
              </section>

              <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
                <Metric
                  label="Monitored"
                  value={data.monitored_symbols}
                />
                <Metric
                  label="Critical"
                  value={data.critical_count}
                  tone="critical"
                />
                <Metric
                  label="Important"
                  value={data.important_count}
                  tone="important"
                />
                <Metric
                  label="Informational"
                  value={
                    data.informational_count
                  }
                  tone="informational"
                />
                <Metric
                  label="Noise"
                  value={data.noise_count}
                />
              </section>

              <section className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900 p-4">
                <div className="flex flex-wrap gap-2">
                  <FilterButton
                    active={filter === "all"}
                    onClick={() =>
                      setFilter("all")
                    }
                    label="All"
                  />

                  {severityOrder.map(
                    (severity) => (
                      <FilterButton
                        key={severity}
                        active={
                          filter === severity
                        }
                        onClick={() =>
                          setFilter(severity)
                        }
                        label={severity}
                      />
                    )
                  )}
                </div>

                <select
                  value={source}
                  onChange={(event) =>
                    setSource(
                      event.target.value as
                        | "all"
                        | "portfolio"
                        | "watchlist"
                    )
                  }
                  className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-300 outline-none focus:border-blue-500"
                >
                  <option value="all">
                    Portfolio + Watchlist
                  </option>
                  <option value="portfolio">
                    Portfolio only
                  </option>
                  <option value="watchlist">
                    Watchlist only
                  </option>
                </select>
              </section>

              <section className="mt-6 space-y-5">
                {alerts.length > 0 ? (
                  alerts.map(
                    (item, index) => (
                      <article
                        key={`${item.symbol}-${item.title}-${index}`}
                        className="rounded-3xl border border-slate-800 bg-slate-900 p-6"
                      >
                        <div className="flex flex-wrap items-start justify-between gap-4">
                          <div>
                            <div className="flex flex-wrap items-center gap-3">
                              <p className="text-2xl font-bold">
                                {item.symbol}
                              </p>

                              <span
                                className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase ${severityClass(
                                  item.severity
                                )}`}
                              >
                                {item.severity}
                              </span>

                              <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs capitalize text-slate-400">
                                {item.source_type}
                              </span>
                            </div>

                            <p className="mt-1 text-sm text-slate-500">
                              {item.company_name ||
                                "Company name unavailable"}
                            </p>
                          </div>

                          <div className="text-right">
                            <p className="text-xs uppercase tracking-wider text-slate-500">
                              Materiality
                            </p>

                            <p className="mt-1 text-2xl font-bold">
                              {item.materiality_score.toFixed(
                                0
                              )}
                              /100
                            </p>
                          </div>
                        </div>

                        <h2 className="mt-5 text-xl font-semibold leading-8 text-white">
                          {item.title}
                        </h2>

                        {item.summary && (
                          <p className="mt-2 text-sm leading-6 text-slate-400">
                            {item.summary}
                          </p>
                        )}

                        <div className="mt-5 grid gap-5 lg:grid-cols-2">
                          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                            <p className="text-sm font-semibold text-white">
                              Why this matters
                            </p>

                            <p className="mt-2 text-sm leading-6 text-slate-400">
                              {item.why_it_matters}
                            </p>
                          </div>

                          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                            <p className="text-sm font-semibold text-white">
                              Suggested action
                            </p>

                            <p className="mt-2 text-sm leading-6 text-slate-300">
                              {item.suggested_action}
                            </p>
                          </div>
                        </div>

                        <div className="mt-5 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                          <span>
                            Allocation:{" "}
                            {item.portfolio_owned
                              ? `${item.portfolio_allocation_percent.toFixed(
                                  2
                                )}%`
                              : "Not owned"}
                          </span>

                          <span>•</span>

                          <span
                            className={thesisClass(
                              item.thesis_impact
                            )}
                          >
                            Thesis:{" "}
                            {item.thesis_impact}
                          </span>

                          <span>•</span>

                          <span className="capitalize">
                            Sentiment:{" "}
                            {item.sentiment}
                          </span>

                          <span>•</span>

                          <span>
                            {formatTime(
                              item.published_at
                            )}
                          </span>

                          {item.publisher && (
                            <>
                              <span>•</span>
                              <span>
                                {item.publisher}
                              </span>
                            </>
                          )}
                        </div>

                        {item.link && (
                          <a
                            href={item.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-5 inline-block text-sm font-semibold text-blue-400 hover:text-blue-300"
                          >
                            Read source article →
                          </a>
                        )}
                      </article>
                    )
                  )
                ) : (
                  <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-900/50 p-10 text-center">
                    <p className="font-semibold text-white">
                      No alerts match the current filters.
                    </p>

                    <p className="mt-2 text-sm text-slate-500">
                      Change the severity or source filter,
                      or refresh the Watchtower scan.
                    </p>
                  </div>
                )}
              </section>

              <p className="mt-7 text-center text-xs leading-5 text-slate-500">
                {data.disclaimer}
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
  tone,
}: {
  label: string;
  value: number;
  tone?: Severity;
}) {
  const valueClass =
    tone === "critical"
      ? "text-red-300"
      : tone === "important"
        ? "text-amber-300"
        : tone === "informational"
          ? "text-blue-300"
          : "text-white";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">
        {label}
      </p>

      <p
        className={`mt-2 text-3xl font-bold ${valueClass}`}
      >
        {value}
      </p>
    </div>
  );
}

function FilterButton({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-4 py-2 text-sm font-medium capitalize transition ${
        active
          ? "bg-blue-600 text-white"
          : "border border-slate-700 bg-slate-950 text-slate-400 hover:text-white"
      }`}
    >
      {label}
    </button>
  );
}
