"use client";

import ScoreProgressBar from "@/components/ScoreProgressBar";
import type { PortfolioScoreResponse } from "@/types/portfolio-score";

type PortfolioScoreHeroProps = {
  score: PortfolioScoreResponse;
};

function getScoreRingClass(score: number) {
  if (score >= 85) {
    return "from-emerald-400 to-cyan-400";
  }

  if (score >= 70) {
    return "from-blue-400 to-cyan-400";
  }

  if (score >= 50) {
    return "from-amber-400 to-orange-400";
  }

  return "from-red-400 to-rose-500";
}

function formatLabel(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function PortfolioScoreHero({
  score,
}: PortfolioScoreHeroProps) {
  const scoreItems = [
    ["Diversification", score.scores.diversification],
    ["Concentration", score.scores.concentration],
    ["Performance", score.scores.performance],
    ["Portfolio Health", score.scores.portfolio_health],
    ["Market Exposure", score.scores.market_exposure],
  ] as const;

  return (
    <section className="overflow-hidden rounded-3xl border border-blue-500/20 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 shadow-2xl shadow-blue-950/20">
      <div className="grid gap-8 p-6 lg:grid-cols-[0.8fr_1.2fr] lg:p-8">
        <div className="flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">
                Vestora Portfolio Score
              </p>

              <span className="rounded-full border border-blue-400/20 bg-blue-400/10 px-3 py-1 text-xs font-semibold capitalize text-blue-200">
                {score.rating}
              </span>
            </div>

            <div className="mt-7 flex items-center gap-6">
              <div
                className={`rounded-full bg-gradient-to-br p-[3px] ${getScoreRingClass(
                  score.overall_score
                )}`}
              >
                <div className="flex h-36 w-36 flex-col items-center justify-center rounded-full bg-slate-950">
                  <span className="text-5xl font-black tracking-tight text-white">
                    {score.overall_score.toFixed(0)}
                  </span>

                  <span className="mt-1 text-sm text-slate-400">
                    out of 100
                  </span>
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-400">
                  Overall rating
                </p>

                <p className="mt-1 text-3xl font-bold capitalize text-white">
                  {score.rating}
                </p>

                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-400">
                  {score.summary}
                </p>
              </div>
            </div>
          </div>

          <p className="mt-6 text-xs leading-5 text-slate-500">
            {score.disclaimer}
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {scoreItems.map(([label, item]) => (
            <ScoreProgressBar
              key={label}
              label={label}
              score={item.score}
              rating={item.rating}
            />
          ))}
        </div>
      </div>

      <div className="grid border-t border-slate-800 bg-slate-950/40 md:grid-cols-3">
        <ScoreList
          title="Top strengths"
          items={score.strengths}
          emptyText="Strengths will appear as your portfolio develops."
          tone="positive"
        />

        <ScoreList
          title="Needs improvement"
          items={score.weaknesses}
          emptyText="No major weaknesses detected."
          tone="warning"
        />

        <ScoreList
          title="Recommended actions"
          items={score.improvement_suggestions}
          emptyText="No immediate action is required."
          tone="action"
        />
      </div>
    </section>
  );
}

function ScoreList({
  title,
  items,
  emptyText,
  tone,
}: {
  title: string;
  items: string[];
  emptyText: string;
  tone: "positive" | "warning" | "action";
}) {
  const marker =
    tone === "positive"
      ? "✓"
      : tone === "warning"
        ? "!"
        : "→";

  const markerClass =
    tone === "positive"
      ? "bg-emerald-500/15 text-emerald-300"
      : tone === "warning"
        ? "bg-amber-500/15 text-amber-300"
        : "bg-blue-500/15 text-blue-300";

  return (
    <div className="border-slate-800 p-6 md:border-r last:border-r-0">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
        {formatLabel(title)}
      </h3>

      <div className="mt-4 space-y-3">
        {(items.length > 0 ? items.slice(0, 3) : [emptyText]).map(
          (item, index) => (
            <div
              key={`${title}-${index}`}
              className="flex items-start gap-3"
            >
              <span
                className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${markerClass}`}
              >
                {marker}
              </span>

              <p className="text-sm leading-6 text-slate-300">
                {item}
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
