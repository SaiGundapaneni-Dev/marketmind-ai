"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type MarketMindScore = {
  score: number;
  rating: string;
  interpretation: string;
  reasons: string[];
  warnings: string[];
};

type StockData = {
  symbol: string;
  company_name?: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  current_price?: number;
  currency?: string;
  website?: string;
  summary?: string;
  pe_ratio?: number;
  forward_pe?: number;
  eps?: number;
  profit_margin?: number;
  revenue_growth?: number;
  fifty_two_week_high?: number;
  fifty_two_week_low?: number;
  analyst_target_price?: number;
  recommendation?: string;
  marketmind_score?: MarketMindScore;
  error?: string;
};

type NewsArticle = {
  title?: string;
  publisher?: string;
  link?: string;
  published_at?: string;
  summary?: string;
  sentiment?: string;
};

type StockAnalysis = {
  symbol: string;
  status: string;
  error?: string;
  stock?: StockData;
  news_summary?: {
    article_count: number;
    positive_count: number;
    negative_count: number;
    neutral_count: number;
    overall_sentiment: string;
    articles: NewsArticle[];
  };
  bull_case?: string[];
  bear_case?: string[];
  key_risks?: string[];
  why_moving?: string;
  portfolio_exposure?: {
    owned: boolean;
    quantity: number;
    current_value: number;
    allocation_percent: number;
    profit: number;
    profit_percent: number;
    message: string;
  };
  recommendation?: {
    label: string;
    score: number;
    confidence: number;
    reason: string;
    disclaimer: string;
  };
};

function MetricCard({
  title,
  value,
  suffix = "",
  multiplier = 1,
}: {
  title: string;
  value?: number | string;
  suffix?: string;
  multiplier?: number;
}) {
  let displayValue = "N/A";

  if (typeof value === "number") {
    displayValue = `${(value * multiplier).toFixed(2)}${suffix}`;
  } else if (typeof value === "string" && value.length > 0) {
    displayValue = value.toUpperCase();
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-1 text-xl font-bold">{displayValue}</p>
    </div>
  );
}

function formatMoney(value?: number) {
  if (typeof value !== "number") return "N/A";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatMarketCap(value?: number) {
  if (!value) return "N/A";
  if (value >= 1_000_000_000_000) {
    return `$${(value / 1_000_000_000_000).toFixed(2)}T`;
  }
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`;
  }
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`;
  }
  return `$${value.toLocaleString()}`;
}

