"use client";

import { useState } from "react";

export default function AddHoldingForm() {
  const [symbol, setSymbol] = useState("");
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const [averagePrice, setAveragePrice] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    setMessage("Adding holding...");

    const response = await fetch("http://127.0.0.1:8000/portfolio/holdings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        asset_type: "US",
        symbol,
        name,
        quantity: Number(quantity),
        average_price: Number(averagePrice),
        currency: "USD",
        portfolio_id: 1,
      }),
    });

    if (!response.ok) {
      setMessage("Failed to add holding.");
      return;
    }

    setMessage("Holding added successfully. Refresh the page to see it.");

    setSymbol("");
    setName("");
    setQuantity("");
    setAveragePrice("");
  }

  return (
    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="text-xl font-semibold">Add Holding</h2>

      <form onSubmit={handleSubmit} className="mt-5 grid gap-4 md:grid-cols-4">
        <input
          className="rounded-xl bg-slate-950 px-4 py-3 text-white outline-none"
          placeholder="Symbol"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          required
        />

        <input
          className="rounded-xl bg-slate-950 px-4 py-3 text-white outline-none"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <input
          className="rounded-xl bg-slate-950 px-4 py-3 text-white outline-none"
          placeholder="Quantity"
          type="number"
          step="any"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
        />

        <input
          className="rounded-xl bg-slate-950 px-4 py-3 text-white outline-none"
          placeholder="Average Price"
          type="number"
          step="any"
          value={averagePrice}
          onChange={(e) => setAveragePrice(e.target.value)}
          required
        />

        <button className="rounded-xl bg-blue-600 px-4 py-3 font-semibold hover:bg-blue-500">
          Add Holding
        </button>
      </form>

      {message && <p className="mt-4 text-sm text-slate-400">{message}</p>}
    </div>
  );
}