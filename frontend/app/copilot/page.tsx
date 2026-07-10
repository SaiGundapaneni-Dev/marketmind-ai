"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";

type CopilotResponse = {
  question: string;
  intent: string;
  answer: string;
  status: string;
  data?: unknown;
};

export default function CopilotPage() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<CopilotResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function askCopilot(event: React.FormEvent) {
    event.preventDefault();

    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/copilot/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setResponse(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-medium text-blue-400">AI Copilot</p>

          <h1 className="mt-1 text-3xl font-bold">MarketMind Copilot</h1>

          <p className="mt-2 text-slate-400">
            Ask questions about your portfolio, stocks, news, and IPO research.
          </p>

          <form onSubmit={askCopilot} className="mt-8 space-y-4">
            <textarea
              className="min-h-32 w-full rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 outline-none focus:border-blue-500"
              placeholder="Example: What is the latest news on NVDA?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              required
            />

            <button
              disabled={loading}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500 disabled:opacity-50"
            >
              {loading ? "Thinking..." : "Ask Copilot"}
            </button>
          </form>

          {response && (
            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-blue-400">
                Intent: {response.intent}
              </p>

              <h2 className="mt-3 text-xl font-semibold">Answer</h2>

              <p className="mt-3 leading-7 text-slate-300">
                {response.answer}
              </p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}