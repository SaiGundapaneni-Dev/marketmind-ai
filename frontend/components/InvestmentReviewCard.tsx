"use client";

import { useState } from "react";

import { apiFetch } from "@/lib/api";


type InvestmentReview = {
  symbol: string;
  company_name: string;
  status:
    | "On Track"
    | "Needs Attention"
    | "Review Due"
    | "Target Reached"
    | "Insufficient Data";
  recommendation: string;
  summary: string;
  current_price: number | null;
  target_price: number | null;
  target_progress_percent: number | null;
  upside_to_target_percent: number | null;
  conviction_score: number | null;
  risk_level: string | null;
  investment_horizon: string | null;
  review_date: string | null;
  review_overdue: boolean;
  news: {
    article_count: number;
    positive: number;
    neutral: number;
    negative: number;
    overall_sentiment:
      | "positive"
      | "neutral"
      | "negative";
  };
  position: {
    quantity: number;
    average_price: number;
    current_value: number | null;
    unrealized_profit: number | null;
    unrealized_return_percent: number | null;
    allocation_percent: number | null;
  };
  signals: string[];
  risks: string[];
  disclaimer: string;
};

function money(value: number | null) {
  if (value === null) {
    return "Unavailable";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function statusClasses(
  status: InvestmentReview["status"]
) {
  if (
    status === "On Track" ||
    status === "Target Reached"
  ) {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  }

  if (
    status === "Needs Attention" ||
    status === "Review Due"
  ) {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-slate-600 bg-slate-800 text-slate-300";
}

async function readError(
  response: Response
) {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }
  } catch {
    // Keep fallback message.
  }

  return "Unable to generate the investment review.";
}

export default function InvestmentReviewCard({
  holdingId,
  symbol,
}: {
  holdingId: number;
  symbol: string;
}) {
  const [review, setReview] =
    useState<InvestmentReview | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function generateReview() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(
        `/portfolio/thesis/review/${holdingId}`
      );

      if (!response.ok) {
        setError(await readError(response));
        return;
      }

      const data: InvestmentReview =
        await response.json();

      setReview(data);
    } catch (requestError) {
      console.error(
        "Investment review error:",
        requestError
      );

      setError(
        "Unable to connect to Vestora AI."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mb-6 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">
            AI Investment Review
          </p>

          <h3 className="mt-1 text-lg font-semibold text-white">
            Review {symbol}
          </h3>
        </div>

        <button
          type="button"
          onClick={generateReview}
          disabled={loading}
          className="rounded-lg bg-cyan-500 px-4 py-2.5 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading
            ? "Reviewing..."
            : review
              ? "Refresh Review"
              : "Run AI Review"}
        </button>
      </div>

      {error && (
        <p className="mt-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {review && (
        <div className="mt-5 space-y-5">
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`rounded-full border px-3 py-1 text-sm font-medium ${statusClasses(
                review.status
              )}`}
            >
              {review.status}
            </span>

            <span className="text-sm text-slate-400">
              News: {review.news.positive} positive ·{" "}
              {review.news.neutral} neutral ·{" "}
              {review.news.negative} negative
            </span>
          </div>

          <p className="text-sm leading-6 text-slate-300">
            {review.summary}
          </p>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase text-slate-500">
                Current price
              </p>
              <p className="mt-2 font-semibold text-white">
                {money(review.current_price)}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase text-slate-500">
                Target price
              </p>
              <p className="mt-2 font-semibold text-white">
                {money(review.target_price)}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase text-slate-500">
                Target progress
              </p>
              <p className="mt-2 font-semibold text-white">
                {review.target_progress_percent !==
                null
                  ? `${review.target_progress_percent.toFixed(
                      2
                    )}%`
                  : "Unavailable"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase text-slate-500">
                Portfolio allocation
              </p>
              <p className="mt-2 font-semibold text-white">
                {review.position
                  .allocation_percent !== null
                  ? `${review.position.allocation_percent.toFixed(
                      2
                    )}%`
                  : "Unavailable"}
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-sm font-medium text-white">
              Recommendation
            </p>

            <p className="mt-2 text-sm leading-6 text-slate-300">
              {review.recommendation}
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-emerald-300">
                Supporting signals
              </p>

              <div className="mt-2 space-y-2">
                {review.signals.length > 0 ? (
                  review.signals.map(
                    (signal) => (
                      <p
                        key={signal}
                        className="text-sm text-slate-300"
                      >
                        • {signal}
                      </p>
                    )
                  )
                ) : (
                  <p className="text-sm text-slate-500">
                    No supporting signals available.
                  </p>
                )}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-amber-300">
                Risks to review
              </p>

              <div className="mt-2 space-y-2">
                {review.risks.length > 0 ? (
                  review.risks.map((risk) => (
                    <p
                      key={risk}
                      className="text-sm text-slate-300"
                    >
                      • {risk}
                    </p>
                  ))
                ) : (
                  <p className="text-sm text-slate-500">
                    No major rule-based risks were detected.
                  </p>
                )}
              </div>
            </div>
          </div>

          <p className="border-t border-slate-800 pt-4 text-xs leading-5 text-slate-500">
            {review.disclaimer}
          </p>
        </div>
      )}
    </section>
  );
}
