"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { apiFetch } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import HoldingsTable, { Holding } from "@/components/HoldingsTable";
import PortfolioTimeline from "@/components/PortfolioTimeline";

type PortfolioSummary = {
  total_cost: number;
  total_value: number;
  total_profit: number;
  total_return_percent: number;
  holdings_count: number;
  priced_holdings_count: number;
  unpriced_holdings_count: number;
};

type LargestHolding = {
  symbol: string;
  name: string;
  current_value: number;
  allocation_percent: number;
};

type PortfolioAllocation = {
  by_asset_type: {
    asset_type: string;
    value: number;
    allocation_percent: number;
  }[];
  largest_holding: LargestHolding | null;
};

type ConcentrationRisk = {
  risk_level: string;
  largest_position_percent: number;
  top_three_percent: number;
  concentrated_positions: {
    symbol: string;
    name: string;
    allocation_percent: number;
  }[];
  message: string;
};

type Performer = {
  symbol: string;
  name: string;
  profit: number;
  profit_percent: number;
};

type PerformanceInsights = {
  top_performer: Performer | null;
  weakest_performer: Performer | null;
  largest_profit_contributor: Performer | null;
  largest_loss_contributor: Performer | null;
  profitable_holdings_count: number;
  losing_holdings_count: number;
  breakeven_holdings_count: number;
  message: string;
};

type HealthScore = {
  score: number;
  rating: string;
  components: {
    diversification_score: number;
    concentration_score: number;
    profitability_score: number;
    pricing_coverage_score: number;
  };
  message: string;
};

type ActionableInsight = {
  category: string;
  severity: string;
  title: string;
  message: string;
};

type ActionableInsights = {
  count: number;
  items: ActionableInsight[];
  disclaimer: string;
};

type PortfolioData = {
  summary: PortfolioSummary;
  allocation: PortfolioAllocation;
  concentration_risk: ConcentrationRisk;
  performance_insights: PerformanceInsights;
  health_score: HealthScore;
  actionable_insights: ActionableInsights;
  holdings: Holding[];
};

type PriorityInsight = {
  priority: number;
  category: string;
  severity: string;
  title: string;
  message: string;
  evidence: string[];
  suggested_action: string;
  affected_symbols: string[];
};

type HoldingToWatch = {
  symbol: string;
  name: string;
  allocation_percent: number;
  profit: number;
  profit_percent: number;
  reason: string;
};

type PortfolioIntelligence = {
  portfolio_status: string;
  executive_summary: string;
  priority_insights: PriorityInsight[];
  strengths: string[];
  risks: string[];
  opportunities: string[];
  holdings_to_watch: HoldingToWatch[];
  recent_changes: string[];
  recommended_questions: string[];
  disclaimer: string;
};

