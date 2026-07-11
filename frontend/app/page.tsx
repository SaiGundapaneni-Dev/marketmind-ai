"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import SummaryCard from "@/components/SummaryCard";
import HoldingsTable, {
  Holding,
} from "@/components/HoldingsTable";
import AddHoldingForm from "@/components/AddHoldingForm";
import AllocationChart from "@/components/AllocationChart";

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
  severity: "high" | "medium" | "low" | string;
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

type NewsItem = {
  title: string;
  url: string;
  source?: string;
  summary?: string;
  description?: string;
  sentiment?: string;
  published_at?: string;
  publishedAt?: string;
  published_date?: string;
  datetime?: string | number;
  relevance_score?: number;
  relevanceScore?: number;
};

const MIN_RELEVANCE_SCORE = 60;

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

function getRelevanceScore(item: NewsItem) {
  return Number(
    item.relevance_score ??
      item.relevanceScore ??
      0
  );
}

function getPublishedValue(item: NewsItem) {
  return (
    item.published_at ??
    item.publishedAt ??
    item.published_date ??
    item.datetime
  );
}

function formatNewsTime(item: NewsItem) {
  const value = getPublishedValue(item);

  if (!value) {
    return "Published time unavailable";
  }

  const date =
    typeof value === "number"
      ? new Date(
          value > 10_000_000_000
            ? value
            : value * 1000
        )
      : new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);
}

function getSentimentStyle(sentiment?: string) {
  const normalized = sentiment?.toLowerCase();

  if (normalized === "positive") {
    return "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
  }

  if (normalized === "negative") {
    return "border-red-500/40 bg-red-500/10 text-red-300";
  }

  return "border-slate-600 bg-slate-700/40 text-slate-300";
}

function getSeverityStyle(severity: string) {
  const normalized = severity.toLowerCase();

  if (normalized === "high") {
    return "border-red-500/30 bg-red-500/10 text-red-200";
  }

  if (normalized === "medium") {
    return "border-yellow-500/30 bg-yellow-500/10 text-yellow-100";
  }

  return "border-emerald-500/30 bg-emerald-500/10 text-emerald-100";
}

function getRiskStyle(riskLevel: string) {
  const normalized = riskLevel.toLowerCase();

  if (normalized === "high") {
    return "text-red-300";
  }

  if (normalized === "medium") {
    return "text-yellow-300";
  }

  return "text-emerald-300";
}

