"use client";
import { apiFetch } from "@/lib/api";
import { useEffect, useRef, useState } from "react";
import Sidebar from "@/components/Sidebar";

type Intent = "portfolio" | "stock" | "news" | "ipo" | "general";

type NewsItem = {
  title?: string;
  publisher?: string;
  link?: string;
  published_at?: string;
  sentiment?: "positive" | "negative" | "neutral" | string;
};

type CopilotResponse = {
  question: string;
  intent: Intent;
  portfolio_question_type?: string;
  answer: string | null;
  status: string;
  data?: {
    summary?: {
      total_value?: number;
      total_profit?: number;
      total_return_percent?: number;
    };
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

type ConversationItem = {
  id: string;
  question: string;
  response: CopilotResponse;
  createdAt: string;
};

const STORAGE_KEY = "vestora-copilot-history-v1";
const MAX_HISTORY_ITEMS = 30;

const EXAMPLE_PROMPTS = [
  "Analyze my portfolio",
  "What are the strengths of my portfolio?",
  "What is my biggest portfolio risk?",
  "How can I improve my portfolio?",
  "Is my portfolio diversified?",
  "Is my portfolio healthy?",
  "Analyze Microsoft stock",
  "Show me the latest news about Nvidia",
  "Analyze the IPO for Stripe",
];

function formatMoney(value?: number) {
  if (typeof value !== "number") return "N/A";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatDate(value?: string) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatConversationTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function isConversationItem(value: unknown): value is ConversationItem {
  if (!value || typeof value !== "object") return false;

  const item = value as Partial<ConversationItem>;

  return (
    typeof item.id === "string" &&
    typeof item.question === "string" &&
    typeof item.createdAt === "string" &&
    !!item.response &&
    typeof item.response === "object" &&
    typeof item.response.intent === "string" &&
    typeof item.response.status === "string"
  );
}

function loadSavedHistory(): ConversationItem[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];

    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed.filter(isConversationItem).slice(-MAX_HISTORY_ITEMS);
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return [];
  }
}

export default function CopilotPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ConversationItem[]>([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState("");
  const [error, setError] = useState("");

  const conversationEndRef = useRef<HTMLDivElement | null>(null);

  const canSubmit = question.trim().length > 0 && !loading;
  
  useEffect(() => {
    setHistory(loadSavedHistory());
    setHistoryLoaded(true);
  }, []);

  useEffect(() => {
    if (!historyLoaded) return;

    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(history.slice(-MAX_HISTORY_ITEMS))
      );
    } catch (storageError) {
      console.error("Unable to save Copilot history:", storageError);
    }
  }, [history, historyLoaded]);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [history, loading]);

  async function askCopilot(event: React.FormEvent) {
    event.preventDefault();

    const cleanQuestion = question.trim();
    if (!cleanQuestion || loading) return;

    setLoading(true);
    setPendingQuestion(cleanQuestion);
    setError("");
    setQuestion("");

    try {
	  const res = await apiFetch("/copilot/ask", {
	  method: "POST",
	  body: JSON.stringify({
		question: cleanQuestion,
	  }),
	});

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

      const item: ConversationItem = {
        id: crypto.randomUUID(),
        question: cleanQuestion,
        response: data,
        createdAt: new Date().toISOString(),
      };

      setHistory((current) =>
        [...current, item].slice(-MAX_HISTORY_ITEMS)
      );
    } catch (requestError) {
      console.error("Copilot error:", requestError);
      setQuestion(cleanQuestion);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the MarketMind Copilot API."
      );
    } finally {
      setLoading(false);
      setPendingQuestion("");
    }
  }

  function selectPrompt(prompt: string) {
    if (loading) return;
    setQuestion(prompt);
    setError("");
  }

  function clearHistory() {
    if (loading) return;

    setHistory([]);
    setError("");
    setQuestion("");
    window.localStorage.removeItem(STORAGE_KEY);
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-blue-400">AI Copilot</p>
              <h1 className="mt-1 text-3xl font-bold">Vestora Copilot</h1>
              <p className="mt-2 text-slate-400">
                Ask questions about your portfolio, stocks, market news, and
                IPO research.
              </p>
            </div>

            {history.length > 0 && (
              <button
                type="button"
                disabled={loading}
                onClick={clearHistory}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 transition hover:border-red-500 hover:text-red-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Clear conversation
              </button>
            )}
          </div>

          <div className="mt-6">
            <p className="mb-3 text-sm text-slate-400">Try an example:</p>

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

          <section className="mt-8 space-y-8">
            {historyLoaded && history.length === 0 && !loading && (
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/50 p-8 text-center">
                <h2 className="text-lg font-semibold">Start a conversation</h2>
                <p className="mt-2 text-sm text-slate-400">
                  Ask Vestora to analyze your portfolio, research a stock,
                  summarize news, or review an IPO.
                </p>
              </div>
            )}

            {history.map((item) => (
              <ConversationMessage key={item.id} item={item} />
            ))}

            {loading && (
              <div className="space-y-4">
                <div className="ml-auto max-w-3xl rounded-2xl rounded-br-md border border-blue-500/20 bg-blue-600/10 p-5">
                  <p className="text-xs font-medium uppercase tracking-wide text-blue-300">
                    You
                  </p>
                  <p className="mt-2 text-slate-100">{pendingQuestion}</p>
                </div>

                <div className="max-w-3xl rounded-2xl rounded-bl-md border border-slate-800 bg-slate-900 p-5">
                  <p className="text-xs font-medium uppercase tracking-wide text-blue-400">
                    MarketMind
                  </p>
                  <p className="mt-2 text-slate-300">
                    Analyzing your question and gathering the relevant
                    MarketMind data...
                  </p>
                  <div className="mt-4 flex gap-2">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-blue-400" />
                    <span className="h-2 w-2 animate-pulse rounded-full bg-blue-400 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-pulse rounded-full bg-blue-400 [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}

            <div ref={conversationEndRef} />
          </section>

          {error && (
            <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
              {error}
            </div>
          )}

          <form
            onSubmit={askCopilot}
            className="sticky bottom-0 mt-8 rounded-2xl border border-slate-800 bg-slate-950/95 p-4 shadow-2xl backdrop-blur"
          >
            <textarea
              className="min-h-28 w-full resize-y rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none transition focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              placeholder="Ask a follow-up question..."
              value={question}
              disabled={loading}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  if (canSubmit) event.currentTarget.form?.requestSubmit();
                }
              }}
            />

            <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
              <p className="text-xs text-slate-500">
                Press Enter to send. Use Shift + Enter for a new line.
              </p>

              <button
                type="submit"
                disabled={!canSubmit}
                className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "MarketMind is analyzing..." : "Ask Copilot"}
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>
  );
}

