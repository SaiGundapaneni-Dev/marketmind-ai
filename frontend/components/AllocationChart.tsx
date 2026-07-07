"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { Holding } from "./HoldingsTable";

export default function AllocationChart({
  holdings,
}: {
  holdings: Holding[];
}) {
  const data = holdings.map((holding) => ({
    name: holding.symbol,
    value: holding.current_value,
  }));

  return (
    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="text-xl font-semibold">Portfolio Allocation</h2>
      <p className="mt-1 text-sm text-slate-400">
        Allocation by current market value.
      </p>

      <div className="mt-6 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              outerRadius={110}
              label
            >
              {data.map((entry) => (
                <Cell key={entry.name} />
              ))}
            </Pie>

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}