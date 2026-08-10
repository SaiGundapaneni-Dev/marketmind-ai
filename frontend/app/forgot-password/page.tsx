"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [devUrl, setDevUrl] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    setDevUrl("");

    try {
      const response = await fetch(`${apiBaseUrl}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Unable to start password reset.");
        return;
      }

      setMessage(data.message);
      if (data.dev_reset_url) setDevUrl(data.dev_reset_url);
    } catch (requestError) {
      console.error(requestError);
      setError("Unable to connect to Vestora AI.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#020817] px-5 text-white">
      <section className="w-full max-w-md rounded-[28px] border border-white/10 bg-[#0F172A] p-8">
        <Link href="/" className="font-semibold tracking-[0.14em]">
          VESTORA <span className="text-[#10B981]">AI</span>
        </Link>

        <p className="mt-8 text-xs font-semibold uppercase tracking-[0.18em] text-[#3B82F6]">
          Account recovery
        </p>
        <h1 className="mt-3 text-3xl font-semibold">Forgot your password?</h1>
        <p className="mt-3 text-sm leading-6 text-slate-400">
          Enter the email associated with your account.
        </p>

        <form onSubmit={submit} className="mt-8 space-y-5">
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full rounded-xl border border-white/10 bg-[#020817] px-4 py-3 outline-none focus:border-[#3B82F6]/70"
          />

          {message && (
            <div className="rounded-xl border border-[#10B981]/20 bg-[#10B981]/10 p-4 text-sm leading-6 text-emerald-200">
              {message}
              {devUrl && (
                <a href={devUrl} className="mt-3 block font-semibold underline">
                  Open development reset link
                </a>
              )}
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          <button
            disabled={loading}
            className="w-full rounded-xl bg-[#3B82F6] px-5 py-3.5 font-semibold hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Preparing..." : "Continue"}
          </button>
        </form>

        <Link href="/login" className="mt-7 block text-center text-sm text-slate-400">
          ← Back to sign in
        </Link>
      </section>
    </main>
  );
}
