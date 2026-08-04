type PriorityInsight = {
  priority: number;
  category: string;
  severity: string;
  title: string;
  message: string;
  evidence: string[];
  suggested_action: string;
  affected_symbols: string[];
};

type PortfolioIntelligence = {
  portfolio_status: string;
  executive_summary: string;
  priority_insights: PriorityInsight[];
  strengths: string[];
  risks: string[];
  opportunities: string[];
  holdings_to_watch: unknown[];
  recent_changes: string[];
  recommended_questions: string[];
  disclaimer: string;
};

function getMemo(
  intelligence: PortfolioIntelligence | null,
  healthScore: number
) {
  const topPriority = intelligence?.priority_insights?.[0];

  if (topPriority?.severity?.toLowerCase() === "high") {
    return {
      action: "Review",
      tone: "border-red-500/30 bg-red-500/10 text-red-300",
      headline: "A material portfolio issue needs attention.",
      reasons: [
        topPriority.message,
        topPriority.suggested_action,
      ],
    };
  }

  if (topPriority || healthScore < 70) {
    return {
      action: "Monitor",
      tone: "border-amber-500/30 bg-amber-500/10 text-amber-300",
      headline:
        "No immediate trade is suggested, but review is warranted.",
      reasons: [
        topPriority?.message ||
          "Portfolio health is below the preferred range.",
        topPriority?.suggested_action ||
          "Review diversification, concentration, and losing positions.",
      ],
    };
  }

  return {
    action: "Hold",
    tone:
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
    headline: "Nothing material requires action today.",
    reasons: [
      "Portfolio health remains within an acceptable range.",
      "Avoid reacting to ordinary daily volatility.",
    ],
  };
}

export default function ActionMemo({
  intelligence,
  healthScore,
  healthRating,
}: {
  intelligence: PortfolioIntelligence | null;
  healthScore: number;
  healthRating: string;
}) {
  const memo = getMemo(intelligence, healthScore);
  const changes = intelligence?.recent_changes ?? [];

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
        Action Memo
      </p>

      <div className="mt-5 flex flex-wrap items-center gap-4">
        <span
          className={`rounded-full border px-4 py-2 text-lg font-bold uppercase ${memo.tone}`}
        >
          {memo.action}
        </span>

        <div>
          <p className="text-sm text-slate-500">Portfolio health</p>
          <p className="font-semibold capitalize text-white">
            {healthScore.toFixed(0)}/100 · {healthRating}
          </p>
        </div>
      </div>

      <h2 className="mt-6 text-xl font-bold leading-8 text-white">
        {memo.headline}
      </h2>

      <div className="mt-5 space-y-3">
        {memo.reasons.map((reason, index) => (
          <div
            key={`${reason}-${index}`}
            className="flex items-start gap-3"
          >
            <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-500/15 text-xs font-bold text-blue-300">
              {index + 1}
            </span>

            <p className="text-sm leading-6 text-slate-300">
              {reason}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-6 border-t border-slate-800 pt-5">
        <p className="text-sm font-semibold text-slate-200">
          Recent changes
        </p>

        {changes.length > 0 ? (
          <div className="mt-3 space-y-2">
            {changes.slice(0, 3).map((change, index) => (
              <p
                key={`${change}-${index}`}
                className="text-sm leading-6 text-slate-400"
              >
                • {change}
              </p>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm leading-6 text-slate-500">
            No meaningful snapshot changes are available yet.
          </p>
        )}
      </div>
    </section>
  );
}
