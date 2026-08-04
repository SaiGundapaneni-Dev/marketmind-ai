"use client";

import {
  FormEvent,
  useState,
} from "react";

import { apiFetch } from "@/lib/api";
import InvestmentReviewCard from "@/components/InvestmentReviewCard";

export type Holding = {
  id: number;
  asset_type: string;
  symbol: string;
  name: string;
  quantity: number;
  average_price: number;
  current_price: number | null;
  cost: number;
  current_value: number;
  profit: number;
  profit_percent: number;
  allocation_percent: number;
  price_status: string;
};

type InvestmentThesis = {
  id: number;
  holding_id: number;
  thesis: string;
  target_price: number | null;
  investment_horizon: string | null;
  conviction_score: number | null;
  risk_level: string | null;
  buy_reasons: string | null;
  sell_conditions: string | null;
  notes: string | null;
  review_date: string | null;
  created_at: string;
  updated_at: string;
};

type ThesisForm = {
  thesis: string;
  target_price: string;
  investment_horizon: string;
  conviction_score: string;
  risk_level: string;
  buy_reasons: string;
  sell_conditions: string;
  notes: string;
  review_date: string;
};

const emptyThesisForm: ThesisForm = {
  thesis: "",
  target_price: "",
  investment_horizon: "",
  conviction_score: "",
  risk_level: "",
  buy_reasons: "",
  sell_conditions: "",
  notes: "",
  review_date: "",
};

function formatMoney(value: number | null) {
  if (value === null) {
    return "Unavailable";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatDate(value: string | null) {
  if (!value) {
    return "Not set";
  }

  const date = new Date(
    `${value}T00:00:00`
  );

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-US",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
    }
  ).format(date);
}

async function getErrorMessage(
  response: Response,
  fallback: string
) {
  try {
    const data = await response.json();

    if (
      typeof data?.detail === "string"
    ) {
      return data.detail;
    }
  } catch {
    // Use fallback when the response
    // is not valid JSON.
  }

  return fallback;
}

