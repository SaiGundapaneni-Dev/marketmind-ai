"use client";

import { useState } from "react";

import { apiFetch } from "@/lib/api";

export default function AddHoldingForm() {
  const [symbol, setSymbol] = useState("");
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const [averagePrice, setAveragePrice] = useState("");
  const [message, setMessage] = useState("");
  const [adding, setAdding] = useState(false);

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (adding) {
      return;
    }

    const cleanSymbol = symbol.trim().toUpperCase();
    const cleanName = name.trim();
    const parsedQuantity = Number(quantity);
    const parsedAveragePrice = Number(averagePrice);

    if (!cleanSymbol || !cleanName) {
      setMessage("Symbol and name are required.");
      return;
    }

    if (
      !Number.isFinite(parsedQuantity) ||
      !Number.isFinite(parsedAveragePrice) ||
      parsedQuantity <= 0 ||
      parsedAveragePrice <= 0
    ) {
      setMessage(
        "Quantity and average price must be greater than zero."
      );
      return;
    }

    setAdding(true);
    setMessage("Adding holding...");

    try {
      const response = await apiFetch(
        "/portfolio/holdings",
        {
          method: "POST",
          body: JSON.stringify({
            asset_type: "US",
            symbol: cleanSymbol,
            name: cleanName,
            quantity: parsedQuantity,
            average_price: parsedAveragePrice,
            currency: "USD",
          }),
        }
      );

      if (!response.ok) {
        let detail = "Failed to add holding.";

        try {
          const errorData = await response.json();

          if (typeof errorData?.detail === "string") {
            detail = errorData.detail;
          }
        } catch {
          // Keep fallback message.
        }

        setMessage(detail);
        return;
      }

      setSymbol("");
      setName("");
      setQuantity("");
      setAveragePrice("");
      setMessage("Holding added successfully.");

      window.location.reload();
    } catch (error) {
      console.error("Add holding error:", error);
      setMessage("Unable to connect to Vestora AI.");
    } finally {
      setAdding(false);
    }
  }

  return (
    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="text-xl font-semibold">Add Holding</h2>

      <p className="mt-1 text-sm text-slate-400">
        Add a stock to your private Vestora portfolio.
      </p>

      <form
        onSubmit={handleSubmit}
        className="mt-5 grid gap-4 md:grid-cols-4"
      >
        <input
          className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          placeholder="Symbol"
          value={symbol}
          onChange={(event) =>
            setSymbol(event.target.value.toUpperCase())
          }
          required
        />

        <input
          className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          placeholder="Name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />

        <input
          className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          placeholder="Quantity"
          type="number"
          min="0"
          step="any"
          value={quantity}
          onChange={(event) => setQuantity(event.target.value)}
          required
        />

        <input
          className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          placeholder="Average Price"
          type="number"
          min="0"
          step="any"
          value={averagePrice}
          onChange={(event) =>
            setAveragePrice(event.target.value)
          }
          required
        />

        <button
          type="submit"
          disabled={adding}
          className="rounded-xl bg-blue-600 px-4 py-3 font-semibold hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50 md:col-span-4 md:w-fit"
        >
          {adding ? "Adding..." : "Add Holding"}
        </button>
      </form>

      {message && (
        <p className="mt-4 text-sm text-slate-400">
          {message}
        </p>
      )}
    </div>
  );
}
