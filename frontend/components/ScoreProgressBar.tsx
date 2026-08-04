"use client";

type ScoreProgressBarProps = {
  label: string;
  score: number;
  rating?: string;
};

function getBarClass(score: number) {
  if (score >= 85) {
    return "bg-emerald-400";
  }

  if (score >= 70) {
    return "bg-blue-400";
  }

  if (score >= 50) {
    return "bg-amber-400";
  }

  return "bg-red-400";
}

function getTextClass(score: number) {
  if (score >= 85) {
    return "text-emerald-300";
  }

  if (score >= 70) {
    return "text-blue-300";
  }

  if (score >= 50) {
    return "text-amber-300";
  }

  return "text-red-300";
}

export default function ScoreProgressBar({
  label,
  score,
  rating,
}: ScoreProgressBarProps) {
  const safeScore = Math.min(Math.max(score, 0), 100);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-200">
            {label}
          </p>

          {rating && (
            <p className="mt-1 text-xs capitalize text-slate-500">
              {rating}
            </p>
          )}
        </div>

        <p className={`text-lg font-bold ${getTextClass(safeScore)}`}>
          {safeScore.toFixed(0)}
        </p>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-700 ${getBarClass(
            safeScore
          )}`}
          style={{ width: `${safeScore}%` }}
        />
      </div>
    </div>
  );
}