export default function Home() {
  const [portfolio, setPortfolio] =
    useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);

  const [ticker, setTicker] = useState("");
  const [news, setNews] = useState<NewsItem[]>([]);
  const [newsLoading, setNewsLoading] =
    useState(false);
  const [searchedTicker, setSearchedTicker] =
    useState("");
  const [newsError, setNewsError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:8000";

  useEffect(() => {
    async function loadPortfolio() {
      try {
        const response = await fetch(
          `${apiBaseUrl}/portfolio/`,
          {
            cache: "no-store",
          }
        );

        if (!response.ok) {
          setPortfolio(null);
          return;
        }

        const data: PortfolioData =
          await response.json();

        setPortfolio(data);
      } catch (error) {
        console.error(
          "Portfolio API error:",
          error
        );
        setPortfolio(null);
      } finally {
        setLoading(false);
      }
    }

    loadPortfolio();
  }, [apiBaseUrl]);

  async function searchNews() {
    const cleanTicker =
      ticker.trim().toUpperCase();

    if (!cleanTicker) {
      return;
    }

    setNewsLoading(true);
    setNews([]);
    setNewsError("");
    setSearchedTicker(cleanTicker);

    try {
      const response = await fetch(
        `${apiBaseUrl}/news/search/${cleanTicker}`,
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        setNews([]);
        setNewsError(
          "Unable to load news right now. Please try again."
        );
        return;
      }

      const data = await response.json();

      setNews(
        data.news ??
          data.articles ??
          data.results ??
          data ??
          []
      );
    } catch (error) {
      console.error("News API error:", error);

      setNews([]);
      setNewsError(
        "Unable to connect to the news API. Make sure the backend is running."
      );
    } finally {
      setNewsLoading(false);
    }
  }

  const relevantNews = news.filter(
    (item) =>
      getRelevanceScore(item) >=
      MIN_RELEVANCE_SCORE
  );

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-slate-400">
          Loading MarketMind AI...
        </p>
      </main>
    );
  }

  if (!portfolio) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
          <h1 className="text-2xl font-bold">
            MarketMind AI
          </h1>

          <p className="mt-3 text-slate-400">
            Unable to load portfolio data.
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Make sure the FastAPI backend and
            PostgreSQL database are running.
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
    health_score,
    actionable_insights,
    holdings,
  } = portfolio;

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8">
            <p className="text-sm font-medium text-blue-400">
              USA Portfolio
            </p>

            <h1 className="mt-1 text-3xl font-bold">
              Portfolio Dashboard
            </h1>

            <p className="mt-2 text-slate-400">
              Track performance, allocation,
              concentration risk, and portfolio
              intelligence.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <SummaryCard
              title="Total Value"
              value={formatMoney(
                summary.total_value
              )}
            />

            <SummaryCard
              title="Total Profit"
              value={formatMoney(
                summary.total_profit
              )}
            />

            <SummaryCard
              title="Total Return"
              value={formatPercent(
                summary.total_return_percent
              )}
            />

            <SummaryCard
              title="Holdings"
              value={`${summary.holdings_count}`}
            />
          </div>

          <section className="mt-8 grid gap-5 lg:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                Portfolio Health
              </p>

              <div className="mt-3 flex items-end gap-2">
                <span className="text-4xl font-bold">
                  {health_score.score.toFixed(2)}
                </span>

                <span className="pb-1 text-slate-400">
                  /100
                </span>
              </div>

              <p className="mt-2 text-lg font-semibold capitalize text-blue-300">
                {health_score.rating}
              </p>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                {health_score.message}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                Concentration Risk
              </p>

              <p
                className={`mt-3 text-3xl font-bold capitalize ${getRiskStyle(
                  concentration_risk.risk_level
                )}`}
              >
                {concentration_risk.risk_level}
              </p>

              <div className="mt-4 space-y-2 text-sm text-slate-300">
                <p>
                  Largest position:{" "}
                  {formatPercent(
                    concentration_risk.largest_position_percent
                  )}
                </p>

                <p>
                  Top three:{" "}
                  {formatPercent(
                    concentration_risk.top_three_percent
                  )}
                </p>
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                {concentration_risk.message}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-400">
                Largest Holding
              </p>

              {allocation.largest_holding ? (
                <>
                  <p className="mt-3 text-3xl font-bold">
                    {
                      allocation.largest_holding
                        .symbol
                    }
                  </p>

                  <p className="mt-1 text-slate-300">
                    {
                      allocation.largest_holding
                        .name
                    }
                  </p>

                  <div className="mt-4 space-y-2 text-sm text-slate-400">
                    <p>
                      Value:{" "}
                      {formatMoney(
                        allocation.largest_holding
                          .current_value
                      )}
                    </p>

                    <p>
                      Allocation:{" "}
                      {formatPercent(
                        allocation.largest_holding
                          .allocation_percent
                      )}
                    </p>
                  </div>
                </>
              ) : (
                <p className="mt-3 text-slate-400">
                  No priced holdings available.
                </p>
              )}
            </div>
          </section>

          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div>
              <p className="text-sm font-medium text-blue-400">
                Performance Intelligence
              </p>

              <h2 className="mt-1 text-xl font-semibold">
                Portfolio Performance
              </h2>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <PerformanceCard
                title="Top Performer"
                performer={
                  performance_insights.top_performer
                }
              />

              <PerformanceCard
                title="Weakest Performer"
                performer={
                  performance_insights.weakest_performer
                }
              />

              <PerformanceCard
                title="Largest Profit"
                performer={
                  performance_insights
                    .largest_profit_contributor
                }
              />

              <PerformanceCard
                title="Largest Loss"
                performer={
                  performance_insights
                    .largest_loss_contributor
                }
              />
            </div>

            <p className="mt-5 text-sm text-slate-400">
              {performance_insights.message}
            </p>
          </section>

          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-blue-400">
                  MarketMind Insights
                </p>

                <h2 className="mt-1 text-xl font-semibold">
                  Actionable Portfolio Insights
                </h2>
              </div>

              <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-sm text-slate-300">
                {actionable_insights.count} insights
              </span>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              {actionable_insights.items.map(
                (insight, index) => (
                  <div
                    key={`${insight.title}-${index}`}
                    className={`rounded-xl border p-5 ${getSeverityStyle(
                      insight.severity
                    )}`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-semibold">
                        {insight.title}
                      </h3>

                      <span className="rounded-full border border-current/20 px-2 py-1 text-xs font-medium uppercase">
                        {insight.severity}
                      </span>
                    </div>

                    <p className="mt-3 text-sm leading-6 opacity-90">
                      {insight.message}
                    </p>

                    <p className="mt-3 text-xs uppercase opacity-60">
                      {insight.category}
                    </p>
                  </div>
                )
              )}
            </div>

            <p className="mt-5 text-xs text-slate-500">
              {actionable_insights.disclaimer}
            </p>
          </section>

          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">
              Health Score Components
            </h2>

            <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <ScoreComponent
                title="Diversification"
                value={
                  health_score.components
                    .diversification_score
                }
              />

              <ScoreComponent
                title="Concentration"
                value={
                  health_score.components
                    .concentration_score
                }
              />

              <ScoreComponent
                title="Profitability"
                value={
                  health_score.components
                    .profitability_score
                }
              />

              <ScoreComponent
                title="Price Coverage"
                value={
                  health_score.components
                    .pricing_coverage_score
                }
              />
            </div>
          </section>

          <AddHoldingForm />

          <AllocationChart holdings={holdings} />

          <HoldingsTable holdings={holdings} />

          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-5">
              <h2 className="text-xl font-semibold text-white">
                Stock News
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Search real-time ticker news with
                relevance score, sentiment, and
                published time.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                value={ticker}
                onChange={(event) =>
                  setTicker(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    searchNews();
                  }
                }}
                placeholder="Enter ticker, e.g. NVDA"
                className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
              />

              <button
                onClick={searchNews}
                disabled={newsLoading}
                className="rounded-xl bg-blue-600 px-5 py-3 font-medium text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {newsLoading
                  ? "Searching..."
                  : "Search News"}
              </button>
            </div>

            {newsError &&
              !newsLoading && (
                <div className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 p-5">
                  <p className="font-medium text-red-200">
                    News API error
                  </p>

                  <p className="mt-1 text-sm text-red-300">
                    {newsError}
                  </p>
                </div>
              )}

            {searchedTicker &&
              !newsLoading &&
              !newsError &&
              relevantNews.length === 0 && (
                <div className="mt-5 rounded-xl border border-slate-700 bg-slate-950 p-5">
                  <p className="font-medium text-white">
                    No highly relevant news found for{" "}
                    {searchedTicker}.
                  </p>

                  <p className="mt-1 text-sm text-slate-400">
                    We filtered out weak or unrelated
                    articles to avoid showing noisy
                    results.
                  </p>
                </div>
              )}

            {relevantNews.length > 0 && (
              <div className="mt-5 space-y-4">
                {relevantNews.map(
                  (item, index) => {
                    const score =
                      getRelevanceScore(item);
                    const sentiment =
                      item.sentiment ?? "Neutral";

                    return (
                      <a
                        key={`${item.url}-${index}`}
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block rounded-xl border border-slate-700 bg-slate-950 p-5 transition hover:border-blue-500"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <h3 className="font-semibold leading-snug text-white">
                            {item.title}
                          </h3>

                          <div className="flex shrink-0 flex-col items-end gap-2">
                            <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300">
                              {score}% relevant
                            </span>

                            <span
                              className={`rounded-full border px-3 py-1 text-xs font-medium uppercase ${getSentimentStyle(
                                sentiment
                              )}`}
                            >
                              {sentiment}
                            </span>
                          </div>
                        </div>

                        {(item.summary ||
                          item.description) && (
                          <p className="mt-2 text-sm leading-6 text-slate-400">
                            {item.summary ??
                              item.description}
                          </p>
                        )}

                        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                          {item.source && (
                            <span>
                              {item.source}
                            </span>
                          )}

                          <span>
                            • Posted{" "}
                            {formatNewsTime(item)}
                          </span>
                        </div>
                      </a>
                    );
                  }
                )}
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}

function PerformanceCard({
  title,
  performer,
}: {
  title: string;
  performer: Performer | null;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      {performer ? (
        <>
          <p className="mt-2 text-xl font-bold">
            {performer.symbol}
          </p>

          <p
            className={`mt-2 font-medium ${
              performer.profit >= 0
                ? "text-emerald-300"
                : "text-red-300"
            }`}
          >
            {formatMoney(performer.profit)}
          </p>

          <p
            className={`mt-1 text-sm ${
              performer.profit_percent >= 0
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {formatPercent(
              performer.profit_percent
            )}
          </p>
        </>
      ) : (
        <p className="mt-2 text-slate-500">
          Not available
        </p>
      )}
    </div>
  );
}

function ScoreComponent({
  title,
  value,
}: {
  title: string;
  value: number;
}) {
  const width = Math.min(
    Math.max((value / 25) * 100, 0),
    100
  );

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-400">
          {title}
        </p>

        <p className="font-semibold">
          {value.toFixed(2)}/25
        </p>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-blue-500"
          style={{
            width: `${width}%`,
          }}
        />
      </div>
    </div>
  );
}