function ConversationMessage({ item }: { item: ConversationItem }) {
  const response = item.response;

  return (
    <article className="space-y-4">
      <div className="ml-auto max-w-3xl rounded-2xl rounded-br-md border border-blue-500/20 bg-blue-600/10 p-5">
        <div className="flex items-center justify-between gap-4">
          <p className="text-xs font-medium uppercase tracking-wide text-blue-300">
            You
          </p>
          <p className="text-xs text-slate-500">
            {formatConversationTime(item.createdAt)}
          </p>
        </div>
        <p className="mt-2 leading-7 text-slate-100">{item.question}</p>
      </div>

      <div className="max-w-4xl space-y-5 rounded-2xl rounded-bl-md border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-blue-400">
              MarketMind
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs uppercase text-slate-300">
                {response.intent}
              </span>
              {response.portfolio_question_type && (
                <span className="rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs uppercase text-blue-300">
                  {response.portfolio_question_type}
                </span>
              )}
            </div>
          </div>

          <StatusBadge status={response.status} />
        </div>

        <p className="leading-7 text-slate-300">
          {response.answer ??
            "MarketMind could not generate an answer for this request."}
        </p>

        <ResponseDetails response={response} />
      </div>
    </article>
  );
}

function ResponseDetails({ response }: { response: CopilotResponse }) {
  return (
    <div className="space-y-5">
      {response.intent === "portfolio" && response.data?.summary && (
        <div className="grid gap-4 md:grid-cols-3">
          <InfoCard
            title="Total Value"
            value={formatMoney(response.data.summary.total_value)}
          />
          <InfoCard
            title="Total Profit"
            value={formatMoney(response.data.summary.total_profit)}
          />
          <InfoCard
            title="Total Return"
            value={`${response.data.summary.total_return_percent ?? 0}%`}
          />
        </div>
      )}

      {response.intent === "stock" && response.data && (
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-400">Stock Research</p>
          <h3 className="mt-1 text-xl font-semibold">
            {response.data.company_name || response.data.symbol || "Stock"}
          </h3>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <InfoCard
              title="Price"
              value={`${response.data.currency || "USD"} ${
                response.data.current_price ?? "N/A"
              }`}
            />
            <InfoCard
              title="MarketMind Score"
              value={`${response.data.marketmind_score?.score ?? "N/A"}/100`}
            />
            <InfoCard
              title="Rating"
              value={response.data.marketmind_score?.rating || "N/A"}
            />
          </div>
        </div>
      )}

      {response.intent === "news" &&
        response.data?.news &&
        response.data.news.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Relevant News</h3>

            {response.data.news.map((item, index) => (
              <div
                key={`${item.title}-${index}`}
                className="rounded-xl border border-slate-800 bg-slate-950 p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="font-semibold leading-6">
                      {item.title || "Untitled"}
                    </h4>
                    <p className="mt-1 text-sm text-slate-400">
                      {item.publisher || "Unknown Publisher"}
                    </p>
                    {item.published_at && (
                      <p className="mt-1 text-xs text-slate-500">
                        {formatDate(item.published_at)}
                      </p>
                    )}
                  </div>

                  <SentimentBadge sentiment={item.sentiment || "neutral"} />
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
            ))}
          </div>
        )}

      {response.intent === "ipo" && response.data?.ipo && (
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-400">IPO Research</p>
          <h3 className="mt-1 text-xl font-semibold">
            {response.data.ipo.company_name || "IPO Company"}
          </h3>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <InfoCard
              title="Status"
              value={response.data.ipo.status || "N/A"}
            />
            <InfoCard
              title="Recommendation"
              value={response.data.ipo.analysis?.recommendation || "N/A"}
            />
            <InfoCard
              title="SEC Matches"
              value={`${response.data.sec?.count ?? 0}`}
            />
          </div>

          {response.data.ipo.analysis?.warnings &&
            response.data.ipo.analysis.warnings.length > 0 && (
              <div className="mt-5 rounded-xl border border-yellow-500/20 bg-yellow-500/10 p-4">
                <p className="font-semibold text-yellow-300">Warnings</p>
                <div className="mt-2 space-y-2">
                  {response.data.ipo.analysis.warnings.map((warning, index) => (
                    <p
                      key={`${warning}-${index}`}
                      className="text-sm text-yellow-100"
                    >
                      • {warning}
                    </p>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
}

function InfoCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-1 text-xl font-bold">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status?.toLowerCase() || "unknown";

  let className =
    "border-slate-700 bg-slate-950 text-slate-300";

  if (normalized === "success") {
    className =
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  } else if (normalized === "error" || normalized === "not_found") {
    className = "border-red-500/30 bg-red-500/10 text-red-300";
  } else if (normalized === "needs_more_info") {
    className =
      "border-yellow-500/30 bg-yellow-500/10 text-yellow-300";
  }

  return (
    <span
      className={`rounded-full border px-3 py-1 text-xs font-medium uppercase ${className}`}
    >
      {normalized.replaceAll("_", " ")}
    </span>
  );
}

function SentimentBadge({ sentiment }: { sentiment: string }) {
  const normalized = sentiment.toLowerCase();

  let className =
    "border-slate-700 bg-slate-800 text-slate-300";

  if (normalized === "positive") {
    className =
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  } else if (normalized === "negative") {
    className = "border-red-500/30 bg-red-500/10 text-red-300";
  }

  return (
    <span
      className={`rounded-full border px-3 py-1 text-xs font-medium ${className}`}
    >
      {normalized.toUpperCase()}
    </span>
  );
}
