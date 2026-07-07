"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export type Holding = {
  id: number;
  asset_type: string;
  symbol: string;
  name: string;
  quantity: number;
  average_price: number;
  current_price: number;
  cost: number;
  current_value: number;
  profit: number;
  profit_percent: number;
};

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export default function HoldingsTable({
  holdings,
}: {
  holdings: Holding[];
}) {
  const router = useRouter();
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  async function deleteHolding(holding: Holding) {
    const confirmed = window.confirm(
      `Are you sure you want to delete ${holding.symbol}?`
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(holding.id);
    setMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/portfolio/holdings/${holding.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        setMessage(`Failed to delete ${holding.symbol}.`);
        return;
      }

      setMessage(`${holding.symbol} deleted successfully.`);
      router.refresh();
    } catch (error) {
      console.error("Delete holding error:", error);
      setMessage("Unable to connect to MarketMind API.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="text-xl font-semibold">Holdings</h2>

      <p className="mt-1 text-sm text-slate-400">
        Live portfolio holdings from the MarketMind API.
      </p>

      {message && (
        <p className="mt-4 text-sm text-slate-300">
          {message}
        </p>
      )}

      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[1000px] text-left text-sm">
          <thead className="border-b border-slate-800 text-slate-400">
            <tr>
              <th className="py-3 pr-4">Symbol</th>
              <th className="py-3 pr-4">Name</th>
              <th className="py-3 pr-4">Asset</th>
              <th className="py-3 pr-4">Qty</th>
              <th className="py-3 pr-4">Avg Price</th>
              <th className="py-3 pr-4">Current Price</th>
              <th className="py-3 pr-4">Current Value</th>
              <th className="py-3 pr-4">P/L</th>
              <th className="py-3 pr-4">P/L %</th>
              <th className="py-3">Actions</th>
            </tr>
          </thead>

          <tbody>
            {holdings.map((holding) => (
              <tr
                key={holding.id}
                className="border-b border-slate-800 last:border-0"
              >
                <td className="py-4 pr-4 font-semibold">
                  {holding.symbol}
                </td>

                <td className="py-4 pr-4">
                  {holding.name}
                </td>

                <td className="py-4 pr-4">
                  {holding.asset_type}
                </td>

                <td className="py-4 pr-4">
                  {holding.quantity}
                </td>

                <td className="py-4 pr-4">
                  {formatMoney(holding.average_price)}
                </td>

                <td className="py-4 pr-4">
                  {formatMoney(holding.current_price)}
                </td>

                <td className="py-4 pr-4">
                  {formatMoney(holding.current_value)}
                </td>

                <td className="py-4 pr-4">
                  {formatMoney(holding.profit)}
                </td>

                <td className="py-4 pr-4">
                  {holding.profit_percent.toFixed(2)}%
                </td>

                <td className="py-4">
                  <button
                    onClick={() => deleteHolding(holding)}
                    disabled={deletingId === holding.id}
                    className="rounded-lg border border-red-500/30 px-3 py-2 text-red-400 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {deletingId === holding.id
                      ? "Deleting..."
                      : "Delete"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}