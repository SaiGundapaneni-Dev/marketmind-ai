"use client";
import { apiFetch } from "@/lib/api";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";

type WatchlistItem = {
  id: number;
  symbol: string;
  company_name?: string;
  notes?: string;
};

type IntelligenceItem = {
  id: number;
  symbol: string;
  company_name?: string;
  current_price?: number;
  currency?: string;
  marketmind_score?: number;
  marketmind_rating?: string;
  research_classification?: string;
  confidence?: number;
  news_sentiment: string;
  article_count: number;
  portfolio_owned: boolean;
  portfolio_allocation_percent: number;
  risk_level: string;
  bull_case: string[];
  bear_case: string[];
  error?: string;
};

type WatchlistSummary = {
  count: number;
  strong_candidates: number;
  positive: number;
  neutral: number;
  cautious_or_high_risk: number;
  top_opportunity?: IntelligenceItem | null;
  highest_risk?: IntelligenceItem | null;
  most_positive_news?: IntelligenceItem | null;
  most_negative_news?: IntelligenceItem | null;
  items: IntelligenceItem[];
};

function formatMoney(value?: number) {
  if (typeof value !== "number") return "N/A";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

export default function WatchlistPage() {
  const [symbol, setSymbol] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [summary, setSummary] = useState<WatchlistSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [message, setMessage] = useState("");

  async function loadItems() {
	const response = await apiFetch(
		"/watchlist/",
		{
		  cache: "no-store",
		}
	  );

    if (!response.ok) {
      throw new Error("Unable to load watchlist.");
    }

    const data: WatchlistItem[] = await response.json();
    setItems(data);
  }

  useEffect(() => {
    async function load() {
      try {
        await loadItems();
      } catch (error) {
        console.error(error);
        setMessage("Unable to load the watchlist.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

	async function addItem(
	  event: React.FormEvent
	) {
	  event.preventDefault();

	  const cleanSymbol =
		symbol.trim().toUpperCase();

	  if (!cleanSymbol) {
		return;
	  }

	  setMessage("");

	  try {
		const response = await apiFetch(
		  "/watchlist/",
		  {
			method: "POST",
			body: JSON.stringify({
			  symbol: cleanSymbol,
			  company_name:
				companyName.trim() || null,
			  notes: null,
			}),
		  }
		);

		if (response.status === 409) {
		  setMessage(
			`${cleanSymbol} is already in your watchlist.`
		  );
		  return;
		}

		if (!response.ok) {
		  setMessage(
			"Unable to add this symbol."
		  );
		  return;
		}

		setSymbol("");
		setCompanyName("");
		setSummary(null);

		setMessage(
		  `${cleanSymbol} added successfully.`
		);

		await loadItems();
	  } catch (error) {
		console.error(
		  "Add watchlist error:",
		  error
		);

		setMessage(
		  "Unable to connect to Vestora AI."
		);
	  }
	}
  async function deleteItem(item: WatchlistItem) {
    const confirmed = window.confirm(
      `Remove ${item.symbol} from your watchlist?`
    );

    if (!confirmed) return;

    const response = await apiFetch(
      `/watchlist/${item.id}`,
      { method: "DELETE" }
    );

    if (!response.ok) {
      setMessage(`Unable to remove ${item.symbol}.`);
      return;
    }

    setSummary(null);
    setMessage(`${item.symbol} removed.`);
    await loadItems();
  }

  async function analyzeWatchlist() {
    setAnalyzing(true);
    setMessage("");

    try {
      const response = await apiFetch(
        "/watchlist/analysis",
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error("Watchlist analysis failed.");
      }

      const data: WatchlistSummary = await response.json();
      setSummary(data);
    } catch (error) {
      console.error(error);
      setMessage("Unable to analyze the watchlist.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-medium text-blue-400">
            Watchlist Intelligence
          </p>

          <h1 className="mt-1 text-3xl font-bold">AI Watchlist</h1>

          <p className="mt-2 text-slate-400">
            Track research candidates and compare score, sentiment, risk,
            and portfolio exposure.
          </p>

          <form
            onSubmit={addItem}
            className="mt-8 grid gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-5 md:grid-cols-[1fr_2fr_auto]"
          >
            <input
              value={symbol}
              onChange={(event) =>
                setSymbol(event.target.value.toUpperCase())
              }
              placeholder="Symbol, e.g. NVDA"
              className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
            />

            <input
              value={companyName}
              onChange={(event) => setCompanyName(event.target.value)}
              placeholder="Company name (optional)"
              className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
            />

            <button className="rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500">
              Add
            </button>
          </form>

          {message && (
            <p className="mt-4 text-sm text-slate-300">{message}</p>
          )}

          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">Saved Symbols</h2>
                <p className="mt-1 text-sm text-slate-400">
                  {items.length} stock{items.length === 1 ? "" : "s"} saved.
                </p>
              </div>

              <button
                onClick={analyzeWatchlist}
                disabled={analyzing || items.length === 0}
                className="rounded-xl bg-emerald-600 px-5 py-3 font-semibold hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {analyzing ? "Analyzing..." : "Analyze Entire Watchlist"}
              </button>
            </div>

            {loading ? (
              <p className="mt-5 text-slate-400">Loading...</p>
            ) : items.length === 0 ? (
              <p className="mt-5 text-slate-400">
                Add your first research candidate above.
              </p>
            ) : (
              <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                  >
                    <p className="text-2xl font-bold">{item.symbol}</p>
                    <p className="mt-1 text-sm text-slate-400">
                      {item.company_name || "Company name unavailable"}
                    </p>

                    <button
                      onClick={() => deleteItem(item)}
                      className="mt-4 text-sm text-red-400 hover:text-red-300"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          {summary && (
            <>
              <section className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <SummaryCard
                  title="Strong Candidates"
                  value={summary.strong_candidates}
                />
                <SummaryCard title="Positive" value={summary.positive} />
                <SummaryCard title="Neutral" value={summary.neutral} />
                <SummaryCard
                  title="Cautious / High Risk"
                  value={summary.cautious_or_high_risk}
                />
              </section>

              <section className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <HighlightCard
                  title="Top Opportunity"
                  item={summary.top_opportunity}
                />
                <HighlightCard
                  title="Highest Risk"
                  item={summary.highest_risk}
                />
                <HighlightCard
                  title="Most Positive News"
                  item={summary.most_positive_news}
                />
                <HighlightCard
                  title="Most Negative News"
                  item={summary.most_negative_news}
                />
              </section>

              <section className="mt-8 grid gap-5 lg:grid-cols-2">
                {summary.items.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-2xl font-bold">{item.symbol}</p>
                        <p className="mt-1 text-sm text-slate-400">
                          {item.company_name}
                        </p>
                      </div>

                      <span className="rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs capitalize text-blue-300">
                        {item.research_classification || "unrated"}
                      </span>
                    </div>

                    {item.error ? (
                      <p className="mt-4 text-red-300">{item.error}</p>
                    ) : (
                      <>
                        <div className="mt-5 grid gap-3 sm:grid-cols-3">
                          <Metric
                            title="Price"
                            value={formatMoney(item.current_price)}
                          />
                          <Metric
                            title="Vestora"
                            value={`${item.marketmind_score ?? "N/A"}/100`}
                          />
                          <Metric
                            title="Confidence"
                            value={`${item.confidence ?? "N/A"}%`}
                          />
                        </div>

                        <div className="mt-5 grid gap-5 md:grid-cols-2">
                          <ListBlock
                            title="Bull Case"
                            items={item.bull_case}
                          />
                          <ListBlock
                            title="Bear Case"
                            items={item.bear_case}
                          />
                        </div>

                        <div className="mt-5 flex flex-wrap gap-2 text-xs">
                          <span className="rounded-full border border-slate-700 px-3 py-1 capitalize">
                            News: {item.news_sentiment}
                          </span>
                          <span className="rounded-full border border-slate-700 px-3 py-1 capitalize">
                            Risk: {item.risk_level}
                          </span>
                          <span className="rounded-full border border-slate-700 px-3 py-1">
                            Portfolio:{" "}
                            {item.portfolio_owned
                              ? `${item.portfolio_allocation_percent.toFixed(
                                  2
                                )}%`
                              : "Not owned"}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </section>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

function SummaryCard({
  title,
  value,
}: {
  title: string;
  value: number;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

function HighlightCard({
  title,
  item,
}: {
  title: string;
  item?: IntelligenceItem | null;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-2 text-2xl font-bold">{item?.symbol || "N/A"}</p>
      <p className="mt-1 text-sm capitalize text-slate-300">
        {item?.research_classification || item?.risk_level || "No data"}
      </p>
    </div>
  );
}

function Metric({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs text-slate-400">{title}</p>
      <p className="mt-1 font-semibold">{value}</p>
    </div>
  );
}

function ListBlock({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div>
      <h3 className="font-semibold">{title}</h3>
      <div className="mt-2 space-y-2">
        {items.length > 0 ? (
          items.map((item, index) => (
            <p
              key={`${item}-${index}`}
              className="text-sm leading-6 text-slate-400"
            >
              • {item}
            </p>
          ))
        ) : (
          <p className="text-sm text-slate-500">No data.</p>
        )}
      </div>
    </div>
  );
}
