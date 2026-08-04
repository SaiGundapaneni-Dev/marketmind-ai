"use client";

import { FormEvent, useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";

type ScenarioChange = {
  symbol: string;
  change_percent: number;
};

type ScenarioPreset = {
  key: string;
  name: string;
  description: string;
  changes: ScenarioChange[];
};

type HoldingImpact = {
  symbol: string;
  name: string;
  current_value: number;
  change_percent: number;
  projected_value: number;
  impact_value: number;
  portfolio_impact_percent: number;
};

type Simulation = {
  scenario_name: string;
  current_portfolio_value: number;
  projected_portfolio_value: number;
  impact_value: number;
  impact_percent: number;
  affected_holdings_count: number;
  unaffected_holdings_count: number;
  resilience_score: number;
  risk_level: "low" | "medium" | "high" | "severe";
  recommendation: string;
  explanation: string;
  holding_impacts: HoldingImpact[];
  warnings: string[];
  disclaimer: string;
};

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function percent(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function riskClass(risk: Simulation["risk_level"]) {
  if (risk === "severe" || risk === "high") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (risk === "medium") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
}

export default function ScenarioSimulatorPage() {
  const [presets, setPresets] = useState<ScenarioPreset[]>([]);
  const [scenarioName, setScenarioName] = useState("Custom Scenario");
  const [symbol, setSymbol] = useState("");
  const [changePercent, setChangePercent] = useState("-20");
  const [changes, setChanges] = useState<ScenarioChange[]>([]);
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [loading, setLoading] = useState(false);
  const [presetsLoading, setPresetsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadPresets() {
      try {
        const response = await apiFetch(
          "/portfolio/scenarios/presets",
          { cache: "no-store" }
        );

        if (!response.ok) {
          throw new Error("Unable to load scenario presets.");
        }

        const data = await response.json();
        setPresets(data.presets ?? []);
      } catch (requestError) {
        console.error("Scenario presets error:", requestError);
        setError("Unable to load scenario presets.");
      } finally {
        setPresetsLoading(false);
      }
    }

    loadPresets();
  }, []);

  function addChange(event: FormEvent) {
    event.preventDefault();

    const cleanSymbol = symbol.trim().toUpperCase();
    const parsedChange = Number(changePercent);

    if (
      !cleanSymbol ||
      Number.isNaN(parsedChange) ||
      parsedChange < -100 ||
      parsedChange > 500
    ) {
      setError(
        "Enter a valid symbol and a percentage between -100 and 500."
      );
      return;
    }

    setChanges((current) => {
      const withoutExisting = current.filter(
        (item) => item.symbol !== cleanSymbol
      );

      return [
        ...withoutExisting,
        {
          symbol: cleanSymbol,
          change_percent: parsedChange,
        },
      ];
    });

    setSymbol("");
    setError("");
    setSimulation(null);
  }

  function selectPreset(preset: ScenarioPreset) {
    setScenarioName(preset.name);
    setChanges(preset.changes);
    setSimulation(null);
    setError("");

    if (preset.changes.length === 0) {
      setError(
        "None of your current priced holdings match this preset."
      );
    }
  }

  function removeChange(target: string) {
    setChanges((current) =>
      current.filter((item) => item.symbol !== target)
    );
    setSimulation(null);
  }

  async function runSimulation() {
    if (changes.length === 0) {
      setError("Add at least one stock change before simulating.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(
        "/portfolio/scenarios/simulate",
        {
          method: "POST",
          body: JSON.stringify({
            name: scenarioName.trim() || "Custom Scenario",
            changes,
          }),
        }
      );

      if (!response.ok) {
        let message = "Scenario simulation failed.";

        try {
          const data = await response.json();
          if (typeof data?.detail === "string") {
            message = data.detail;
          }
        } catch {
          // Keep fallback.
        }

        throw new Error(message);
      }

      setSimulation(await response.json());
    } catch (requestError) {
      console.error("Scenario simulation error:", requestError);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to run scenario simulation."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-7 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <header>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
              Predictive Intelligence
            </p>

            <h1 className="mt-2 text-3xl font-bold sm:text-4xl">
              Scenario Simulator
            </h1>

            <p className="mt-3 max-w-3xl text-slate-400">
              Model deterministic what-if changes against your current
              portfolio and see which holdings drive the result.
            </p>
          </header>

          <section className="mt-7 rounded-3xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm font-semibold text-white">
              Built-in scenarios
            </p>

            {presetsLoading ? (
              <p className="mt-4 text-sm text-slate-400">
                Loading presets...
              </p>
            ) : (
              <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {presets.map((preset) => (
                  <button
                    key={preset.key}
                    type="button"
                    onClick={() => selectPreset(preset)}
                    className="rounded-2xl border border-slate-800 bg-slate-950 p-5 text-left transition hover:border-blue-500"
                  >
                    <p className="font-semibold text-white">
                      {preset.name}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {preset.description}
                    </p>
                    <p className="mt-3 text-xs text-slate-500">
                      {preset.changes.length} matching holding
                      {preset.changes.length === 1 ? "" : "s"}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </section>

          <section className="mt-7 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">
                Build a custom scenario
              </h2>

              <label className="mt-5 block text-sm text-slate-300">
                Scenario name
              </label>

              <input
                value={scenarioName}
                onChange={(event) => setScenarioName(event.target.value)}
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />

              <form onSubmit={addChange} className="mt-5 space-y-4">
                <div>
                  <label className="text-sm text-slate-300">
                    Stock symbol
                  </label>
                  <input
                    value={symbol}
                    onChange={(event) =>
                      setSymbol(event.target.value.toUpperCase())
                    }
                    placeholder="NVDA"
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="text-sm text-slate-300">
                    Price change %
                  </label>
                  <input
                    type="number"
                    min="-100"
                    max="500"
                    step="0.1"
                    value={changePercent}
                    onChange={(event) =>
                      setChangePercent(event.target.value)
                    }
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full rounded-xl border border-blue-500/30 bg-blue-500/10 px-4 py-3 font-semibold text-blue-300 hover:bg-blue-500/20"
                >
                  Add or update change
                </button>
              </form>

              {error && (
                <p className="mt-4 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
                  {error}
                </p>
              )}
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-xl font-bold">
                    Scenario changes
                  </h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Only symbols currently owned will affect the result.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={runSimulation}
                  disabled={loading || changes.length === 0}
                  className="rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? "Simulating..." : "Run simulation"}
                </button>
              </div>

              <div className="mt-5 space-y-3">
                {changes.length > 0 ? (
                  changes.map((item) => (
                    <div
                      key={item.symbol}
                      className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <div>
                        <p className="font-semibold text-white">
                          {item.symbol}
                        </p>
                        <p
                          className={`mt-1 text-sm ${
                            item.change_percent >= 0
                              ? "text-emerald-300"
                              : "text-red-300"
                          }`}
                        >
                          {percent(item.change_percent)}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeChange(item.symbol)}
                        className="text-sm text-red-400 hover:text-red-300"
                      >
                        Remove
                      </button>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-sm text-slate-500">
                    Select a preset or add a custom stock change.
                  </div>
                )}
              </div>
            </div>
          </section>

          {simulation && (
            <>
              <section className="mt-7 overflow-hidden rounded-3xl border border-slate-800 bg-slate-900">
                <div className="p-6 sm:p-8">
                  <div className="flex flex-wrap items-start justify-between gap-5">
                    <div>
                      <p className="text-sm text-slate-400">
                        Simulation result
                      </p>
                      <h2 className="mt-2 text-2xl font-bold">
                        {simulation.scenario_name}
                      </h2>
                    </div>

                    <span
                      className={`rounded-full border px-4 py-2 text-sm font-bold uppercase ${riskClass(
                        simulation.risk_level
                      )}`}
                    >
                      {simulation.risk_level} risk
                    </span>
                  </div>

                  <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
                    <Metric
                      label="Before"
                      value={money(
                        simulation.current_portfolio_value
                      )}
                    />
                    <Metric
                      label="After"
                      value={money(
                        simulation.projected_portfolio_value
                      )}
                    />
                    <Metric
                      label="Impact"
                      value={money(simulation.impact_value)}
                      negative={simulation.impact_value < 0}
                      positive={simulation.impact_value > 0}
                    />
                    <Metric
                      label="Impact %"
                      value={percent(simulation.impact_percent)}
                      negative={simulation.impact_percent < 0}
                      positive={simulation.impact_percent > 0}
                    />
                    <Metric
                      label="Resilience"
                      value={`${simulation.resilience_score.toFixed(
                        0
                      )}/100`}
                    />
                  </div>

                  <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-5">
                    <p className="font-semibold text-white">
                      {simulation.recommendation}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {simulation.explanation}
                    </p>
                  </div>
                </div>
              </section>

              <section className="mt-7 rounded-3xl border border-slate-800 bg-slate-900 p-6">
                <h2 className="text-xl font-bold">
                  Holding impact
                </h2>

                <div className="mt-5 overflow-x-auto">
                  <table className="w-full min-w-[800px] text-left text-sm">
                    <thead className="border-b border-slate-800 text-slate-400">
                      <tr>
                        <th className="py-3 pr-4">Symbol</th>
                        <th className="py-3 pr-4">Current</th>
                        <th className="py-3 pr-4">Change</th>
                        <th className="py-3 pr-4">Projected</th>
                        <th className="py-3 pr-4">Impact</th>
                        <th className="py-3">Portfolio impact</th>
                      </tr>
                    </thead>
                    <tbody>
                      {simulation.holding_impacts.map((item) => (
                        <tr
                          key={item.symbol}
                          className="border-b border-slate-800 last:border-0"
                        >
                          <td className="py-4 pr-4">
                            <p className="font-semibold text-white">
                              {item.symbol}
                            </p>
                            <p className="mt-1 text-xs text-slate-500">
                              {item.name}
                            </p>
                          </td>
                          <td className="py-4 pr-4">
                            {money(item.current_value)}
                          </td>
                          <td
                            className={`py-4 pr-4 ${
                              item.change_percent >= 0
                                ? "text-emerald-300"
                                : "text-red-300"
                            }`}
                          >
                            {percent(item.change_percent)}
                          </td>
                          <td className="py-4 pr-4">
                            {money(item.projected_value)}
                          </td>
                          <td
                            className={`py-4 pr-4 ${
                              item.impact_value >= 0
                                ? "text-emerald-300"
                                : "text-red-300"
                            }`}
                          >
                            {money(item.impact_value)}
                          </td>
                          <td className="py-4">
                            {percent(
                              item.portfolio_impact_percent
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {simulation.warnings.length > 0 && (
                  <div className="mt-5 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
                    {simulation.warnings.map((warning) => (
                      <p
                        key={warning}
                        className="text-sm leading-6 text-amber-100/80"
                      >
                        • {warning}
                      </p>
                    ))}
                  </div>
                )}

                <p className="mt-5 text-xs leading-5 text-slate-500">
                  {simulation.disclaimer}
                </p>
              </section>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

function Metric({
  label,
  value,
  negative = false,
  positive = false,
}: {
  label: string;
  value: string;
  negative?: boolean;
  positive?: boolean;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </p>
      <p
        className={`mt-2 text-lg font-bold ${
          negative
            ? "text-red-300"
            : positive
              ? "text-emerald-300"
              : "text-white"
        }`}
      >
        {value}
      </p>
    </div>
  );
}
