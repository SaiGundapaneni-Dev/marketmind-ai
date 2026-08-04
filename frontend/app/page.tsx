"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import HoldingsTable, { Holding } from "@/components/HoldingsTable";
import AddHoldingForm from "@/components/AddHoldingForm";
import AllocationChart from "@/components/AllocationChart";
import PortfolioTimeline from "@/components/PortfolioTimeline";
import PortfolioScoreHero from "@/components/PortfolioScoreHero";
import TodayIntelligence from "@/components/TodayIntelligence";
import ActionMemo from "@/components/ActionMemo";
import AIPortfolioCoach from "@/components/AIPortfolioCoach";
import type { PortfolioScoreResponse } from "@/types/portfolio-score";

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

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value: number) {
  return `${value.toFixed(2)}%`;
}

export default function Home() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [portfolioScore, setPortfolioScore] =
    useState<PortfolioScoreResponse | null>(null);
  const [intelligence, setIntelligence] =
    useState<PortfolioIntelligence | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [portfolioResponse, scoreResponse, intelligenceResponse] =
          await Promise.all([
            apiFetch("/portfolio/", { cache: "no-store" }),
            apiFetch("/portfolio/score", { cache: "no-store" }),
            apiFetch("/portfolio/intelligence", { cache: "no-store" }),
          ]);

        if (!portfolioResponse.ok) {
          throw new Error("Unable to load portfolio data.");
        }

        setPortfolio(await portfolioResponse.json());

        if (scoreResponse.ok) {
          setPortfolioScore(await scoreResponse.json());
        } else {
          setPortfolioScore(null);
        }

        if (intelligenceResponse.ok) {
          setIntelligence(await intelligenceResponse.json());
        } else {
          setIntelligence(null);
        }
      } catch (requestError) {
        console.error("Dashboard load error:", requestError);
        setPortfolio(null);
        setPortfolioScore(null);
        setIntelligence(null);
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load the dashboard."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-slate-700 border-t-blue-400" />
          <p className="mt-4 text-slate-400">
            Preparing today&apos;s intelligence...
          </p>
        </div>
      </main>
    );
  }

  if (!portfolio) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="max-w-lg rounded-2xl border border-red-500/20 bg-red-500/10 p-8 text-center">
          <h1 className="text-2xl font-bold">Dashboard unavailable</h1>
          <p className="mt-3 text-red-100/80">
            {error || "Unable to load your portfolio."}
          </p>
          <p className="mt-2 text-sm text-slate-400">
            Confirm FastAPI and PostgreSQL are running, then refresh.
          </p>
        </div>
      </main>
    );
  }

  const {
    summary,
    allocation,
    concentration_risk,
    performance_insights,
    holdings,
  } = portfolio;

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-7 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <header className="mb-7">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
              MarketMind Daily
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Here&apos;s what matters today.
            </h1>
            <p className="mt-3 max-w-3xl text-slate-400">
              A focused view of portfolio quality, material risks,
              and the actions that deserve your attention.
            </p>
          </header>

          <AIPortfolioCoach />

          <div className="mt-6">
            {portfolioScore ? (
              <PortfolioScoreHero score={portfolioScore} />
          ) : (
            <section className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-6">
              <p className="font-semibold text-amber-200">
                Portfolio score unavailable
              </p>
              <p className="mt-2 text-sm text-amber-100/70">
                Today&apos;s intelligence and portfolio data remain available.
              </p>
            </section>
            )}
          </div>

          <section className="mt-6 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <TodayIntelligence intelligence={intelligence} />
            <ActionMemo
              intelligence={intelligence}
              healthScore={portfolio.health_score.score}
              healthRating={portfolio.health_score.rating}
            />
          </section>

          <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <SnapshotCard
              label="Portfolio value"
              value={formatMoney(summary.total_value)}
              detail={`${summary.holdings_count} holdings`}
            />
            <SnapshotCard
              label="Total return"
              value={formatPercent(summary.total_return_percent)}
              detail={formatMoney(summary.total_profit)}
              tone={summary.total_profit >= 0 ? "positive" : "negative"}
            />
            <SnapshotCard
              label="Largest position"
              value={allocation.largest_holding?.symbol || "N/A"}
              detail={
                allocation.largest_holding
                  ? formatPercent(allocation.largest_holding.allocation_percent)
                  : "No priced holdings"
              }
            />
            <SnapshotCard
              label="Concentration risk"
              value={concentration_risk.risk_level}
              detail={`${formatPercent(
                concentration_risk.top_three_percent
              )} in top three`}
              tone={
                concentration_risk.risk_level.toLowerCase() === "high"
                  ? "negative"
                  : concentration_risk.risk_level.toLowerCase() === "medium"
                    ? "warning"
                    : "positive"
              }
            />
          </section>

          <section className="mt-8 grid gap-6 xl:grid-cols-[1fr_0.9fr]">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
                Allocation
              </p>
              <h2 className="mt-2 text-xl font-semibold">
                Portfolio composition
              </h2>
              <div className="mt-5">
                <AllocationChart holdings={holdings} />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
                Performance
              </p>
              <h2 className="mt-2 text-xl font-semibold">
                Leaders and laggards
              </h2>

              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <PerformanceCard
                  title="Top performer"
                  performer={performance_insights.top_performer}
                />
                <PerformanceCard
                  title="Weakest performer"
                  performer={performance_insights.weakest_performer}
                />
                <PerformanceCard
                  title="Largest profit"
                  performer={
                    performance_insights.largest_profit_contributor
                  }
                />
                <PerformanceCard
                  title="Largest loss"
                  performer={
                    performance_insights.largest_loss_contributor
                  }
                />
              </div>
            </div>
          </section>

          <PortfolioTimeline />

          <section className="mt-8">
            <div className="mb-4">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
                Portfolio management
              </p>
              <h2 className="mt-2 text-2xl font-bold">
                Holdings and theses
              </h2>
              <p className="mt-2 text-sm text-slate-400">
                Add positions, monitor performance, and review the
                original reason behind each investment.
              </p>
            </div>

            <AddHoldingForm />
            <HoldingsTable holdings={holdings} />
          </section>

          <p className="mt-8 text-center text-xs leading-5 text-slate-500">
            {intelligence?.disclaimer ||
              "These insights are informational and are not personalized financial advice."}
          </p>
        </div>
      </section>
    </main>
  );
}

