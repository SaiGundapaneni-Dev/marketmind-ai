"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type IPOResponse = {
  company_name: string;
  status: string;
  ipo_available: boolean;
  message: string;
  analysis: {
    recommendation: string;
    confidence: number;
    reasons: string[];
  };
};

export default function IPOAnalyzerPage() {
  const [companyName, setCompanyName] = useState("");
  const [data, setData] = useState<IPOResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function searchIPO(event: React.FormEvent) {
    event.preventDefault();

    setLoading(true);
    setData(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/ipo/search/${companyName}`
      );

      const result = await response.json();
      setData(result);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-medium text-blue-400">IPO Analyzer</p>

          <h1 className="mt-1 text-3xl font-bold">
            IPO Research Assistant
          </h1>

          <p className="mt-2 text-slate-400">
            Search an IPO company and start an analysis workflow.
          </p>

          <form onSubmit={searchIPO} className="mt-8 flex gap-3">
            <input
              className="w-full rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none focus:border-blue-500"
              placeholder="Enter company name, e.g. Reddit"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              required
            />

            <button
              disabled={loading}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </form>

          {data && (
            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-2xl font-bold">{data.company_name}</h2>

              <p className="mt-3 text-slate-300">{data.message}</p>

              <div className="mt-6 grid gap-4 md:grid-cols-3">
                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-sm text-slate-400">IPO Available</p>
                  <p className="mt-1 text-xl font-bold">
                    {data.ipo_available ? "Yes" : "No"}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-sm text-slate-400">Recommendation</p>
                  <p className="mt-1 text-xl font-bold">
                    {data.analysis.recommendation}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-4">
                  <p className="text-sm text-slate-400">Confidence</p>
                  <p className="mt-1 text-xl font-bold">
                    {data.analysis.confidence}%
                  </p>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="font-semibold">Reasons</h3>

                <div className="mt-3 space-y-2">
                  {data.analysis.reasons.map((reason, index) => (
                    <p key={index} className="text-sm text-slate-300">
                      • {reason}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}