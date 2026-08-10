"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { saveToken } from "@/lib/auth";

type LoginResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    name: string;
    email: string;
    is_active: boolean;
  };
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to sign in."
        );
        return;
      }

      const loginData = data as LoginResponse;
      saveToken(loginData.access_token);

      window.localStorage.setItem(
        "vestora_user",
        JSON.stringify(loginData.user)
      );

      router.replace("/dashboard");
      router.refresh();
    } catch (requestError) {
      console.error("Login error:", requestError);
      setError("Unable to connect to Vestora AI.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#020817] px-5 py-12 text-white">
      <div className="pointer-events-none absolute left-1/2 top-0 h-[440px] w-[760px] -translate-x-1/2 rounded-full bg-[#3B82F6]/10 blur-[120px]" />

      <section className="relative w-full max-w-md rounded-[28px] border border-white/10 bg-[#0F172A] p-8 shadow-2xl shadow-black/30">
        <Brand />

        <div className="mt-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#3B82F6]">
            Welcome back
          </p>
          <h1 className="mt-3 text-3xl font-semibold">Sign in to Vestora</h1>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            Your portfolio intelligence, goals and investment context are private to your account.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <label className="block">
            <span className="text-sm text-slate-300">Email address</span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-2 w-full rounded-xl border border-white/10 bg-[#020817] px-4 py-3 outline-none focus:border-[#3B82F6]/70"
            />
          </label>

          <label className="block">
            <span className="text-sm text-slate-300">Password</span>
            <div className="relative mt-2">
              <input
                type={showPassword ? "text" : "password"}
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-[#020817] px-4 py-3 pr-16 outline-none focus:border-[#3B82F6]/70"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 px-4 text-xs text-slate-500 hover:text-white"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </label>

          <div className="flex justify-end">
            <Link
              href="/forgot-password"
              className="text-sm font-medium text-[#3B82F6] hover:text-blue-300"
            >
              Forgot password?
            </Link>
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-[#3B82F6] px-5 py-3.5 font-semibold hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="mt-7 text-center text-sm text-slate-400">
          New to Vestora?{" "}
          <Link href="/register" className="font-semibold text-[#3B82F6]">
            Create an account
          </Link>
        </p>
      </section>
    </main>
  );
}

function Brand() {
  return (
    <Link href="/" className="mx-auto flex w-fit items-center gap-3">
      <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-gradient-to-br from-[#3B82F6]/20 to-[#10B981]/20 text-xl font-black">
        V
      </div>
      <div>
        <p className="font-semibold tracking-[0.14em]">
          VESTORA <span className="text-[#10B981]">AI</span>
        </p>
        <p className="text-[10px] uppercase tracking-[0.16em] text-slate-500">
          Investing Copilot
        </p>
      </div>
    </Link>
  );
}