function SnapshotCard({
  label,
  value,
  detail,
  tone = "neutral",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "neutral" | "positive" | "warning" | "negative";
}) {
  const valueClass =
    tone === "positive"
      ? "text-emerald-300"
      : tone === "warning"
        ? "text-amber-300"
        : tone === "negative"
          ? "text-red-300"
          : "text-white";

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-2xl font-bold capitalize ${valueClass}`}>
        {value}
      </p>
      <p className="mt-2 text-xs text-slate-500">{detail}</p>
    </article>
  );
}

function PerformanceCard({
  title,
  performer,
}: {
  title: string;
  performer: Performer | null;
}) {
  if (!performer) {
    return (
      <article className="rounded-xl border border-slate-800 bg-slate-950 p-4">
        <p className="text-sm text-slate-400">{title}</p>
        <p className="mt-3 text-sm text-slate-500">Not available</p>
      </article>
    );
  }

  const positive = performer.profit >= 0;

  return (
    <article className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">{title}</p>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div>
          <p className="text-xl font-bold">{performer.symbol}</p>
          <p className="mt-1 text-xs text-slate-500">{performer.name}</p>
        </div>

        <div className="text-right">
          <p
            className={`font-semibold ${
              positive ? "text-emerald-300" : "text-red-300"
            }`}
          >
            {formatPercent(performer.profit_percent)}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {formatMoney(performer.profit)}
          </p>
        </div>
      </div>
    </article>
  );
}
