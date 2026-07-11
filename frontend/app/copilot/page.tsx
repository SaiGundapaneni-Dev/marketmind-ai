"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type Intent =
  | "portfolio"
  | "stock"
  | "news"
  | "ipo"
  | "general";

type NewsItem = {
  title?: string;
  publisher?: string;
  link?: string;
  published_at?: string;
  sentiment?: "positive" | "negative" | "neutral" | string;
};

type Holding = {
  id?: number;
  symbol: string;
  name: string;
  quantity: number;
  current_value: number;
  profit: number;
};

type CopilotResponse = {
  question: string;
  intent: Intent;
  answer: string;
  status: string;

  data?: {
    summary?: {
      total_value?: number;
      total_profit?: number;
      total_return_percent?: number;
    };

    holdings?: Holding[];

    symbol?: string;
    company_name?: string;
    current_price?: number;
    currency?: string;

    marketmind_score?: {
      score?: number;
      rating?: string;
    };

    news?: NewsItem[];

    ipo?: {
      company_name?: string;
      status?: string;
      analysis?: {
        recommendation?: string;
        confidence?: number;
        warnings?: string[];
      };
    };

    sec?: {
      count?: number;
    };
  };
};

const EXAMPLE_PROMPTS = [
  "Summarize my portfolio",
  "Analyze Microsoft stock",
  "Show me the latest news about Nvidia",
  "Analyze the IPO for Stripe",
];