export default function HoldingsTable({
  holdings,
}: {
  holdings: Holding[];
}) {
  const [deletingId, setDeletingId] =
    useState<number | null>(null);

  const [message, setMessage] =
    useState("");

  const [
    selectedHolding,
    setSelectedHolding,
  ] = useState<Holding | null>(null);

  const [
    selectedThesis,
    setSelectedThesis,
  ] = useState<InvestmentThesis | null>(
    null
  );

  const [thesisForm, setThesisForm] =
    useState<ThesisForm>(
      emptyThesisForm
    );

  const [
    thesisLoading,
    setThesisLoading,
  ] = useState(false);

  const [
    thesisSaving,
    setThesisSaving,
  ] = useState(false);

  const [
    thesisDeleting,
    setThesisDeleting,
  ] = useState(false);

  const [
    thesisMessage,
    setThesisMessage,
  ] = useState("");

  const [isModalOpen, setIsModalOpen] =
    useState(false);

  async function deleteHolding(
    holding: Holding
  ) {
    const confirmed = window.confirm(
      `Are you sure you want to delete ${holding.symbol}?`
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(holding.id);
    setMessage("");

    try {
      const response = await apiFetch(
        `/portfolio/holdings/${holding.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorMessage =
          await getErrorMessage(
            response,
            `Failed to delete ${holding.symbol}.`
          );

        setMessage(errorMessage);
        return;
      }

      setMessage(
        `${holding.symbol} deleted successfully.`
      );

      window.location.reload();
    } catch (error) {
      console.error(
        "Delete holding error:",
        error
      );

      setMessage(
        "Unable to connect to Vestora AI."
      );
    } finally {
      setDeletingId(null);
    }
  }

  function populateThesisForm(
    thesis: InvestmentThesis
  ) {
    setThesisForm({
      thesis: thesis.thesis ?? "",
      target_price:
        thesis.target_price !== null
          ? String(thesis.target_price)
          : "",
      investment_horizon:
        thesis.investment_horizon ?? "",
      conviction_score:
        thesis.conviction_score !== null
          ? String(
              thesis.conviction_score
            )
          : "",
      risk_level:
        thesis.risk_level ?? "",
      buy_reasons:
        thesis.buy_reasons ?? "",
      sell_conditions:
        thesis.sell_conditions ?? "",
      notes: thesis.notes ?? "",
      review_date:
        thesis.review_date ?? "",
    });
  }

  async function openThesisModal(
    holding: Holding
  ) {
    setSelectedHolding(holding);
    setSelectedThesis(null);
    setThesisForm(emptyThesisForm);
    setThesisMessage("");
    setIsModalOpen(true);
    setThesisLoading(true);

    try {
      const response = await apiFetch(
        `/portfolio/thesis/${holding.id}`
      );

      if (response.status === 404) {
        setSelectedThesis(null);
        setThesisForm(
          emptyThesisForm
        );
        return;
      }

      if (!response.ok) {
        const errorMessage =
          await getErrorMessage(
            response,
            "Unable to load the investment thesis."
          );

        setThesisMessage(
          errorMessage
        );
        return;
      }

      const thesis: InvestmentThesis =
        await response.json();

      setSelectedThesis(thesis);
      populateThesisForm(thesis);
    } catch (error) {
      console.error(
        "Load thesis error:",
        error
      );

      setThesisMessage(
        "Unable to connect to Vestora AI."
      );
    } finally {
      setThesisLoading(false);
    }
  }

  function closeThesisModal() {
    if (
      thesisSaving ||
      thesisDeleting
    ) {
      return;
    }

    setIsModalOpen(false);
    setSelectedHolding(null);
    setSelectedThesis(null);
    setThesisForm(emptyThesisForm);
    setThesisMessage("");
  }

  function updateThesisField(
    field: keyof ThesisForm,
    value: string
  ) {
    setThesisForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function buildThesisPayload() {
    return {
      thesis:
        thesisForm.thesis.trim(),

      target_price:
        thesisForm.target_price
          ? Number(
              thesisForm.target_price
            )
          : null,

      investment_horizon:
        thesisForm
          .investment_horizon
          .trim() || null,

      conviction_score:
        thesisForm.conviction_score
          ? Number(
              thesisForm.conviction_score
            )
          : null,

      risk_level:
        thesisForm.risk_level ||
        null,

      buy_reasons:
        thesisForm.buy_reasons.trim() ||
        null,

      sell_conditions:
        thesisForm
          .sell_conditions
          .trim() || null,

      notes:
        thesisForm.notes.trim() ||
        null,

      review_date:
        thesisForm.review_date ||
        null,
    };
  }

  async function saveThesis(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!selectedHolding) {
      return;
    }

    if (
      !thesisForm.thesis.trim()
    ) {
      setThesisMessage(
        "Please enter your investment thesis."
      );
      return;
    }

    const convictionScore =
      thesisForm.conviction_score
        ? Number(
            thesisForm.conviction_score
          )
        : null;

    if (
      convictionScore !== null &&
      (
        convictionScore < 1 ||
        convictionScore > 10
      )
    ) {
      setThesisMessage(
        "Conviction score must be between 1 and 10."
      );
      return;
    }

    setThesisSaving(true);
    setThesisMessage("");

    const isEditing =
      selectedThesis !== null;

    const endpoint = isEditing
      ? `/portfolio/thesis/${selectedHolding.id}`
      : "/portfolio/thesis";

    const method = isEditing
      ? "PUT"
      : "POST";

    const payload = isEditing
      ? buildThesisPayload()
      : {
          holding_id:
            selectedHolding.id,
          ...buildThesisPayload(),
        };

    try {
      const response = await apiFetch(
        endpoint,
        {
          method,
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorMessage =
          await getErrorMessage(
            response,
            `Unable to ${
              isEditing
                ? "update"
                : "create"
            } the investment thesis.`
          );

        setThesisMessage(
          errorMessage
        );
        return;
      }

      const savedThesis:
        InvestmentThesis =
        await response.json();

      setSelectedThesis(
        savedThesis
      );

      populateThesisForm(
        savedThesis
      );

      setThesisMessage(
        isEditing
          ? "Investment thesis updated successfully."
          : "Investment thesis created successfully."
      );
    } catch (error) {
      console.error(
        "Save thesis error:",
        error
      );

      setThesisMessage(
        "Unable to connect to Vestora AI."
      );
    } finally {
      setThesisSaving(false);
    }
  }

  async function deleteThesis() {
    if (
      !selectedHolding ||
      !selectedThesis
    ) {
      return;
    }

    const confirmed = window.confirm(
      `Delete the investment thesis for ${selectedHolding.symbol}?`
    );

    if (!confirmed) {
      return;
    }

    setThesisDeleting(true);
    setThesisMessage("");

    try {
      const response = await apiFetch(
        `/portfolio/thesis/${selectedHolding.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorMessage =
          await getErrorMessage(
            response,
            "Unable to delete the investment thesis."
          );

        setThesisMessage(
          errorMessage
        );
        return;
      }

      setSelectedThesis(null);
      setThesisForm(
        emptyThesisForm
      );

      setThesisMessage(
        "Investment thesis deleted successfully."
      );
    } catch (error) {
      console.error(
        "Delete thesis error:",
        error
      );

      setThesisMessage(
        "Unable to connect to Vestora AI."
      );
    } finally {
      setThesisDeleting(false);
    }
  }

  return (
    <>
      <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <h2 className="text-xl font-semibold">
          Holdings
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Live holdings from your private
          Vestora portfolio.
        </p>

        {message && (
          <p className="mt-4 text-sm text-slate-300">
            {message}
          </p>
        )}

        {holdings.length === 0 && (
          <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-6 text-center">
            <h3 className="font-semibold text-white">
              Your portfolio is empty
            </h3>

            <p className="mt-2 text-sm text-slate-400">
              Add your first US stock using
              the Add Holding form above.
            </p>
          </div>
        )}

        {holdings.length > 0 && (
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[1250px] text-left text-sm">
              <thead className="border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="py-3 pr-4">
                    Symbol
                  </th>

                  <th className="py-3 pr-4">
                    Name
                  </th>

                  <th className="py-3 pr-4">
                    Asset
                  </th>

                  <th className="py-3 pr-4">
                    Qty
                  </th>

                  <th className="py-3 pr-4">
                    Avg Price
                  </th>

                  <th className="py-3 pr-4">
                    Current Price
                  </th>

                  <th className="py-3 pr-4">
                    Current Value
                  </th>

                  <th className="py-3 pr-4">
                    Allocation
                  </th>

                  <th className="py-3 pr-4">
                    P/L
                  </th>

                  <th className="py-3 pr-4">
                    P/L %
                  </th>

                  <th className="py-3">
                    Actions
                  </th>
                </tr>
              </thead>

              <tbody>
                {holdings.map(
                  (holding) => (
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
                        {formatMoney(
                          holding.average_price
                        )}
                      </td>

                      <td className="py-4 pr-4">
                        {formatMoney(
                          holding.current_price
                        )}
                      </td>

                      <td className="py-4 pr-4">
                        {formatMoney(
                          holding.current_value
                        )}
                      </td>

                      <td className="py-4 pr-4">
                        {holding
                          .allocation_percent
                          .toFixed(2)}
                        %
                      </td>

                      <td
                        className={`py-4 pr-4 ${
                          holding.profit >= 0
                            ? "text-emerald-300"
                            : "text-red-300"
                        }`}
                      >
                        {formatMoney(
                          holding.profit
                        )}
                      </td>

                      <td
                        className={`py-4 pr-4 ${
                          holding
                            .profit_percent >= 0
                            ? "text-emerald-300"
                            : "text-red-300"
                        }`}
                      >
                        {holding
                          .profit_percent
                          .toFixed(2)}
                        %
                      </td>

                      <td className="py-4">
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() =>
                              openThesisModal(
                                holding
                              )
                            }
                            className="rounded-lg border border-cyan-500/30 px-3 py-2 text-cyan-300 transition hover:bg-cyan-500/10"
                          >
                            Thesis
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              deleteHolding(
                                holding
                              )
                            }
                            disabled={
                              deletingId ===
                              holding.id
                            }
                            className="rounded-lg border border-red-500/30 px-3 py-2 text-red-400 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {deletingId ===
                            holding.id
                              ? "Deleting..."
                              : "Delete"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {isModalOpen &&
        selectedHolding && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 py-8 backdrop-blur-sm">
            <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
              <div className="sticky top-0 z-10 flex items-start justify-between border-b border-slate-800 bg-slate-900 px-6 py-5">
                <div>
                  <p className="text-sm text-cyan-300">
                    Investment Thesis
                  </p>

                  <h2 className="mt-1 text-2xl font-semibold text-white">
                    {
                      selectedHolding.symbol
                    }
                  </h2>

                  <p className="mt-1 text-sm text-slate-400">
                    {
                      selectedHolding.name
                    }
                  </p>
                </div>

                <button
                  type="button"
                  onClick={
                    closeThesisModal
                  }
                  className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
                >
                  Close
                </button>
              </div>

              <div className="p-6">
                {thesisLoading ? (
                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-8 text-center text-slate-400">
                    Loading investment
                    thesis...
                  </div>
                ) : (
                  <>
                    {selectedThesis && (
                      <div className="mb-6 grid gap-4 sm:grid-cols-4">
                        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                          <p className="text-xs uppercase tracking-wide text-slate-500">
                            Target
                          </p>

                          <p className="mt-2 font-semibold text-white">
                            {formatMoney(
                              selectedThesis
                                .target_price
                            )}
                          </p>
                        </div>

                        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                          <p className="text-xs uppercase tracking-wide text-slate-500">
                            Conviction
                          </p>

                          <p className="mt-2 font-semibold text-white">
                            {selectedThesis
                              .conviction_score !==
                            null
                              ? `${selectedThesis.conviction_score}/10`
                              : "Not set"}
                          </p>
                        </div>

                        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                          <p className="text-xs uppercase tracking-wide text-slate-500">
                            Risk
                          </p>

                          <p className="mt-2 font-semibold text-white">
                            {selectedThesis
                              .risk_level ||
                              "Not set"}
                          </p>
                        </div>

                        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                          <p className="text-xs uppercase tracking-wide text-slate-500">
                            Review
                          </p>

                          <p className="mt-2 font-semibold text-white">
                            {formatDate(
                              selectedThesis
                                .review_date
                            )}
                          </p>
                        </div>
                      </div>
                    )}

                    {selectedThesis && (
                      <InvestmentReviewCard
                        holdingId={
                          selectedHolding.id
                        }
                        symbol={
                          selectedHolding.symbol
                        }
                      />
                    )}

                    <form
                      onSubmit={saveThesis}
                      className="space-y-5"
                    >
                      <div>
                        <label className="text-sm font-medium text-slate-200">
                          Investment thesis
                        </label>

                        <textarea
                          value={
                            thesisForm.thesis
                          }
                          onChange={(event) =>
                            updateThesisField(
                              "thesis",
                              event.target.value
                            )
                          }
                          rows={5}
                          required
                          placeholder="Why do you own this investment?"
                          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                        />
                      </div>

                      <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                          <label className="text-sm font-medium text-slate-200">
                            Target price
                          </label>

                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={
                              thesisForm
                                .target_price
                            }
                            onChange={(
                              event
                            ) =>
                              updateThesisField(
                                "target_price",
                                event.target
                                  .value
                              )
                            }
                            placeholder="300"
                            className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                          />
                        </div>

                        <div>
                          <label className="text-sm font-medium text-slate-200">
                            Investment horizon
                          </label>

                          <input
                            type="text"
                            value={
                              thesisForm
                                .investment_horizon
                            }
                            onChange={(
                              event
                            ) =>
                              updateThesisField(
                                "investment_horizon",
                                event.target
                                  .value
                              )
                            }
                            placeholder="5 Years"
                            className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                          />
                        </div>

                        <div>
                          <label className="text-sm font-medium text-slate-200">
                            Conviction score
                          </label>

                          <input
                            type="number"
                            min="1"
                            max="10"
                            step="1"
                            value={
                              thesisForm
                                .conviction_score
                            }
                            onChange={(
                              event
                            ) =>
                              updateThesisField(
                                "conviction_score",
                                event.target
                                  .value
                              )
                            }
                            placeholder="1 to 10"
                            className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                          />
                        </div>

                        <div>
                          <label className="text-sm font-medium text-slate-200">
                            Risk level
                          </label>

                          <select
                            value={
                              thesisForm
                                .risk_level
                            }
                            onChange={(
                              event
                            ) =>
                              updateThesisField(
                                "risk_level",
                                event.target
                                  .value
                              )
                            }
                            className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
                          >
                            <option value="">
                              Select risk
                            </option>

                            <option value="Low">
                              Low
                            </option>

                            <option value="Medium">
                              Medium
                            </option>

                            <option value="High">
                              High
                            </option>
                          </select>
                        </div>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-slate-200">
                          Buy reasons
                        </label>

                        <textarea
                          value={
                            thesisForm
                              .buy_reasons
                          }
                          onChange={(event) =>
                            updateThesisField(
                              "buy_reasons",
                              event.target.value
                            )
                          }
                          rows={3}
                          placeholder="Strong moat, AI growth, recurring revenue..."
                          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium text-slate-200">
                          Sell conditions
                        </label>

                        <textarea
                          value={
                            thesisForm
                              .sell_conditions
                          }
                          onChange={(event) =>
                            updateThesisField(
                              "sell_conditions",
                              event.target.value
                            )
                          }
                          rows={3}
                          placeholder="What would invalidate your thesis?"
                          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium text-slate-200">
                          Notes
                        </label>

                        <textarea
                          value={
                            thesisForm.notes
                          }
                          onChange={(event) =>
                            updateThesisField(
                              "notes",
                              event.target.value
                            )
                          }
                          rows={3}
                          placeholder="Additional notes..."
                          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium text-slate-200">
                          Review date
                        </label>

                        <input
                          type="date"
                          value={
                            thesisForm
                              .review_date
                          }
                          onChange={(event) =>
                            updateThesisField(
                              "review_date",
                              event.target.value
                            )
                          }
                          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500 sm:w-64"
                        />
                      </div>

                      {thesisMessage && (
                        <p className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-300">
                          {thesisMessage}
                        </p>
                      )}

                      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 pt-5">
                        <div>
                          {selectedThesis && (
                            <button
                              type="button"
                              onClick={
                                deleteThesis
                              }
                              disabled={
                                thesisDeleting ||
                                thesisSaving
                              }
                              className="rounded-lg border border-red-500/30 px-4 py-2.5 text-red-400 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              {thesisDeleting
                                ? "Deleting..."
                                : "Delete Thesis"}
                            </button>
                          )}
                        </div>

                        <div className="flex gap-3">
                          <button
                            type="button"
                            onClick={
                              closeThesisModal
                            }
                            disabled={
                              thesisSaving ||
                              thesisDeleting
                            }
                            className="rounded-lg border border-slate-700 px-4 py-2.5 text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            Cancel
                          </button>

                          <button
                            type="submit"
                            disabled={
                              thesisSaving ||
                              thesisDeleting
                            }
                            className="rounded-lg bg-cyan-500 px-4 py-2.5 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {thesisSaving
                              ? "Saving..."
                              : selectedThesis
                                ? "Update Thesis"
                                : "Create Thesis"}
                          </button>
                        </div>
                      </div>
                    </form>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
    </>
  );
}