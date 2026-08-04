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

type HoldingToWatch = {
  symbol: string;
  name: string;
  allocation_percent: number;
  profit: number;
  profit_percent: number;
  reason: string;
};

type PortfolioIntelligence = {
  portfolio_status: string;
  executive_summary: string;
  priority_insights: PriorityInsight[];
  strengths: string[];
  risks: string[];
  opportunities: string[];
  holdings_to_watch: HoldingToWatch[];
  recent_changes: string[];
  recommended_questions: string[];
  disclaimer: string;
};

function severityStyle(severity: string) {
  const normalized = severity.toLowerCase();

  if (normalized === "high") {
    return {
      marker: "bg-red-500/15 text-red-300",
      border: "border-red-500/20",
    };
  }

  if (normalized === "medium") {
    return {
      marker: "bg-amber-500/15 text-amber-300",
      border: "border-amber-500/20",
    };
  }

  return {
    marker: "bg-emerald-500/15 text-emerald-300",
    border: "border-emerald-500/20",
  };
}

export default function TodayIntelligence({
  intelligence,
}: {
  intelligence: PortfolioIntelligence | null;
}) {
  const priorities = intelligence?.priority_insights ?? [];
  const watchItems = intelligence?.holdings_to_watch ?? [];

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-400">
            Today&apos;s Intelligence
          </p>
          <h2 className="mt-2 text-2xl font-bold">
            What deserves attention
          </h2>
        </div>

        <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs capitalize text-slate-300">
          {intelligence?.portfolio_status || "Unavailable"}
        </span>
      </div>

      {intelligence ? (
        <>
          <p className="mt-4 text-sm leading-6 text-slate-400">
            {intelligence.executive_summary}
          </p>

          <div className="mt-6 space-y-3">
            {priorities.length > 0 ? (
              priorities.slice(0, 4).map((item) => {
                const style = severityStyle(item.severity);

                return (
                  <article
                    key={`${item.priority}-${item.title}`}
                    className={`rounded-2xl border bg-slate-950 p-4 ${style.border}`}
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${style.marker}`}
                      >
                        {item.priority}
                      </span>

                      <div>
                        <h3 className="font-semibold text-white">
                          {item.title}
                        </h3>

                        <p className="mt-1 text-sm leading-6 text-slate-400">
                          {item.message}
                        </p>

                        <p className="mt-3 text-sm text-slate-300">
                          {item.suggested_action}
                        </p>
                      </div>
                    </div>
                  </article>
                );
              })
            ) : (
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
                <p className="font-semibold text-emerald-300">
                  No urgent portfolio issues detected
                </p>
                <p className="mt-2 text-sm text-slate-400">
                  Continue monitoring your portfolio and investment theses.
                </p>
              </div>
            )}
          </div>

          {watchItems.length > 0 && (
            <div className="mt-6 border-t border-slate-800 pt-5">
              <p className="text-sm font-semibold text-slate-200">
                Holdings to watch
              </p>

              <div className="mt-3 flex flex-wrap gap-2">
                {watchItems.slice(0, 5).map((item) => (
                  <span
                    key={item.symbol}
                    className="rounded-full border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300"
                  >
                    <strong className="text-white">{item.symbol}</strong>
                    {" · "}
                    {item.reason}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-400">
            Portfolio intelligence is temporarily unavailable.
          </p>
        </div>
      )}
    </section>
  );
}
