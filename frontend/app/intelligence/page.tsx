"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import IntelligenceCard from "@/components/IntelligenceCard";
import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";
import type {
  HoldingToWatch,
  IntelligenceInsight,
  IntelligenceListItem,
  PortfolioIntelligenceResponse,
} from "@/types/intelligence";

function formatMoney(value?: number) {
  if (typeof value !== "number") return "N/A";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatPercent(value?: number) {
  return typeof value === "number" ? `${value.toFixed(2)}%` : "N/A";
}

function titleCase(value?: string) {
  if (!value) return "Unknown";

  return value
    .replaceAll("_", " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0]?.toUpperCase() + word.slice(1))
    .join(" ");
}

function statusClasses(status?: string) {
  switch (status?.toLowerCase()) {
    case "excellent":
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
    case "good":
      return "border-blue-500/30 bg-blue-500/10 text-blue-300";
    case "fair":
      return "border-yellow-500/30 bg-yellow-500/10 text-yellow-300";
    case "weak":
    case "critical":
      return "border-red-500/30 bg-red-500/10 text-red-300";
    default:
      return "border-slate-700 bg-slate-800 text-slate-300";
  }
}

function severityClasses(severity?: string) {
  switch (severity?.toLowerCase()) {
    case "critical":
    case "high":
      return "border-red-500/30 bg-red-500/10 text-red-300";
    case "medium":
      return "border-yellow-500/30 bg-yellow-500/10 text-yellow-300";
    case "low":
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
    default:
      return "border-slate-700 bg-slate-800 text-slate-300";
  }
}

function itemTitle(item: IntelligenceListItem) {
  if (typeof item === "string") return item;

  return (
    item.title ||
    item.message ||
    item.description ||
    item.symbol ||
    "Portfolio insight"
  );
}

function itemDescription(item: IntelligenceListItem) {
  if (typeof item === "string") return "";

  if (item.title && item.message) return item.message;
  if (item.title && item.description) return item.description;

  return item.suggested_action || "";
}

export default function IntelligencePage() {
  const [data, setData] =
    useState<PortfolioIntelligenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadIntelligence = useCallback(async (refresh = false) => {
    refresh ? setRefreshing(true) : setLoading(true);
    setError("");

    try {
      const response = await apiFetch("/portfolio/intelligence");

      if (!response.ok) {
        let message = "Unable to load portfolio intelligence.";

        try {
          const errorData = await response.json();
          if (typeof errorData?.detail === "string") {
            message = errorData.detail;
          }
        } catch {
          // Keep fallback message.
        }

        throw new Error(message);
      }

      const result: PortfolioIntelligenceResponse =
        await response.json();

      setData(result);
    } catch (requestError) {
      console.error("Portfolio intelligence error:", requestError);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the Vestora API."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadIntelligence();
  }, [loadIntelligence]);

  const primaryInsight = useMemo(
    () => data?.priority_insights?.[0],
    [data]
  );

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          <Header
            refreshing={refreshing}
            disabled={loading}
            onRefresh={() => void loadIntelligence(true)}
          />

          {loading && <LoadingState />}

          {!loading && error && (
            <ErrorState
              message={error}
              onRetry={() => void loadIntelligence()}
            />
          )}

          {!loading && !error && data && (
            <div className="mt-8 space-y-6">
              <Overview
                data={data}
                primaryInsight={primaryInsight}
              />

              <div className="grid gap-6 xl:grid-cols-3">
                <InsightListCard
                  title="Strengths"
                  subtitle="What is currently working well"
                  items={data.strengths || []}
                  emptyMessage="No major portfolio strengths were identified yet."
                  tone="positive"
                />

                <InsightListCard
                  title="Risks"
                  subtitle="Areas that may require attention"
                  items={data.risks || []}
                  emptyMessage="No major portfolio risks were identified."
                  tone="negative"
                />

                <InsightListCard
                  title="Opportunities"
                  subtitle="Possible areas to improve"
                  items={data.opportunities || []}
                  emptyMessage="No specific opportunities were identified yet."
                  tone="neutral"
                />
              </div>

              <div className="grid gap-6 xl:grid-cols-2">
                <HoldingsCard
                  holdings={data.holdings_to_watch || []}
                />
                <ChangesCard
                  changes={data.recent_changes || []}
                />
              </div>

              <QuestionsCard
                questions={data.recommended_questions || []}
              />

              {data.disclaimer && (
                <p className="rounded-xl border border-slate-800 bg-slate-900/60 px-5 py-4 text-xs leading-6 text-slate-500">
                  {data.disclaimer}
                </p>
              )}
            </div>
          )}

          {!loading && !error && !data && (
            <EmptyState onRetry={() => void loadIntelligence()} />
          )}
        </div>
      </section>
    </main>
  );
}

function Header({
  refreshing,
  disabled,
  onRefresh,
}: {
  refreshing: boolean;
  disabled: boolean;
  onRefresh: () => void;
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div>
        <p className="text-sm font-medium text-blue-400">
          Personalized Analysis
        </p>
        <h1 className="mt-1 text-3xl font-bold">
          Portfolio Intelligence
        </h1>
        <p className="mt-2 max-w-3xl text-slate-400">
          A prioritized view of portfolio strengths, risks,
          opportunities, holdings to watch, and recent changes.
        </p>
      </div>

      <button
        type="button"
        onClick={onRefresh}
        disabled={disabled || refreshing}
        className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        {refreshing ? "Refreshing..." : "Refresh intelligence"}
      </button>
    </div>
  );
}

function Overview({
  data,
  primaryInsight,
}: {
  data: PortfolioIntelligenceResponse;
  primaryInsight?: IntelligenceInsight;
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.4fr]">
      <IntelligenceCard
        title="Portfolio Status"
        subtitle="Current overall intelligence assessment"
      >
        <span
          className={`inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${statusClasses(
            data.portfolio_status
          )}`}
        >
          {titleCase(data.portfolio_status)}
        </span>

        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm font-medium text-slate-400">
            Executive Summary
          </p>
          <p className="mt-3 leading-7 text-slate-200">
            {data.executive_summary ||
              "No executive summary is available yet."}
          </p>
        </div>
      </IntelligenceCard>

      <IntelligenceCard
        title="Top Priority"
        subtitle="The most important area to review first"
      >
        {primaryInsight ? (
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-blue-400">
                  Priority {primaryInsight.priority ?? 1}
                </p>
                <h3 className="mt-2 text-xl font-semibold">
                  {primaryInsight.title || "Portfolio review"}
                </h3>
              </div>

              <span
                className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase ${severityClasses(
                  primaryInsight.severity
                )}`}
              >
                {titleCase(primaryInsight.severity || "informational")}
              </span>
            </div>

            <p className="mt-4 leading-7 text-slate-300">
              {primaryInsight.message ||
                "Review this area before making new portfolio decisions."}
            </p>

            {!!primaryInsight.evidence?.length && (
              <div className="mt-5">
                <p className="text-sm font-semibold">Evidence</p>
                <div className="mt-2 space-y-2">
                  {primaryInsight.evidence.map((item, index) => (
                    <p
                      key={`${item}-${index}`}
                      className="text-sm leading-6 text-slate-400"
                    >
                      • {item}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {primaryInsight.suggested_action && (
              <div className="mt-5 rounded-xl border border-blue-500/20 bg-blue-500/10 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-blue-300">
                  Suggested Review
                </p>
                <p className="mt-2 text-sm leading-6 text-blue-100">
                  {primaryInsight.suggested_action}
                </p>
              </div>
            )}
          </div>
        ) : (
          <EmptyMessage message="No urgent portfolio priority was identified." />
        )}
      </IntelligenceCard>
    </div>
  );
}

function InsightListCard({
  title,
  subtitle,
  items,
  emptyMessage,
  tone,
}: {
  title: string;
  subtitle: string;
  items: IntelligenceListItem[];
  emptyMessage: string;
  tone: "positive" | "negative" | "neutral";
}) {
  const dot =
    tone === "positive"
      ? "bg-emerald-400"
      : tone === "negative"
        ? "bg-red-400"
        : "bg-blue-400";

  return (
    <IntelligenceCard title={title} subtitle={subtitle}>
      {items.length ? (
        <div className="space-y-4">
          {items.map((item, index) => (
            <div
              key={`${itemTitle(item)}-${index}`}
              className="rounded-xl border border-slate-800 bg-slate-950 p-4"
            >
              <div className="flex items-start gap-3">
                <span
                  className={`mt-2 h-2.5 w-2.5 shrink-0 rounded-full ${dot}`}
                />
                <div>
                  <p className="font-medium leading-6">
                    {itemTitle(item)}
                  </p>
                  {itemDescription(item) && (
                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {itemDescription(item)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyMessage message={emptyMessage} />
      )}
    </IntelligenceCard>
  );
}

function HoldingsCard({
  holdings,
}: {
  holdings: HoldingToWatch[];
}) {
  return (
    <IntelligenceCard
      title="Holdings to Watch"
      subtitle="Positions that currently deserve closer review"
    >
      {holdings.length ? (
        <div className="space-y-4">
          {holdings.map((holding, index) => (
            <div
              key={`${holding.symbol}-${index}`}
              className="rounded-xl border border-slate-800 bg-slate-950 p-5"
            >
              <div className="flex flex-wrap justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold">
                    {holding.symbol || "Unknown"}
                  </p>
                  {holding.name && (
                    <p className="mt-1 text-sm text-slate-400">
                      {holding.name}
                    </p>
                  )}
                </div>

                <div className="text-right">
                  <p className="font-medium">
                    {formatPercent(holding.allocation_percent)}
                  </p>
                  <p className="text-xs text-slate-500">
                    Portfolio allocation
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Metric
                  label="Unrealized Profit"
                  value={formatMoney(holding.profit)}
                />
                <Metric
                  label="Unrealized Return"
                  value={formatPercent(holding.profit_percent)}
                />
              </div>

              {holding.reason && (
                <p className="mt-4 rounded-lg bg-slate-900 px-4 py-3 text-sm leading-6 text-slate-300">
                  {holding.reason}
                </p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <EmptyMessage message="No holding currently requires special attention." />
      )}
    </IntelligenceCard>
  );
}

function ChangesCard({ changes }: { changes: string[] }) {
  return (
    <IntelligenceCard
      title="Recent Changes"
      subtitle="What changed since the previous portfolio snapshot"
    >
      {changes.length ? (
        <div className="space-y-3">
          {changes.map((change, index) => (
            <div
              key={`${change}-${index}`}
              className="flex gap-3 rounded-xl border border-slate-800 bg-slate-950 p-4"
            >
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-500/10 text-xs font-bold text-blue-300">
                {index + 1}
              </div>
              <p className="text-sm leading-6 text-slate-300">
                {change}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <EmptyMessage message="Not enough snapshot history is available yet." />
      )}
    </IntelligenceCard>
  );
}

function QuestionsCard({ questions }: { questions: string[] }) {
  const defaults = [
    "What should I focus on today?",
    "Which holding deserves attention?",
    "What changed since yesterday?",
  ];

  return (
    <IntelligenceCard
      title="Ask Vestora Next"
      subtitle="Suggested Copilot questions based on your portfolio"
    >
      <div className="flex flex-wrap gap-3">
        {(questions.length ? questions : defaults).map((question) => (
          <Link
            key={question}
            href={`/copilot?question=${encodeURIComponent(question)}`}
            className="rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
          >
            {question}
          </Link>
        ))}
      </div>
    </IntelligenceCard>
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
    <div className="rounded-lg bg-slate-900 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-200">{value}</p>
    </div>
  );
}

function EmptyMessage({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/60 p-5 text-sm leading-6 text-slate-400">
      {message}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="mt-8 grid gap-6">
      <div className="h-44 animate-pulse rounded-2xl border border-slate-800 bg-slate-900" />
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="h-72 animate-pulse rounded-2xl border border-slate-800 bg-slate-900" />
        <div className="h-72 animate-pulse rounded-2xl border border-slate-800 bg-slate-900" />
      </div>
    </div>
  );
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="mt-8 rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
      <h2 className="font-semibold text-red-300">
        Portfolio intelligence could not be loaded
      </h2>
      <p className="mt-2 text-sm text-red-200">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 rounded-xl border border-red-400/30 px-4 py-2 text-sm font-medium text-red-200 transition hover:bg-red-500/10"
      >
        Try again
      </button>
    </div>
  );
}

function EmptyState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="mt-8 rounded-2xl border border-dashed border-slate-700 bg-slate-900/50 p-10 text-center">
      <h2 className="text-xl font-semibold">
        No intelligence available
      </h2>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-400">
        Add holdings and create portfolio snapshots before generating
        personalized intelligence.
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-5 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold transition hover:bg-blue-500"
      >
        Try again
      </button>
    </div>
  );
}
