"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type NewsItem = {
  title?: string;
  publisher?: string;
  link?: string;
  published_at?: string;
  publishedAt?: string;
  published?: string;
  date?: string;
  datetime?: string;
  summary?: string;
  sentiment: "positive" | "negative" | "neutral";
};

type NewsResponse = {
  symbol: string;
  count: number;
  news: NewsItem[];
  error?: string;
};

function formatNewsDate(value?: string) {
  if (!value) return "Timestamp unavailable";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Timestamp unavailable";
  }

  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function NewsPage() {
  const [symbol, setSymbol] = useState("");
  const [data, setData] = useState<NewsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function searchNews(event: React.FormEvent) {
    event.preventDefault();

    setLoading(true);
    setData(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/news/search/${symbol}`
      );

      const result = await response.json();
      setData(result);
    } catch {
      setData({
        symbol,
        count: 0,
        news: [],
        error: "Unable to connect to MarketMind API.",
      });
    } finally {
      setLoading(false);
    }
  }

  function sentimentStyle(sentiment: string) {
    if (sentiment === "positive") return "text-green-400 border-green-500/30";
    if (sentiment === "negative") return "text-red-400 border-red-500/30";
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
            Search stock news and view basic sentiment labels.
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

          {data?.error && <p className="mt-6 text-red-400">{data.error}</p>}

          {data && !data.error && (
            <div className="mt-8 space-y-4">
              <h2 className="text-xl font-semibold">
                {data.symbol} News ({data.count})
              </h2>

              {data.news.length === 0 ? (
                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                  <p className="font-semibold text-white">
                    No relevant news found.
                  </p>
                  <p className="mt-1 text-sm text-slate-400">
                    We could not find strong news results for this stock right
                    now. Try again later or search another ticker.
                  </p>
                </div>
              ) : (
                data.news.map((item, index) => (
                  <div
                    key={`${item.title}-${index}`}
                    className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold">
                          {item.title || "Untitled"}
                        </h3>

                        <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-slate-400">
                          <span>{item.publisher || "Unknown Publisher"}</span>
                          <span>•</span>
                          <span>
                            {formatNewsDate(
                              item.published_at ||
                                item.publishedAt ||
                                item.published ||
                                item.date ||
                                item.datetime
                            )}
                          </span>
                        </div>
                      </div>

                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${sentimentStyle(
                          item.sentiment
                        )}`}
                      >
                        {item.sentiment.toUpperCase()}
                      </span>
                    </div>

                    {item.summary && (
                      <p className="mt-4 text-slate-300">{item.summary}</p>
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
                ))
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}