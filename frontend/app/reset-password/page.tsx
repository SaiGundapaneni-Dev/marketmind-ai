"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [checking, setChecking] = useState(true);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setToken(params.get("token") || "");
    setChecking(false);
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    if (!token) {
      setError("This reset link is missing a token.");
      return;
    }

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Unable to reset password.");
        return;
      }

      setMessage(data.message || "Password reset successfully.");
      setPassword("");
      setConfirm("");
    } catch (requestError) {
      console.error(requestError);
      setError("Unable to connect to Vestora AI.");
    } finally {
      setLoading(false);
    }
  }

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020817] text-slate-400">
        Checking reset link...
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#020817] px-5 text-white">
      <section className="w-full max-w-md rounded-[28px] border border-white/10 bg-[#0F172A] p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#3B82F6]">
          Secure reset
        </p>
        <h1 className="mt-3 text-3xl font-semibold">Choose a new password</h1>
        <p className="mt-3 text-sm leading-6 text-slate-400">
          Use at least 8 characters.
        </p>

        <form onSubmit={submit} className="mt-8 space-y-5">
          <Password label="New password" value={password} onChange={setPassword} show={show} />
          <Password label="Confirm password" value={confirm} onChange={setConfirm} show={show} />

          <label className="flex items-center gap-2 text-sm text-slate-500">
            <input
              type="checkbox"
              checked={show}
              onChange={(e) => setShow(e.target.checked)}
            />
            Show passwords
          </label>

          {message && (
            <div className="rounded-xl border border-[#10B981]/20 bg-[#10B981]/10 p-4 text-sm text-emerald-200">
              {message}
              <Link href="/login" className="mt-2 block font-semibold underline">
                Sign in
              </Link>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !token}
            className="w-full rounded-xl bg-[#3B82F6] px-5 py-3.5 font-semibold hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Updating..." : "Reset password"}
          </button>
        </form>
      </section>
    </main>
  );
}

function Password({
  label,
  value,
  onChange,
  show,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  show: boolean;
}) {
  return (
    <label className="block">
      <span className="text-sm text-slate-300">{label}</span>
      <input
        type={show ? "text" : "password"}
        required
        minLength={8}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-2 w-full rounded-xl border border-white/10 bg-[#020817] px-4 py-3 outline-none focus:border-[#3B82F6]/70"
      />
    </label>
  );
}