type StoredUser = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
};

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value: number) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function getGreeting() {
  const hour = new Date().getHours();

  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function getHealthCopy(status?: string) {
  const normalized = status?.toLowerCase();

  if (normalized === "excellent" || normalized === "good") {
    return {
      title: "Your portfolio looks healthy.",
      text: "Nothing in your portfolio currently stands out as a major concern.",
      tone: "positive",
    };
  }

  if (normalized === "fair") {
    return {
      title: "Your portfolio looks okay.",
      text: "A few areas deserve attention, but nothing looks immediately alarming.",
      tone: "warning",
    };
  }

  if (normalized === "weak" || normalized === "critical") {
    return {
      title: "Your portfolio needs attention.",
      text: "There are a few issues worth reviewing before making new investment decisions.",
      tone: "negative",
    };
  }

  return {
    title: "Your portfolio has been reviewed.",
    text: "Vestora is monitoring your holdings for meaningful changes.",
    tone: "neutral",
  };
}

export default function Home() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [intelligence, setIntelligence] =
    useState<PortfolioIntelligence | null>(null);
  const [user, setUser] = useState<StoredUser | null>(null);
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setMounted(true);

    try {
      const stored = localStorage.getItem("vestora_user");
      setUser(stored ? (JSON.parse(stored) as StoredUser) : null);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [portfolioResponse, intelligenceResponse] =
          await Promise.all([
            apiFetch("/portfolio/", { cache: "no-store" }),
            apiFetch("/portfolio/intelligence", { cache: "no-store" }),
          ]);

        if (!portfolioResponse.ok) {
          throw new Error("Unable to load portfolio data.");
        }

        setPortfolio(await portfolioResponse.json());

        if (intelligenceResponse.ok) {
          setIntelligence(await intelligenceResponse.json());
        } else {
          setIntelligence(null);
        }
      } catch (requestError) {
        console.error("Dashboard load error:", requestError);

        setPortfolio(null);
        setIntelligence(null);

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load your portfolio."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const primaryInsight = useMemo(
    () => intelligence?.priority_insights?.[0] ?? null,
    [intelligence]
  );

  const primaryHolding = useMemo(
    () => intelligence?.holdings_to_watch?.[0] ?? null,
    [intelligence]
  );

  if (loading || !mounted) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020817] text-white">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-[#3B82F6]" />
          <p className="mt-4 text-sm text-slate-400">
            Reviewing your portfolio...
          </p>
        </div>
      </main>
    );
  }

  if (!portfolio) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020817] px-6 text-white">
        <div className="max-w-lg rounded-3xl border border-red-500/20 bg-red-500/10 p-8 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-red-300">
            Vestora
          </p>

          <h1 className="mt-3 text-2xl font-bold">
            We couldn&apos;t load your portfolio
          </h1>

          <p className="mt-3 text-sm leading-6 text-red-100/80">
            {error || "Please try again in a moment."}
          </p>
        </div>
      </main>
    );
  }

  const { summary, allocation, concentration_risk, holdings } = portfolio;
  const health = getHealthCopy(intelligence?.portfolio_status);
  const largest = allocation.largest_holding;
  const firstName = user?.name?.split(" ")[0] || "";

  const attentionTitle = primaryInsight
    ? "One thing deserves your attention."
    : "Nothing urgent needs your attention.";

  const attentionMessage =
    primaryInsight?.message ||
    intelligence?.executive_summary ||
    "Your portfolio does not show a material issue right now.";

  const actionMessage =
    primaryInsight?.suggested_action ||
    "Stay consistent with your plan and avoid reacting to ordinary market noise.";

  const watchMessage =
    primaryHolding?.reason ||
    (largest && largest.allocation_percent >= 25
      ? `${largest.symbol} now represents ${largest.allocation_percent.toFixed(
          1
        )}% of your portfolio. Consider other investments before adding more.`
      : concentration_risk.message ||
        "Your portfolio does not currently show an unusual concentration issue.");

  return (
    <main className="flex min-h-screen bg-[#020817] text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-8 lg:px-10">
        <div className="mx-auto max-w-6xl">
          <header className="mb-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#3B82F6]/20 bg-[#3B82F6]/10 px-3 py-1.5">
              <span className="h-2 w-2 rounded-full bg-[#10B981]" />
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-200">
                Today
              </span>
            </div>

            <h1 className="mt-5 text-3xl font-semibold tracking-tight sm:text-4xl lg:text-5xl">
              {getGreeting()}
              {firstName ? `, ${firstName}.` : "."}
            </h1>

            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-400">
              Here&apos;s how your portfolio is doing and what deserves your attention.
            </p>
          </header>

          <section className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#0F172A] p-6 shadow-2xl shadow-black/20 lg:p-8">
            <div className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-[#3B82F6]/10 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-20 left-20 h-56 w-56 rounded-full bg-[#10B981]/10 blur-3xl" />

            <div className="relative flex flex-wrap items-end justify-between gap-6">
              <div>
                <p className="text-sm text-slate-400">Your portfolio</p>

                <p className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
                  {formatMoney(summary.total_value)}
                </p>

                <div className="mt-4 flex flex-wrap items-center gap-3">
                  <span
                    className={`font-semibold ${
                      summary.total_profit >= 0
                        ? "text-[#10B981]"
                        : "text-red-300"
                    }`}
                  >
                    {summary.total_profit >= 0 ? "+" : ""}
                    {formatMoney(summary.total_profit)}
                  </span>

                  <span
                    className={
                      summary.total_return_percent >= 0
                        ? "text-[#10B981]"
                        : "text-red-300"
                    }
                  >
                    {formatPercent(summary.total_return_percent)}
                  </span>

                  <span className="text-sm text-slate-500">
                    all time
                  </span>
                </div>
              </div>

              <div
                className={`max-w-sm rounded-2xl border px-5 py-4 ${
                  health.tone === "positive"
                    ? "border-[#10B981]/20 bg-[#10B981]/10"
                    : health.tone === "warning"
                      ? "border-[#F59E0B]/20 bg-[#F59E0B]/10"
                      : health.tone === "negative"
                        ? "border-red-500/20 bg-red-500/10"
                        : "border-white/10 bg-white/5"
                }`}
              >
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
                  Portfolio health
                </p>

                <p className="mt-2 font-semibold text-white">
                  {health.title}
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {health.text}
                </p>
              </div>
            </div>
          </section>

          <PortfolioTimeline />

          <section className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <article className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
              <div className="flex items-center gap-2">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#10B981]/10 text-[#10B981]">
                  ✓
                </span>

                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#10B981]">
                  What matters today
                </p>
              </div>

              <h2 className="mt-5 text-2xl font-semibold">
                {attentionTitle}
              </h2>

              <p className="mt-4 max-w-2xl leading-7 text-slate-300">
                {attentionMessage}
              </p>

              <div className="mt-6 rounded-2xl border border-white/10 bg-[#020817]/60 p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#3B82F6]">
                  What to consider
                </p>

                <p className="mt-3 text-sm leading-6 text-slate-300">
                  {actionMessage}
                </p>
              </div>
            </article>

            <article className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
              <div className="flex items-center gap-2">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#F59E0B]/10 text-[#F59E0B]">
                  !
                </span>

                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#F59E0B]">
                  One thing to watch
                </p>
              </div>

              <h2 className="mt-5 text-2xl font-semibold">
                {primaryHolding?.symbol || largest?.symbol || "Portfolio balance"}
              </h2>

              <p className="mt-4 leading-7 text-slate-300">
                {watchMessage}
              </p>

              <Link
                href="/intelligence"
                className="mt-6 inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-[#3B82F6]/50 hover:bg-[#3B82F6]/10"
              >
                Understand why
                <span>→</span>
              </Link>
            </article>
          </section>

          <section className="mt-8 rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#3B82F6]">
                  Your investments
                </p>

                <h2 className="mt-2 text-2xl font-semibold">
                  What you own
                </h2>

                <p className="mt-2 text-sm text-slate-400">
                  {summary.holdings_count} holdings in your portfolio.
                </p>
              </div>

              <Link
                href="/intelligence"
                className="rounded-xl border border-white/10 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-[#3B82F6]/50 hover:text-white"
              >
                View portfolio
              </Link>
            </div>

            <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
              <HoldingsTable holdings={holdings} />
            </div>
          </section>

          <section className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/copilot"
              className="rounded-xl bg-[#3B82F6] px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              Ask Vestora
            </Link>

            <Link
              href="/goals"
              className="rounded-xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-[#10B981]/40 hover:text-white"
            >
              View goals
            </Link>
          </section>

          <p className="mt-8 text-center text-xs leading-5 text-slate-600">
            {intelligence?.disclaimer ||
              "Vestora provides informational portfolio insights and not personalized financial advice."}
          </p>
        </div>
      </section>
    </main>
  );
}