function sentimentStyle(sentiment?: string) {
  const normalized = sentiment?.toLowerCase();

  if (normalized === "positive") {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (normalized === "negative") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

export default function StockSearchPage() {
  const [symbol, setSymbol] = useState("");
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [quantity, setQuantity] = useState("");
  const [averagePrice, setAveragePrice] = useState("");
  const [message, setMessage] = useState("");
  const [adding, setAdding] = useState(false);

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  async function searchStock(event: React.FormEvent) {
    event.preventDefault();

    const cleanSymbol = symbol.trim().toUpperCase();
    if (!cleanSymbol) return;

    setLoading(true);
    setAnalysis(null);
    setMessage("");

    try {
      const response = await fetch(
        `${apiBaseUrl}/stocks/analyze/${cleanSymbol}`,
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error("Stock analysis request failed");
      }

      const data: StockAnalysis = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error("Stock analysis error:", error);
      setAnalysis({
        symbol: cleanSymbol,
        status: "error",
        error:
          "Unable to analyze this stock. Check the FastAPI backend connection.",
      });
    } finally {
      setLoading(false);
    }
  }

  async function addToPortfolio() {
    const stock = analysis?.stock;

    if (!stock || analysis?.error) return;

    if (!quantity || !averagePrice) {
      setMessage("Please enter quantity and average price.");
      return;
    }

    if (Number(quantity) <= 0 || Number(averagePrice) <= 0) {
      setMessage("Quantity and average price must be greater than zero.");
      return;
    }

    setAdding(true);
    setMessage("Adding to portfolio...");

    try {
      const response = await fetch(
        `${apiBaseUrl}/portfolio/holdings`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            asset_type: "US",
            symbol: stock.symbol,
            name: stock.company_name || stock.symbol,
            quantity: Number(quantity),
            average_price: Number(averagePrice),
            currency: "USD",
            portfolio_id: 1,
          }),
        }
      );

      if (!response.ok) {
        setMessage("Failed to add stock to portfolio.");
        return;
      }

      setMessage(`${stock.symbol} added to portfolio successfully.`);
      setQuantity("");
      setAveragePrice("");
    } catch (error) {
      console.error("Add holding error:", error);
      setMessage("Unable to connect to MarketMind API.");
    } finally {
      setAdding(false);
    }
  }

  const stock = analysis?.stock;

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          <div>
            <p className="text-sm font-medium text-blue-400">
              Stock Intelligence
            </p>
            <h1 className="mt-1 text-3xl font-bold">
              Unified Company Research
            </h1>
            <p className="mt-2 text-slate-400">
              Combine fundamentals, MarketMind scoring, relevant news,
              portfolio exposure, bull and bear cases, and an explainable
              research classification.
            </p>
          </div>

          <form onSubmit={searchStock} className="mt-8 flex gap-3">
            <input
              className="w-full rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none transition focus:border-blue-500"
              placeholder="Enter symbol, e.g. NVDA"
              value={symbol}
              onChange={(event) => setSymbol(event.target.value.toUpperCase())}
              required
            />

            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </form>

          {loading && (
            <div className="mt-6 rounded-xl border border-blue-500/20 bg-blue-500/10 p-4 text-blue-200">
              Building the unified MarketMind research report...
            </div>
          )}

          {analysis && (
            <div className="mt-8 space-y-6">
              {analysis.error || !stock ? (
                <div className="rounded-2xl border border-red-900 bg-slate-900 p-6">
                  <p className="text-red-400">
                    {analysis.error || "Stock analysis is unavailable."}
                  </p>
                </div>
              ) : (
                <>
                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                    <div className="flex flex-wrap items-start justify-between gap-5">
                      <div>
                        <p className="text-sm text-blue-400">Company Snapshot</p>
                        <h2 className="mt-1 text-3xl font-bold">
                          {stock.company_name || stock.symbol} ({stock.symbol})
                        </h2>
                        <p className="mt-2 text-slate-400">
                          {stock.sector || "Sector unavailable"} •{" "}
                          {stock.industry || "Industry unavailable"}
                        </p>
                      </div>

                      {analysis.recommendation && (
                        <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 px-5 py-4 text-right">
                          <p className="text-xs uppercase tracking-wide text-blue-300">
                            Research Classification
                          </p>
                          <p className="mt-1 text-xl font-bold capitalize">
                            {analysis.recommendation.label}
                          </p>
                          <p className="mt-1 text-sm text-slate-300">
                            Confidence: {analysis.recommendation.confidence}%
                          </p>
                        </div>
                      )}
                    </div>

                    <div className="mt-6 grid gap-4 md:grid-cols-3">
                      <MetricCard
                        title="Current Price"
                        value={`${stock.currency || "USD"} ${
                          stock.current_price ?? "N/A"
                        }`}
                      />
                      <MetricCard
                        title="Market Cap"
                        value={formatMarketCap(stock.market_cap)}
                      />
                      <MetricCard
                        title="Analyst View"
                        value={stock.recommendation || "N/A"}
                      />
                    </div>
                  </section>

                  {stock.marketmind_score && (
                    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                      <p className="text-sm font-medium text-blue-400">
                        MarketMind Score
                      </p>

                      <div className="mt-3 flex flex-wrap items-end gap-4">
                        <h2 className="text-4xl font-bold">
                          {stock.marketmind_score.score}/100
                        </h2>
                        <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-sm font-semibold">
                          {stock.marketmind_score.rating}
                        </span>
                      </div>

                      <p className="mt-4 max-w-3xl text-slate-300">
                        {stock.marketmind_score.interpretation}
                      </p>

                      <div className="mt-5 grid gap-4 lg:grid-cols-2">
                        <InsightList
                          title="Positive Signals"
                          items={stock.marketmind_score.reasons}
                        />
                        <InsightList
                          title="Data Warnings"
                          items={stock.marketmind_score.warnings}
                          emptyText="No major data warnings."
                        />
                      </div>
                    </section>
                  )}

                  <section className="grid gap-6 lg:grid-cols-2">
                    <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-6">
                      <h2 className="text-xl font-semibold text-emerald-300">
                        Bull Case
                      </h2>
                      <InsightList items={analysis.bull_case || []} />
                    </div>

                    <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6">
                      <h2 className="text-xl font-semibold text-red-300">
                        Bear Case
                      </h2>
                      <InsightList items={analysis.bear_case || []} />
                    </div>
                  </section>

                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                    <p className="text-sm font-medium text-blue-400">
                      Fundamental Analysis
                    </p>
                    <h2 className="mt-1 text-xl font-semibold">
                      Valuation & Growth Metrics
                    </h2>

                    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      <MetricCard title="P/E Ratio" value={stock.pe_ratio} />
                      <MetricCard title="Forward P/E" value={stock.forward_pe} />
                      <MetricCard title="EPS" value={stock.eps} />
                      <MetricCard
                        title="Profit Margin"
                        value={stock.profit_margin}
                        multiplier={100}
                        suffix="%"
                      />
                      <MetricCard
                        title="Revenue Growth"
                        value={stock.revenue_growth}
                        multiplier={100}
                        suffix="%"
                      />
                      <MetricCard
                        title="Analyst Target"
                        value={stock.analyst_target_price}
                      />
                      <MetricCard
                        title="52-Week High"
                        value={stock.fifty_two_week_high}
                      />
                      <MetricCard
                        title="52-Week Low"
                        value={stock.fifty_two_week_low}
                      />
                    </div>
                  </section>

                  <section className="grid gap-6 lg:grid-cols-2">
                    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                      <h2 className="text-xl font-semibold">Key Risks</h2>
                      <InsightList items={analysis.key_risks || []} />
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                      <h2 className="text-xl font-semibold">
                        Why the Stock May Be Moving
                      </h2>
                      <p className="mt-4 leading-7 text-slate-300">
                        {analysis.why_moving}
                      </p>
                    </div>
                  </section>

                  {analysis.news_summary && (
                    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                      <div className="flex flex-wrap items-center justify-between gap-4">
                        <div>
                          <p className="text-sm font-medium text-blue-400">
                            News Intelligence
                          </p>
                          <h2 className="mt-1 text-xl font-semibold">
                            Recent Relevant Coverage
                          </h2>
                        </div>

                        <span
                          className={`rounded-full border px-3 py-1 text-xs font-medium uppercase ${sentimentStyle(
                            analysis.news_summary.overall_sentiment
                          )}`}
                        >
                          {analysis.news_summary.overall_sentiment}
                        </span>
                      </div>

                      <div className="mt-5 grid gap-4 md:grid-cols-4">
                        <MetricCard
                          title="Articles"
                          value={analysis.news_summary.article_count}
                        />
                        <MetricCard
                          title="Positive"
                          value={analysis.news_summary.positive_count}
                        />
                        <MetricCard
                          title="Neutral"
                          value={analysis.news_summary.neutral_count}
                        />
                        <MetricCard
                          title="Negative"
                          value={analysis.news_summary.negative_count}
                        />
                      </div>

                      {analysis.news_summary.articles.length > 0 && (
                        <div className="mt-6 space-y-4">
                          {analysis.news_summary.articles.map((article, index) => (
                            <div
                              key={`${article.title}-${index}`}
                              className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                            >
                              <div className="flex items-start justify-between gap-4">
                                <div>
                                  <h3 className="font-semibold">
                                    {article.title || "Untitled"}
                                  </h3>
                                  <p className="mt-1 text-sm text-slate-400">
                                    {article.publisher || "Unknown Publisher"}
                                  </p>
                                </div>

                                <span
                                  className={`rounded-full border px-3 py-1 text-xs uppercase ${sentimentStyle(
                                    article.sentiment
                                  )}`}
                                >
                                  {article.sentiment || "neutral"}
                                </span>
                              </div>

                              {article.summary && (
                                <p className="mt-3 text-sm leading-6 text-slate-400">
                                  {article.summary}
                                </p>
                              )}

                              {article.link && (
                                <a
                                  href={article.link}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="mt-4 inline-block text-sm text-blue-400 hover:underline"
                                >
                                  Read article
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </section>
                  )}

                  {analysis.portfolio_exposure && (
                    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                      <p className="text-sm font-medium text-blue-400">
                        Portfolio Impact
                      </p>
                      <h2 className="mt-1 text-xl font-semibold">
                        Your Exposure to {stock.symbol}
                      </h2>

                      <p className="mt-3 text-slate-300">
                        {analysis.portfolio_exposure.message}
                      </p>

                      {analysis.portfolio_exposure.owned && (
                        <div className="mt-5 grid gap-4 md:grid-cols-4">
                          <MetricCard
                            title="Quantity"
                            value={analysis.portfolio_exposure.quantity}
                          />
                          <MetricCard
                            title="Current Value"
                            value={formatMoney(
                              analysis.portfolio_exposure.current_value
                            )}
                          />
                          <MetricCard
                            title="Allocation"
                            value={analysis.portfolio_exposure.allocation_percent}
                            suffix="%"
                          />
                          <MetricCard
                            title="Unrealized Return"
                            value={analysis.portfolio_exposure.profit_percent}
                            suffix="%"
                          />
                        </div>
                      )}
                    </section>
                  )}

                  {analysis.recommendation && (
                    <section className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-6">
                      <p className="text-sm font-medium text-blue-400">
                        Explainable Recommendation
                      </p>
                      <div className="mt-2 flex flex-wrap items-end gap-4">
                        <h2 className="text-3xl font-bold capitalize">
                          {analysis.recommendation.label}
                        </h2>
                        <span className="text-slate-400">
                          {analysis.recommendation.score.toFixed(2)}/100
                        </span>
                      </div>

                      <p className="mt-4 leading-7 text-slate-300">
                        {analysis.recommendation.reason}
                      </p>
                      <p className="mt-4 text-xs text-slate-500">
                        {analysis.recommendation.disclaimer}
                      </p>
                    </section>
                  )}

                  {stock.summary && (
                    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                      <h2 className="text-xl font-semibold">Company Overview</h2>
                      <p className="mt-4 leading-7 text-slate-300">
                        {stock.summary}
                      </p>
                    </section>
                  )}

                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                    <h2 className="text-xl font-semibold">Add to Portfolio</h2>
                    <p className="mt-1 text-sm text-slate-400">
                      Enter your position details for {stock.symbol}.
                    </p>

                    <div className="mt-5 grid gap-3 md:grid-cols-3">
                      <input
                        className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
                        placeholder="Quantity"
                        type="number"
                        min="0"
                        step="any"
                        value={quantity}
                        onChange={(event) => setQuantity(event.target.value)}
                      />

                      <input
                        className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
                        placeholder="Average Price"
                        type="number"
                        min="0"
                        step="any"
                        value={averagePrice}
                        onChange={(event) =>
                          setAveragePrice(event.target.value)
                        }
                      />

                      <button
                        type="button"
                        onClick={addToPortfolio}
                        disabled={adding}
                        className="rounded-xl bg-green-600 px-4 py-3 font-semibold transition hover:bg-green-500 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {adding ? "Adding..." : "Add to Portfolio"}
                      </button>
                    </div>

                    {message && (
                      <p className="mt-4 text-sm text-slate-400">{message}</p>
                    )}
                  </section>
                </>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function InsightList({
  title,
  items,
  emptyText = "No strong signal available.",
}: {
  title?: string;
  items: string[];
  emptyText?: string;
}) {
  return (
    <div>
      {title && <h3 className="font-semibold">{title}</h3>}
      <div className="mt-3 space-y-2">
        {items.length > 0 ? (
          items.map((item, index) => (
            <p key={`${item}-${index}`} className="text-sm leading-6 text-slate-300">
              • {item}
            </p>
          ))
        ) : (
          <p className="text-sm text-slate-500">{emptyText}</p>
        )}
      </div>
    </div>
  );
}