function formatMoney(value?: number) {
  if (typeof value !== "number") {
    return "N/A";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatDate(value?: string) {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function CopilotPage() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] =
    useState<CopilotResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canSubmit =
    question.trim().length > 0 && !loading;

  async function askCopilot(event: React.FormEvent) {
    event.preventDefault();

    const cleanQuestion = question.trim();

    if (!cleanQuestion || loading) {
      return;
    }

    setLoading(true);
    setResponse(null);
    setError("");

    try {
	  const apiBaseUrl =
		process.env.NEXT_PUBLIC_API_BASE_URL ??
		"http://127.0.0.1:8000";

	  const res = await fetch(
		`${apiBaseUrl}/copilot/ask`,
		{
		  method: "POST",
		  headers: {
			"Content-Type": "application/json",
		  },
		  body: JSON.stringify({
			question: cleanQuestion,
		  }),
		}
	  );

      if (!res.ok) {
        let message = "Copilot request failed.";

        try {
          const errorData = await res.json();

          if (typeof errorData?.detail === "string") {
            message = errorData.detail;
          }
        } catch {
          // Keep fallback message.
        }

        throw new Error(message);
      }

      const data: CopilotResponse = await res.json();

      setResponse(data);
    } catch (requestError) {
      console.error("Copilot error:", requestError);

      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError(
          "Unable to connect to the MarketMind Copilot API."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function selectPrompt(prompt: string) {
    if (loading) {
      return;
    }

    setQuestion(prompt);
    setError("");
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-medium text-blue-400">
            AI Copilot
          </p>

          <h1 className="mt-1 text-3xl font-bold">
            MarketMind Copilot
          </h1>

          <p className="mt-2 text-slate-400">
            Ask questions about your portfolio, stocks,
            market news, and IPO research.
          </p>

          <div className="mt-6">
            <p className="mb-3 text-sm text-slate-400">
              Try an example:
            </p>

            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  disabled={loading}
                  onClick={() => selectPrompt(prompt)}
                  className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <form
            onSubmit={askCopilot}
            className="mt-6 space-y-4"
          >
            <textarea
              className="min-h-32 w-full resize-y rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none transition focus:border-blue-500"
              placeholder="Example: Show me the latest news about Nvidia"
              value={question}
              disabled={loading}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
            />

            <button
              type="submit"
              disabled={!canSubmit}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "MarketMind is analyzing..."
                : "Ask Copilot"}
            </button>
          </form>

          {loading && (
            <div className="mt-6 rounded-xl border border-blue-500/20 bg-blue-500/10 p-4 text-blue-200">
              Analyzing your question and gathering the
              relevant MarketMind data...
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
              {error}
            </div>
          )}

          {response && (
            <div className="mt-8 space-y-6">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="text-sm text-blue-400">
                    Intent: {response.intent.toUpperCase()}
                  </p>

                  <StatusBadge status={response.status} />
                </div>

                <h2 className="mt-3 text-xl font-semibold">
                  Answer
                </h2>

                <p className="mt-3 leading-7 text-slate-300">
                  {response.answer}
                </p>
              </div>

              {response.intent === "portfolio" &&
                response.data?.summary && (
                  <div className="grid gap-4 md:grid-cols-3">
                    <InfoCard
                      title="Total Value"
                      value={formatMoney(
                        response.data.summary.total_value
                      )}
                    />

                    <InfoCard
                      title="Total Profit"
                      value={formatMoney(
                        response.data.summary.total_profit
                      )}
                    />

                    <InfoCard
                      title="Total Return"
                      value={`${
                        response.data.summary
                          .total_return_percent ?? 0
                      }%`}
                    />
                  </div>
                )}

              {response.intent === "stock" &&
                response.data && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                    <div>
                      <p className="text-sm text-slate-400">
                        Stock Research
                      </p>

                      <h2 className="mt-1 text-xl font-semibold">
                        {response.data.company_name ||
                          response.data.symbol ||
                          "Stock"}
                      </h2>
                    </div>

                    <div className="mt-5 grid gap-4 md:grid-cols-3">
                      <InfoCard
                        title="Price"
                        value={`${
                          response.data.currency || "USD"
                        } ${
                          response.data.current_price ??
                          "N/A"
                        }`}
                      />

                      <InfoCard
                        title="MarketMind Score"
                        value={`${
                          response.data.marketmind_score
                            ?.score ?? "N/A"
                        }/100`}
                      />

                      <InfoCard
                        title="Rating"
                        value={
                          response.data.marketmind_score
                            ?.rating || "N/A"
                        }
                      />
                    </div>
                  </div>
                )}

              {response.intent === "news" &&
                response.data?.news &&
                response.data.news.length > 0 && (
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold">
                      Relevant News
                    </h2>

                    {response.data.news.map(
                      (item, index) => (
                        <div
                          key={`${item.title}-${index}`}
                          className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <h3 className="font-semibold leading-6">
                                {item.title || "Untitled"}
                              </h3>

                              <p className="mt-1 text-sm text-slate-400">
                                {item.publisher ||
                                  "Unknown Publisher"}
                              </p>

                              {item.published_at && (
                                <p className="mt-1 text-xs text-slate-500">
                                  {formatDate(
                                    item.published_at
                                  )}
                                </p>
                              )}
                            </div>

                            <SentimentBadge
                              sentiment={
                                item.sentiment || "neutral"
                              }
                            />
                          </div>

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
                      )
                    )}
                  </div>
                )}

              {response.intent === "ipo" &&
                response.data?.ipo && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                    <p className="text-sm text-slate-400">
                      IPO Research
                    </p>

                    <h2 className="mt-1 text-xl font-semibold">
                      {response.data.ipo.company_name ||
                        "IPO Company"}
                    </h2>

                    <div className="mt-5 grid gap-4 md:grid-cols-3">
                      <InfoCard
                        title="Status"
                        value={
                          response.data.ipo.status || "N/A"
                        }
                      />

                      <InfoCard
                        title="Recommendation"
                        value={
                          response.data.ipo.analysis
                            ?.recommendation || "N/A"
                        }
                      />

                      <InfoCard
                        title="SEC Matches"
                        value={`${response.data.sec?.count ?? 0}`}
                      />
                    </div>

                    {response.data.ipo.analysis
                      ?.warnings &&
                      response.data.ipo.analysis.warnings
                        .length > 0 && (
                        <div className="mt-5 rounded-xl border border-yellow-500/20 bg-yellow-500/10 p-4">
                          <p className="font-semibold text-yellow-300">
                            Warnings
                          </p>

                          <div className="mt-2 space-y-2">
                            {response.data.ipo.analysis.warnings.map(
                              (warning, index) => (
                                <p
                                  key={`${warning}-${index}`}
                                  className="text-sm text-yellow-100"
                                >
                                  • {warning}
                                </p>
                              )
                            )}
                          </div>
                        </div>
                      )}
                  </div>
                )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function InfoCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-1 text-xl font-bold">
        {value}
      </p>
    </div>
  );
}

function StatusBadge({
  status,
}: {
  status: string;
}) {
  const normalizedStatus =
    status?.toLowerCase() || "unknown";

  return (
    <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium uppercase text-slate-300">
      {normalizedStatus}
    </span>
  );
}

function SentimentBadge({
  sentiment,
}: {
  sentiment: string;
}) {
  const normalizedSentiment =
    sentiment.toLowerCase();

  let className =
    "border-slate-700 bg-slate-800 text-slate-300";

  if (normalizedSentiment === "positive") {
    className =
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (normalizedSentiment === "negative") {
    className =
      "border-red-500/30 bg-red-500/10 text-red-300";
  }

  return (
    <span
      className={`rounded-full border px-3 py-1 text-xs font-medium ${className}`}
    >
      {normalizedSentiment.toUpperCase()}
    </span>
  );
}