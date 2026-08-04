"use client";

import { useState } from "react";
import type {
  PortfolioScoreCategory,
  PortfolioScoreResponse,
} from "@/types/portfolio-score";

type PortfolioScoreBreakdownProps = {
  score: PortfolioScoreResponse;
};

const categories = [
  ["diversification", "Diversification"],
  ["concentration", "Concentration"],
  ["performance", "Performance"],
  ["portfolio_health", "Portfolio Health"],
  ["market_exposure", "Market Exposure"],
] as const;

export default function PortfolioScoreBreakdown({
  score,
}: PortfolioScoreBreakdownProps) {
  const [selected, setSelected] =
    useState<(typeof categories)[number][0]>(
      "diversification"
    );

  const details = score.scores[selected];

  return (
    <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div>
        <p className="text-sm font-medium text-blue-400">
          Explainable scoring
        </p>

        <h2 className="mt-1 text-xl font-semibold">
          Portfolio Score Breakdown
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Select a category to understand the score and its recommended action.
        </p>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {categories.map(([key, label]) => {
          const category = score.scores[key];
          const isActive = selected === key;

          return (
            <button
              key={key}
              onClick={() => setSelected(key)}
              className={`rounded-xl border px-4 py-3 text-left transition ${
                isActive
                  ? "border-blue-500 bg-blue-500/10 text-white"
                  : "border-slate-700 bg-slate-950 text-slate-400 hover:border-slate-600 hover:text-white"
              }`}
            >
              <span className="block text-sm font-medium">
                {label}
              </span>

              <span className="mt-1 block text-xs">
                {category.score.toFixed(0)}/100
              </span>
            </button>
          );
        })}
      </div>

      <CategoryDetails details={details} />
    </section>
  );
}

function CategoryDetails({
  details,
}: {
  details: PortfolioScoreCategory;
}) {
  return (
    <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_0.9fr]">
      <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-400">
              Category score
            </p>

            <p className="mt-1 text-3xl font-bold">
              {details.score.toFixed(0)}
              <span className="text-base font-normal text-slate-500">
                /100
              </span>
            </p>
          </div>

          <span className="rounded-full border border-slate-700 px-3 py-1 text-sm capitalize text-slate-300">
            {details.rating}
          </span>
        </div>

        <p className="mt-5 text-sm leading-6 text-slate-300">
          {details.summary}
        </p>

        <div className="mt-5">
          <p className="text-sm font-semibold text-white">
            Score factors
          </p>

          <ul className="mt-3 space-y-2">
            {details.factors.map((factor, index) => (
              <li
                key={`${factor}-${index}`}
                className="flex items-start gap-3 text-sm leading-6 text-slate-400"
              >
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                {factor}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-5">
        <p className="text-sm font-semibold uppercase tracking-wider text-blue-300">
          Suggested action
        </p>

        <p className="mt-4 text-base leading-7 text-slate-200">
          {details.suggested_action}
        </p>

        <p className="mt-5 text-xs leading-5 text-slate-500">
          Review this suggestion alongside your time horizon, goals, and risk tolerance.
        </p>
      </div>
    </div>
  );
}
