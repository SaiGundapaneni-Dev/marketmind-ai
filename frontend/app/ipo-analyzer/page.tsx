"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type IPOResponse = {
  company_name: string;
  symbol?: string | null;
  status: string;
  sector?: string;
  exchange?: string | null;
  ipo_year?: number | null;
  description?: string;
  ipo_available: boolean;
  message: string;
  analysis: {
    score: number;
    rating: string;
    recommendation: string;
    confidence: number;
    reasons: string[];
    warnings: string[];
  };
};

type SECMatch = {
  company_name: string;
  ticker: string;
  cik: string;
};

type SECFiling = {
  form: string;
  accession_number?: string;
  filing_date?: string;
  report_date?: string;
  primary_document?: string;
  description?: string;
};

type SECFilingsResponse = {
  company_name: string;
  cik: string;
  count: number;
  ipo_filings: SECFiling[];
  error?: string;
};

function InfoCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-1 text-xl font-bold">{value}</p>
    </div>
  );
}

export default function IPOAnalyzerPage() {
  const [companyName, setCompanyName] = useState("");
  const [data, setData] = useState<IPOResponse | null>(null);
  const [secMatches, setSecMatches] = useState<SECMatch[]>([]);
  const [secFilings, setSecFilings] = useState<SECFilingsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [secLoading, setSecLoading] = useState(false);
  const [error, setError] = useState("");

  async function searchIPO(event: React.FormEvent) {
    event.preventDefault();

    const cleanCompanyName = companyName.trim();

    if (!cleanCompanyName) {
      setError("Please enter a company name.");
      return;
    }

    setLoading(true);
    setSecLoading(true);
    setData(null);
    setSecMatches([]);
    setSecFilings(null);
    setError("");

    try {
      const ipoResponse = await fetch(
        `http://127.0.0.1:8000/ipo/search/${encodeURIComponent(cleanCompanyName)}`
      );

      const ipoResult: IPOResponse = await ipoResponse.json();
      setData(ipoResult);

      const secResponse = await fetch(
        `http://127.0.0.1:8000/ipo/sec-search/${encodeURIComponent(cleanCompanyName)}`
      );

      const secResult = await secResponse.json();
      setSecMatches(secResult.matches || []);

      const firstMatch = secResult.matches?.[0];

      if (firstMatch?.cik) {
        const filingsResponse = await fetch(
          `http://127.0.0.1:8000/ipo/sec-ipo-filings/${firstMatch.cik}`
        );

        const filingsResult: SECFilingsResponse = await filingsResponse.json();
        setSecFilings(filingsResult);
      }
    } catch (searchError) {
      console.error("IPO search error:", searchError);
      setError("Unable to connect to the MarketMind IPO API.");
    } finally {
      setLoading(false);
      setSecLoading(false);
    }
  }

  function statusStyle(status: string) {
    if (status === "upcoming") return "border-green-500/30 text-green-400";
    if (status === "rumored") return "border-yellow-500/30 text-yellow-300";
    if (status === "listed") return "border-blue-500/30 text-blue-400";
    return "border-slate-700 text-slate-400";
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-medium text-blue-400">IPO Analyzer</p>

          <h1 className="mt-1 text-3xl font-bold">IPO Research Assistant</h1>

          <p className="mt-2 text-slate-400">
            Search an IPO company, review MarketMind analysis, and check SEC IPO filing availability.
          </p>

          <form onSubmit={searchIPO} className="mt-8 flex gap-3">
            <input
              className="w-full rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none transition focus:border-blue-500"
              placeholder="Enter company name, e.g. Stripe"
              value={companyName}
              onChange={(event) => setCompanyName(event.target.value)}
              required
            />

            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </form>

          {error && (
            <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {data && (
            <div className="mt-8 space-y-6">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-bold">
                      {data.company_name}
                      {data.symbol ? ` (${data.symbol})` : ""}
                    </h2>

                    <p className="mt-3 text-slate-300">{data.message}</p>
                  </div>

                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusStyle(
                      data.status
                    )}`}
                  >
                    {data.status.replaceAll("_", " ").toUpperCase()}
                  </span>
                </div>

                {data.description && (
                  <p className="mt-5 leading-7 text-slate-300">{data.description}</p>
                )}
              </div>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <InfoCard title="IPO Available" value={data.ipo_available ? "Yes" : "No"} />
                <InfoCard title="Sector" value={data.sector || "N/A"} />
                <InfoCard title="Exchange" value={data.exchange || "N/A"} />
                <InfoCard title="IPO Year" value={data.ipo_year ? String(data.ipo_year) : "N/A"} />
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-medium text-blue-400">MarketMind IPO Analysis</p>

                <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <InfoCard title="IPO Score" value={`${data.analysis.score}/60`} />
                  <InfoCard title="Rating" value={data.analysis.rating} />
                  <InfoCard title="Recommendation" value={data.analysis.recommendation} />
                  <InfoCard title="Confidence" value={`${data.analysis.confidence}%`} />
                </div>

                <div className="mt-6">
                  <h3 className="font-semibold">Analysis Reasons</h3>

                  <div className="mt-3 space-y-2">
                    {data.analysis.reasons.map((reason, index) => (
                      <p key={`${reason}-${index}`} className="text-sm text-slate-300">
                        • {reason}
                      </p>
                    ))}
                  </div>
                </div>

                {data.analysis.warnings.length > 0 && (
                  <div className="mt-6 rounded-xl border border-yellow-500/20 bg-yellow-500/10 p-4">
                    <p className="text-sm font-semibold text-yellow-300">Data Warnings</p>

                    <div className="mt-3 space-y-2">
                      {data.analysis.warnings.map((warning, index) => (
                        <p key={`${warning}-${index}`} className="text-sm text-yellow-100">
                          • {warning}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-medium text-blue-400">SEC Filing Research</p>

                <h2 className="mt-1 text-xl font-semibold">SEC Company Matches</h2>

                {secLoading && <p className="mt-4 text-slate-400">Searching SEC filings...</p>}

                {!secLoading && secMatches.length === 0 && (
                  <p className="mt-4 text-slate-400">
                    No SEC company match found for this search.
                  </p>
                )}

                {secMatches.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {secMatches.map((match) => (
                      <div
                        key={match.cik}
                        className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                      >
                        <p className="font-semibold">{match.company_name}</p>
                        <p className="mt-1 text-sm text-slate-400">
                          Ticker: {match.ticker || "N/A"} · CIK: {match.cik}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {secFilings && (
                  <div className="mt-6">
                    <h3 className="font-semibold">
                      IPO-Relevant SEC Filings ({secFilings.count})
                    </h3>

                    {secFilings.count === 0 && (
                      <p className="mt-3 text-sm text-slate-400">
                        No S-1, F-1, or prospectus filings found in the recent SEC filing list.
                      </p>
                    )}

                    {secFilings.ipo_filings.length > 0 && (
                      <div className="mt-4 space-y-3">
                        {secFilings.ipo_filings.map((filing, index) => (
                          <div
                            key={`${filing.accession_number}-${index}`}
                            className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                          >
                            <div className="flex flex-wrap items-center justify-between gap-3">
                              <p className="font-semibold">{filing.form}</p>
                              <p className="text-sm text-slate-400">
                                Filed: {filing.filing_date || "N/A"}
                              </p>
                            </div>

                            <p className="mt-2 text-sm text-slate-300">
                              {filing.description || "No description available."}
                            </p>

                            <p className="mt-2 text-xs text-slate-500">
                              Accession: {filing.accession_number || "N/A"}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {data.status === "listed" && (
                <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-5">
                  <p className="font-semibold text-blue-300">Already Publicly Listed</p>

                  <p className="mt-2 text-sm text-slate-300">
                    {data.company_name} is already publicly listed. Use the Stock Search section
                    for ongoing fundamental research and the News section for recent company
                    developments.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}