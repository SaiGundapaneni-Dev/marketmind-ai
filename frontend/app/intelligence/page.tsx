"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";
import type {
  HoldingToWatch,
  IntelligenceListItem,
  PortfolioIntelligenceResponse,
} from "@/types/intelligence";

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

function simpleStatus(status?: string) {
  const value = status?.toLowerCase();

  if (value === "excellent" || value === "good") {
    return {
      title: "Your portfolio looks healthy.",
      classes: "border-[#10B981]/20 bg-[#10B981]/10 text-[#10B981]",
    };
  }

  if (value === "fair") {
    return {
      title: "Your portfolio looks okay, with a few things to watch.",
      classes: "border-[#F59E0B]/20 bg-[#F59E0B]/10 text-[#F59E0B]",
    };
  }

  if (value === "weak" || value === "critical") {
    return {
      title: "Your portfolio needs some attention.",
      classes: "border-red-500/20 bg-red-500/10 text-red-300",
    };
  }

  return {
    title: "Your portfolio has been reviewed.",
    classes: "border-white/10 bg-white/5 text-slate-300",
  };
}

export default function IntelligencePage() {
  const [data, setData] =
    useState<PortfolioIntelligenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [detailsOpen, setDetailsOpen] = useState(false);

  const loadIntelligence = useCallback(async (refresh = false) => {
    if (refresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");

    try {
      const response = await apiFetch("/portfolio/intelligence");

      if (!response.ok) {
        let message = "Unable to load portfolio details.";

        try {
          const errorData = await response.json();

          if (typeof errorData?.detail === "string") {
            message = errorData.detail;
          }
        } catch {
          // Keep fallback.
        }

        throw new Error(message);
      }

      const result: PortfolioIntelligenceResponse =
        await response.json();

      setData(result);
    } catch (requestError) {
      console.error("Portfolio details error:", requestError);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to Vestora."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadIntelligence();
    }, 0);

    return () => clearTimeout(timer);
  }, [loadIntelligence]);

  const primaryInsight = useMemo(
    () => data?.priority_insights?.[0],
    [data]
  );

  const holdingToWatch = useMemo(
    () => data?.holdings_to_watch?.[0],
    [data]
  );

  return (
    <main className="flex min-h-screen bg-[#020817] text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-8 lg:px-10">
        <div className="mx-auto max-w-6xl">
          <header className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3B82F6]">
                Portfolio
              </p>

              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
                Understand what you own.
              </h1>

              <p className="mt-3 max-w-2xl leading-7 text-slate-400">
                See what is working, what deserves attention, and why it matters.
              </p>
            </div>

            <button
              type="button"
              onClick={() => void loadIntelligence(true)}
              disabled={loading || refreshing}
              className="rounded-xl border border-white/10 bg-[#0F172A] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-[#3B82F6]/40 hover:text-white disabled:opacity-50"
            >
              {refreshing ? "Refreshing..." : "Refresh"}
            </button>
          </header>

          {loading && (
            <div className="mt-8 rounded-[28px] border border-white/10 bg-[#0F172A] p-10 text-center text-slate-400">
              Reviewing your portfolio...
            </div>
          )}

          {!loading && error && (
            <div className="mt-8 rounded-[28px] border border-red-500/20 bg-red-500/10 p-6">
              <p className="font-semibold text-red-300">
                Portfolio details could not be loaded
              </p>

              <p className="mt-2 text-sm leading-6 text-red-200/80">
                {error}
              </p>
            </div>
          )}

          {!loading && !error && data && (
            <div className="mt-8 space-y-6">
              <PortfolioHealth
                status={data.portfolio_status}
                summary={data.executive_summary}
              />

              <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                <article className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#3B82F6]">
                    What matters most
                  </p>

                  {primaryInsight ? (
                    <>
                      <h2 className="mt-4 text-2xl font-semibold">
                        {primaryInsight.title || "Portfolio review"}
                      </h2>

                      <p className="mt-4 leading-7 text-slate-300">
                        {primaryInsight.message ||
                          "This area deserves review before making new portfolio decisions."}
                      </p>

                      {primaryInsight.suggested_action && (
                        <div className="mt-6 rounded-2xl border border-[#3B82F6]/20 bg-[#3B82F6]/10 p-5">
                          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-300">
                            What to consider
                          </p>

                          <p className="mt-3 text-sm leading-6 text-blue-100">
                            {primaryInsight.suggested_action}
                          </p>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      <h2 className="mt-4 text-2xl font-semibold">
                        Nothing urgent right now.
                      </h2>

                      <p className="mt-4 leading-7 text-slate-300">
                        Vestora did not identify a portfolio issue that requires immediate attention.
                      </p>
                    </>
                  )}
                </article>

                <article className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#F59E0B]">
                    One thing to watch
                  </p>

                  {holdingToWatch ? (
                    <>
                      <h2 className="mt-4 text-2xl font-semibold">
                        {holdingToWatch.symbol}
                      </h2>

                      {holdingToWatch.name && (
                        <p className="mt-1 text-sm text-slate-500">
                          {holdingToWatch.name}
                        </p>
                      )}

                      <p className="mt-4 leading-7 text-slate-300">
                        {holdingToWatch.reason ||
                          `${holdingToWatch.symbol} currently deserves closer review.`}
                      </p>

                      <p className="mt-5 text-sm text-slate-400">
					  {typeof holdingToWatch.allocation_percent === "number"
						? `${holdingToWatch.allocation_percent.toFixed(1)}% of your portfolio`
						: "Portfolio allocation unavailable"}
					</p>
                    </>
                  ) : (
                    <>
                      <h2 className="mt-4 text-2xl font-semibold">
                        No holding stands out.
                      </h2>

                      <p className="mt-4 leading-7 text-slate-300">
                        No individual investment currently requires special attention.
                      </p>
                    </>
                  )}
                </article>
              </section>

              <section className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#10B981]">
                      Ask Vestora
                    </p>

                    <h2 className="mt-2 text-xl font-semibold">
                      Questions worth asking
                    </h2>
                  </div>

                  <Link
                    href="/copilot"
                    className="rounded-xl bg-[#3B82F6] px-4 py-2.5 text-sm font-semibold transition hover:bg-blue-500"
                  >
                    Open Ask Vestora
                  </Link>
                </div>

                <div className="mt-5 flex flex-wrap gap-3">
                  {(
                    data.recommended_questions?.length
                      ? data.recommended_questions
                      : [
                          "What should I focus on today?",
                          "Which holding deserves attention?",
                          "What changed recently?",
                        ]
                  ).map((question) => (
                    <Link
                      key={question}
                      href={`/copilot?question=${encodeURIComponent(question)}`}
                      className="rounded-full border border-white/10 bg-[#020817]/60 px-4 py-2 text-sm text-slate-300 transition hover:border-[#3B82F6]/40 hover:text-white"
                    >
                      {question}
                    </Link>
                  ))}
                </div>
              </section>

              <section className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
                <button
                  type="button"
                  onClick={() => setDetailsOpen((value) => !value)}
                  className="flex w-full items-center justify-between gap-4 text-left"
                >
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                      Advanced details
                    </p>

                    <h2 className="mt-2 text-xl font-semibold">
                      {detailsOpen ? "Hide deeper analysis" : "View deeper analysis"}
                    </h2>
                  </div>

                  <span className="text-2xl text-slate-500">
                    {detailsOpen ? "−" : "+"}
                  </span>
                </button>

                {detailsOpen && (
                  <div className="mt-6 space-y-6 border-t border-white/10 pt-6">
                    <div className="grid gap-6 lg:grid-cols-3">
                      <SimpleList
                        title="What is working"
                        items={data.strengths || []}
                        empty="No clear strengths identified yet."
                        tone="positive"
                      />

                      <SimpleList
                        title="What to watch"
                        items={data.risks || []}
                        empty="No major risks identified."
                        tone="warning"
                      />

                      <SimpleList
                        title="Possible improvements"
                        items={data.opportunities || []}
                        empty="No specific improvements identified."
                        tone="neutral"
                      />
                    </div>

                    <div className="grid gap-6 lg:grid-cols-2">
                      <SimpleTextList
                        title="Recent changes"
                        items={data.recent_changes || []}
                        empty="More snapshot history is needed."
                      />

                      <SimpleTextList
                        title="Why Vestora said this"
                        items={primaryInsight?.evidence || []}
                        empty="No additional evidence is available."
                      />
                    </div>
                  </div>
                )}
              </section>

              {data.disclaimer && (
                <p className="text-center text-xs leading-5 text-slate-600">
                  {data.disclaimer}
                </p>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function PortfolioHealth({
  status,
  summary,
}: {
  status?: string;
  summary?: string;
}) {
  const health = simpleStatus(status);

  return (
    <section className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-8">
      <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-[#10B981]/10 blur-3xl" />

      <div className="relative">
        <div
          className={`inline-flex rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] ${health.classes}`}
        >
          Portfolio health
        </div>

        <h2 className="mt-5 text-3xl font-semibold tracking-tight">
          {health.title}
        </h2>

        <p className="mt-4 max-w-3xl leading-7 text-slate-300">
          {summary ||
            "Vestora reviewed your portfolio and did not identify a major issue."}
        </p>
      </div>
    </section>
  );
}

function SimpleList({
  title,
  items,
  empty,
  tone,
}: {
  title: string;
  items: IntelligenceListItem[];
  empty: string;
  tone: "positive" | "warning" | "neutral";
}) {
  const dotClass =
    tone === "positive"
      ? "bg-[#10B981]"
      : tone === "warning"
        ? "bg-[#F59E0B]"
        : "bg-[#3B82F6]";

  return (
    <div className="rounded-2xl border border-white/10 bg-[#020817]/60 p-5">
      <p className="font-semibold">{title}</p>

      <div className="mt-4 space-y-4">
        {items.length ? (
          items.map((item, index) => (
            <div key={`${itemTitle(item)}-${index}`} className="flex gap-3">
              <span
                className={`mt-2 h-2 w-2 shrink-0 rounded-full ${dotClass}`}
              />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  {itemTitle(item)}
                </p>

                {itemDescription(item) && (
                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    {itemDescription(item)}
                  </p>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-500">{empty}</p>
        )}
      </div>
    </div>
  );
}

function SimpleTextList({
  title,
  items,
  empty,
}: {
  title: string;
  items: string[];
  empty: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#020817]/60 p-5">
      <p className="font-semibold">{title}</p>

      <div className="mt-4 space-y-3">
        {items.length ? (
          items.map((item, index) => (
            <p
              key={`${item}-${index}`}
              className="text-sm leading-6 text-slate-400"
            >
              • {item}
            </p>
          ))
        ) : (
          <p className="text-sm text-slate-500">{empty}</p>
        )}
      </div>
    </div>
  );
}
