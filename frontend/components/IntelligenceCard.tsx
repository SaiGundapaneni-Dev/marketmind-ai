import type { ReactNode } from "react";

type IntelligenceCardProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
};

export default function IntelligenceCard({
  title,
  subtitle,
  children,
  className = "",
}: IntelligenceCardProps) {
  return (
    <section
      className={`rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-sm ${className}`}
    >
      <div>
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        {subtitle && (
          <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
        )}
      </div>

      <div className="mt-5">{children}</div>
    </section>
  );
}
