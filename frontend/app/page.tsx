"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import SummaryCard from "@/components/SummaryCard";
import HoldingsTable, { Holding } from "@/components/HoldingsTable";
import AddHoldingForm from "@/components/AddHoldingForm";
import AllocationChart from "@/components/AllocationChart";

type PortfolioData = {
  summary: {
    total_cost: number;
    total_value: number;
    total_profit: number;
    total_return_percent: number;
  };
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

function getRelevanceScore(item: NewsItem) {
  return Number(item.relevance_score ?? item.relevanceScore ?? 0);
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
      ? new Date(value > 10_000_000_000 ? value : value * 1000)
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

export default function Home() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);

  const [ticker, setTicker] = useState("");
  const [news, setNews] = useState<NewsItem[]>([]);
  const [newsLoading, setNewsLoading] = useState(false);
  const [searchedTicker, setSearchedTicker] = useState("");
  const [newsError, setNewsError] = useState("");

  useEffect(() => {
    async function loadPortfolio() {
      try {
        const response = await fetch("http://127.0.0.1:8000/portfolio/", {
          cache: "no-store",
        });

        if (!response.ok) {
          setPortfolio(null);
          return;
        }

        const data = await response.json();
        setPortfolio(data);
      } catch (error) {
        console.error("Portfolio API error:", error);
        setPortfolio(null);
      } finally {
        setLoading(false);
      }
    }

    loadPortfolio();
  }, []);

  async function searchNews() {
    const cleanTicker = ticker.trim().toUpperCase();

    if (!cleanTicker) return;

    setNewsLoading(true);
    setNews([]);
    setNewsError("");
    setSearchedTicker(cleanTicker);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/news/search/${cleanTicker}`,
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        setNews([]);
        setNewsError("Unable to load news right now. Please try again.");
        return;
      }

      const data = await response.json();
      setNews(data.news ?? data.articles ?? data.results ?? data ?? []);
    } catch (error) {
      console.error("News API error:", error);
      setNews([]);
      setNewsError("Unable to connect to the news API. Make sure the backend is running.");
    } finally {
      setNewsLoading(false);
    }
  }

  const relevantNews = news.filter((item) => {
    return getRelevanceScore(item) >= MIN_RELEVANCE_SCORE;
  });

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-slate-400">Loading MarketMind AI...</p>
      </main>
    );
  }

  if (!portfolio) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
          <h1 className="text-2xl font-bold">MarketMind AI</h1>

          <p className="mt-3 text-slate-400">
            Unable to load portfolio data.
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Make sure the FastAPI backend and PostgreSQL database are running.
          </p>
        </div>
      </main>
    );
  }

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
              Track your US holdings, performance, allocation, and future AI insights.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <SummaryCard
              title="Total Value"
              value={formatMoney(portfolio.summary.total_value)}
            />

            <SummaryCard
              title="Total Profit"
              value={formatMoney(portfolio.summary.total_profit)}
            />

            <SummaryCard
              title="Total Return"
              value={`${portfolio.summary.total_return_percent.toFixed(2)}%`}
            />

            <SummaryCard
              title="Holdings"
              value={`${portfolio.holdings.length}`}
            />
          </div>

          <AddHoldingForm />

          <AllocationChart holdings={portfolio.holdings} />

          <HoldingsTable holdings={portfolio.holdings} />

          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-5">
              <h2 className="text-xl font-semibold text-white">
                Stock News
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Search real-time ticker news with relevance score, sentiment, and published time.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                value={ticker}
                onChange={(event) => setTicker(event.target.value)}
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
                {newsLoading ? "Searching..." : "Search News"}
              </button>
            </div>

            {newsError && !newsLoading && (
              <div className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 p-5">
                <p className="font-medium text-red-200">News API error</p>
                <p className="mt-1 text-sm text-red-300">{newsError}</p>
              </div>
            )}

            {searchedTicker && !newsLoading && !newsError && relevantNews.length === 0 && (
              <div className="mt-5 rounded-xl border border-slate-700 bg-slate-950 p-5">
                <p className="font-medium text-white">
                  No highly relevant news found for {searchedTicker}.
                </p>

                <p className="mt-1 text-sm text-slate-400">
                  We filtered out weak or unrelated articles to avoid showing noisy results.
                </p>
              </div>
            )}

            {relevantNews.length > 0 && (
              <div className="mt-5 space-y-4">
                {relevantNews.map((item, index) => {
                  const score = getRelevanceScore(item);
                  const sentiment = item.sentiment ?? "Neutral";

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

                      {(item.summary || item.description) && (
                        <p className="mt-2 text-sm leading-6 text-slate-400">
                          {item.summary ?? item.description}
                        </p>
                      )}

                      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        {item.source && <span>{item.source}</span>}
                        <span>• Posted {formatNewsTime(item)}</span>
                      </div>
                    </a>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
