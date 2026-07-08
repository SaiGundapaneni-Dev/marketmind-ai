"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type NewsItem = {
  title?: string;
  publisher?: string;
  link?: string;
  published_at?: string;
  summary?: string;
  sentiment: "positive" | "negative" | "neutral";
  sentiment_confidence?: number;
  sentiment_reason?: string;
  relevance_score?: number;
};

type NewsResponse = {
  symbol: string;
  count: number;
  news: NewsItem[];
  error?: string;
};

type RecentSearch = {
  id: number;
  symbol: string;
  result_count: number;
  searched_at: string;
};

type RecentSearchResponse = {
  count: number;
  searches: RecentSearch[];
};

function formatDate(value?: string) {
  if (!value) return "Date unavailable";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function NewsPage() {
  const [symbol, setSymbol] = useState("");
  const [data, setData] = useState<NewsResponse | null>(null);
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const [loading, setLoading] = useState(false);

  async function loadRecentSearches() {
    try {
      const response = await fetch("http://127.0.0.1:8000/news/recent");
      const result: RecentSearchResponse = await response.json();
      setRecentSearches(result.searches);
    } catch {
      setRecentSearches([]);
    }
  }
  
  async function fetchNews(searchSymbol: string) {
	  const cleanSymbol = searchSymbol.trim().toUpperCase();

	  if (!cleanSymbol) {
		return;
	  }

	  setSymbol(cleanSymbol);
	  setLoading(true);
	  setData(null);

	  try {
		const response = await fetch(
		  `http://127.0.0.1:8000/news/search/${cleanSymbol}`
		);

		if (!response.ok) {
		  throw new Error("News search failed");
		}

		const result: NewsResponse = await response.json();

		setData(result);

		await loadRecentSearches();
	  } catch (error) {
		console.error("News search error:", error);

		setData({
		  symbol: cleanSymbol,
		  count: 0,
		  news: [],
		  error: "Unable to connect to MarketMind API.",
		});
	  } finally {
		setLoading(false);
	  }
	}

  async function searchNews(event: React.FormEvent) {
  event.preventDefault();

  await fetchNews(symbol);
}

  function sentimentStyle(sentiment: string) {
    if (sentiment === "positive") {
      return "text-green-400 border-green-500/30";
    }

    if (sentiment === "negative") {
      return "text-red-400 border-red-500/30";
    }

    return "text-slate-400 border-slate-700";
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-medium text-blue-400">Market News</p>

          <h1 className="mt-1 text-3xl font-bold">Stock News Search</h1>

          <p className="mt-2 text-slate-400">
            Search stock news and view relevance-filtered articles with sentiment analysis.
          </p>

          <form onSubmit={searchNews} className="mt-8 flex gap-3">
            <input
              className="w-full rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none focus:border-blue-500"
              placeholder="Enter symbol, e.g. AAPL"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              required
            />

            <button
              disabled={loading}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </form>

          {recentSearches.length > 0 && (
            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold">Recent Searches</h2>

              <div className="mt-4 flex flex-wrap gap-2">
                {recentSearches.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => fetchNews(item.symbol)}
                    className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:border-blue-500 hover:text-white"
                  >
                    {item.symbol} · {item.result_count} articles
                  </button>
                ))}
              </div>
            </div>
          )}

          {data?.error && <p className="mt-6 text-red-400">{data.error}</p>}

          {data && !data.error && (
            <div className="mt-8 space-y-4">
              <h2 className="text-xl font-semibold">
                {data.symbol} News ({data.count})
              </h2>

              <div className="grid gap-4 md:grid-cols-4">
                <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                  <p className="text-sm text-slate-400">Total Articles</p>
                  <p className="mt-1 text-2xl font-bold">{data.count}</p>
                </div>

                <div className="rounded-xl border border-green-500/20 bg-slate-900 p-4">
                  <p className="text-sm text-slate-400">Positive</p>
                  <p className="mt-1 text-2xl font-bold text-green-400">
                    {data.news.filter((item) => item.sentiment === "positive").length}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
                  <p className="text-sm text-slate-400">Neutral</p>
                  <p className="mt-1 text-2xl font-bold text-slate-300">
                    {data.news.filter((item) => item.sentiment === "neutral").length}
                  </p>
                </div>

                <div className="rounded-xl border border-red-500/20 bg-slate-900 p-4">
                  <p className="text-sm text-slate-400">Negative</p>
                  <p className="mt-1 text-2xl font-bold text-red-400">
                    {data.news.filter((item) => item.sentiment === "negative").length}
                  </p>
                </div>
              </div>

              {data.news.length === 0 && (
                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-center text-slate-400">
                  No highly relevant news found for {data.symbol}.
                </div>
              )}

              {data.news.map((item, index) => (
                <div
                  key={`${item.title}-${index}`}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="text-lg font-semibold">
                        {item.title || "Untitled"}
                      </h3>

                      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-400">
                        <span>{item.publisher || "Unknown Publisher"}</span>
                        <span className="text-slate-600">•</span>
                        <span>{formatDate(item.published_at)}</span>
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-2">
                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${sentimentStyle(
                          item.sentiment
                        )}`}
                      >
                        {item.sentiment.toUpperCase()}
                        {item.sentiment_confidence !== undefined &&
                          ` ${(item.sentiment_confidence * 100).toFixed(0)}%`}
                      </span>

                      <span className="rounded-full border border-blue-500/30 px-3 py-1 text-xs font-semibold text-blue-400">
                        Relevance {item.relevance_score ?? 0}
                      </span>
                    </div>
                  </div>

                  {item.summary && (
                    <p className="mt-4 text-slate-300">{item.summary}</p>
                  )}

                  {item.sentiment_reason && (
                    <p className="mt-3 text-sm text-slate-500">
                      Sentiment reason: {item.sentiment_reason}
                    </p>
                  )}

                  {item.link && (
                    <a
                      href={item.link}
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
        </div>
      </section>
    </main>
  );
}