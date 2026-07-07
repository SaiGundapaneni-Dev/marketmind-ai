"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

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

  error?: string;
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
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-1 text-xl font-bold">
        {displayValue}
      </p>
    </div>
  );
}

function formatMarketCap(value?: number) {
  if (!value) {
    return "N/A";
  }

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

export default function StockSearchPage() {
  const [symbol, setSymbol] = useState("");

  const [stock, setStock] =
    useState<StockData | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [quantity, setQuantity] =
    useState("");

  const [averagePrice, setAveragePrice] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [adding, setAdding] =
    useState(false);


  async function searchStock(
    event: React.FormEvent
  ) {
    event.preventDefault();

    setLoading(true);
    setStock(null);
    setMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/stocks/search/${symbol}`
      );

      if (!response.ok) {
        throw new Error(
          "Stock search request failed"
        );
      }

      const data = await response.json();

      setStock(data);

    } catch (error) {
      console.error(
        "Stock search error:",
        error
      );

      setStock({
        symbol,
        error:
          "Unable to search stock. Check the FastAPI backend connection.",
      });

    } finally {
      setLoading(false);
    }
  }


  async function addToPortfolio() {
    if (!stock || stock.error) {
      return;
    }

    if (!quantity || !averagePrice) {
      setMessage(
        "Please enter quantity and average price."
      );

      return;
    }

    if (
      Number(quantity) <= 0 ||
      Number(averagePrice) <= 0
    ) {
      setMessage(
        "Quantity and average price must be greater than zero."
      );

      return;
    }

    setAdding(true);
    setMessage("Adding to portfolio...");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/portfolio/holdings",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            asset_type: "US",
            symbol: stock.symbol,
            name:
              stock.company_name ||
              stock.symbol,
            quantity:
              Number(quantity),
            average_price:
              Number(averagePrice),
            currency: "USD",
            portfolio_id: 1,
          }),
        }
      );

      if (!response.ok) {
        setMessage(
          "Failed to add stock to portfolio."
        );

        return;
      }

      setMessage(
        `${stock.symbol} added to portfolio successfully.`
      );

      setQuantity("");
      setAveragePrice("");

    } catch (error) {
      console.error(
        "Add holding error:",
        error
      );

      setMessage(
        "Unable to connect to MarketMind API."
      );

    } finally {
      setAdding(false);
    }
  }


  return (
    <main className="flex min-h-screen bg-slate-950 text-white">

      <Sidebar />


      <section className="flex-1 px-6 py-8">

        <div className="mx-auto max-w-6xl">


          {/* Page Header */}

          <div>

            <p className="text-sm font-medium text-blue-400">
              Stock Search
            </p>

            <h1 className="mt-1 text-3xl font-bold">
              Company Research
            </h1>

            <p className="mt-2 text-slate-400">
              Search a US stock symbol,
              review company fundamentals and
              valuation metrics, and add the
              stock directly to your portfolio.
            </p>

          </div>


          {/* Search Form */}

          <form
            onSubmit={searchStock}
            className="mt-8 flex gap-3"
          >

            <input
              className="w-full rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none transition focus:border-blue-500"
              placeholder="Enter symbol, e.g. AAPL"
              value={symbol}
              onChange={(event) =>
                setSymbol(
                  event.target.value.toUpperCase()
                )
              }
              required
            />

            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >

              {loading
                ? "Searching..."
                : "Search"}

            </button>

          </form>


          {/* Search Result */}

          {stock && (

            <div className="mt-8 space-y-6">


              {stock.error ? (

                <div className="rounded-2xl border border-red-900 bg-slate-900 p-6">

                  <p className="text-red-400">
                    {stock.error}
                  </p>

                </div>

              ) : (

                <>


                  {/* Company Header */}

                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h2 className="text-2xl font-bold">

                      {stock.company_name}
                      {" "}
                      ({stock.symbol})

                    </h2>


                    <p className="mt-2 text-slate-400">

                      {stock.sector ||
                        "Sector unavailable"}

                      {" • "}

                      {stock.industry ||
                        "Industry unavailable"}

                    </p>


                    {/* Main Company Metrics */}

                    <div className="mt-6 grid gap-4 md:grid-cols-3">


                      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

                        <p className="text-sm text-slate-400">
                          Current Price
                        </p>

                        <p className="mt-1 text-xl font-bold">

                          {stock.currency ||
                            "USD"}

                          {" "}

                          {stock.current_price ??
                            "N/A"}

                        </p>

                      </div>


                      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

                        <p className="text-sm text-slate-400">
                          Market Cap
                        </p>

                        <p className="mt-1 text-xl font-bold">

                          {formatMarketCap(
                            stock.market_cap
                          )}

                        </p>

                      </div>


                      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

                        <p className="text-sm text-slate-400">
                          Website
                        </p>


                        {stock.website ? (

                          <a
                            href={stock.website}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-1 block truncate text-blue-400 hover:underline"
                          >

                            {stock.website}

                          </a>

                        ) : (

                          <p className="mt-1 text-slate-500">
                            N/A
                          </p>

                        )}

                      </div>

                    </div>

                  </div>


                  {/* Fundamental Analysis */}

                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <div>

                      <p className="text-sm font-medium text-blue-400">
                        Fundamental Analysis
                      </p>

                      <h2 className="mt-1 text-xl font-semibold">
                        Valuation & Growth Metrics
                      </h2>

                    </div>


                    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">


                      <MetricCard
                        title="P/E Ratio"
                        value={stock.pe_ratio}
                      />


                      <MetricCard
                        title="Forward P/E"
                        value={stock.forward_pe}
                      />


                      <MetricCard
                        title="EPS"
                        value={stock.eps}
                      />


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
                        title="Analyst Recommendation"
                        value={
                          stock.recommendation
                        }
                      />


                      <MetricCard
                        title="52-Week High"
                        value={
                          stock.fifty_two_week_high
                        }
                      />


                      <MetricCard
                        title="52-Week Low"
                        value={
                          stock.fifty_two_week_low
                        }
                      />


                      <MetricCard
                        title="Analyst Target Price"
                        value={
                          stock.analyst_target_price
                        }
                      />


                    </div>

                  </div>


                  {/* Company Overview */}

                  {stock.summary && (

                    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                      <h2 className="text-xl font-semibold">
                        Company Overview
                      </h2>

                      <p className="mt-4 leading-7 text-slate-300">

                        {stock.summary}

                      </p>

                    </div>

                  )}


                  {/* Add to Portfolio */}

                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h2 className="text-xl font-semibold">
                      Add to Portfolio
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">

                      Enter your position details
                      for {stock.symbol}.

                    </p>


                    <div className="mt-5 grid gap-3 md:grid-cols-3">


                      <input
                        className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
                        placeholder="Quantity"
                        type="number"
                        min="0"
                        step="any"
                        value={quantity}
                        onChange={(event) =>
                          setQuantity(
                            event.target.value
                          )
                        }
                      />


                      <input
                        className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
                        placeholder="Average Price"
                        type="number"
                        min="0"
                        step="any"
                        value={averagePrice}
                        onChange={(event) =>
                          setAveragePrice(
                            event.target.value
                          )
                        }
                      />


                      <button
                        type="button"
                        onClick={addToPortfolio}
                        disabled={adding}
                        className="rounded-xl bg-green-600 px-4 py-3 font-semibold transition hover:bg-green-500 disabled:cursor-not-allowed disabled:opacity-50"
                      >

                        {adding
                          ? "Adding..."
                          : "Add to Portfolio"}

                      </button>


                    </div>


                    {message && (

                      <p className="mt-4 text-sm text-slate-400">

                        {message}

                      </p>

                    )}


                  </div>

                </>

              )}

            </div>

          )}

        </div>

      </section>

    </main>
  );
}