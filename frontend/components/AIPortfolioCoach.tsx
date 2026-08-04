"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type CoachItem = {
  severity:
    | "high"
    | "medium"
    | "low"
    | "positive";
  category: string;
  title: string;
  message: string;
  suggested_action: string;
  symbol?: string | null;
};

type CoachResponse = {
  generated_at: string;
  greeting: string;
  portfolio_status: string;
  health_score: number;
  health_rating: string;
  headline: string;
  priorities: CoachItem[];
  positive_highlights: CoachItem[];
  recommendations: string[];
  estimated_review_minutes: number;
  no_action_required: boolean;
  disclaimer: string;
};

function severityStyle(
  severity: CoachItem["severity"]
) {
  if (severity === "high") {
    return {
      border: "border-red-500/20",
      badge:
        "border-red-500/30 bg-red-500/10 text-red-300",
    };
  }

  if (severity === "medium") {
    return {
      border: "border-amber-500/20",
      badge:
        "border-amber-500/30 bg-amber-500/10 text-amber-300",
    };
  }

  return {
    border: "border-emerald-500/20",
    badge:
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  };
}

export default function AIPortfolioCoach() {
  const [coach, setCoach] =
    useState<CoachResponse | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadCoach() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(
        "/portfolio/coach",
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to load AI Portfolio Coach."
        );
      }

      setCoach(await response.json());
    } catch (requestError) {
      console.error(
        "AI Coach error:",
        requestError
      );

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load AI Portfolio Coach."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCoach();
  }, []);

  if (loading) {
    return (
      <section className="rounded-3xl border border-blue-500/20 bg-gradient-to-br from-slate-900 to-blue-950/30 p-6">
        <p className="text-sm text-slate-400">
          AI Coach is reviewing your portfolio...
        </p>
      </section>
    );
  }

  if (error || !coach) {
    return (
      <section className="rounded-3xl border border-red-500/20 bg-red-500/5 p-6">
        <p className="font-semibold text-red-300">
          AI Coach unavailable
        </p>

        <p className="mt-2 text-sm text-slate-400">
          {error}
        </p>

        <button
          type="button"
          onClick={loadCoach}
          className="mt-4 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500"
        >
          Try again
        </button>
      </section>
    );
  }

  return (
    <section className="overflow-hidden rounded-3xl border border-blue-500/20 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/30 shadow-2xl shadow-blue-950/20">
      <div className="p-6 lg:p-8">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">
              AI Portfolio Coach
            </p>

            <h2 className="mt-2 text-3xl font-bold text-white">
              {coach.greeting}.
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              {coach.headline}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-950/70 px-5 py-4 text-right">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Review time
            </p>

            <p className="mt-1 text-2xl font-bold text-white">
              {coach.estimated_review_minutes} min
            </p>

            <p className="mt-1 text-xs capitalize text-slate-400">
              {coach.portfolio_status}
            </p>
          </div>
        </div>

        <div className="mt-7 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <div>
            <p className="text-sm font-semibold text-white">
              Today&apos;s priorities
            </p>

            <div className="mt-3 space-y-3">
              {coach.priorities.length > 0 ? (
                coach.priorities.map(
                  (item, index) => {
                    const style =
                      severityStyle(
                        item.severity
                      );

                    return (
                      <article
                        key={`${item.title}-${index}`}
                        className={`rounded-2xl border bg-slate-950/80 p-5 ${style.border}`}
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <h3 className="font-semibold text-white">
                              {item.title}
                            </h3>

                            <p className="mt-2 text-sm leading-6 text-slate-400">
                              {item.message}
                            </p>
                          </div>

                          <span
                            className={`rounded-full border px-3 py-1 text-xs uppercase ${style.badge}`}
                          >
                            {item.severity}
                          </span>
                        </div>

                        <p className="mt-3 text-sm leading-6 text-slate-200">
                          {item.suggested_action}
                        </p>
                      </article>
                    );
                  }
                )
              ) : (
                <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
                  <p className="font-semibold text-emerald-300">
                    No urgent action required
                  </p>

                  <p className="mt-2 text-sm text-slate-400">
                    Your portfolio does not show a material issue today.
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-5">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
              <p className="text-sm font-semibold text-white">
                Today&apos;s recommendation
              </p>

              <div className="mt-4 space-y-3">
                {coach.recommendations.map(
                  (item, index) => (
                    <div
                      key={`${item}-${index}`}
                      className="flex items-start gap-3"
                    >
                      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-500/15 text-xs font-bold text-blue-300">
                        {index + 1}
                      </span>

                      <p className="text-sm leading-6 text-slate-300">
                        {item}
                      </p>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
              <p className="text-sm font-semibold text-emerald-300">
                Positive highlights
              </p>

              <div className="mt-3 space-y-3">
                {coach.positive_highlights.length >
                0 ? (
                  coach.positive_highlights
                    .slice(0, 3)
                    .map((item, index) => (
                      <p
                        key={`${item.title}-${index}`}
                        className="text-sm leading-6 text-slate-300"
                      >
                        • {item.message}
                      </p>
                    ))
                ) : (
                  <p className="text-sm text-slate-400">
                    Positive highlights will appear as more thesis and portfolio data becomes available.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        <p className="mt-6 border-t border-slate-800 pt-5 text-xs leading-5 text-slate-500">
          {coach.disclaimer}
        </p>
      </div>
    </section>
  );
}
