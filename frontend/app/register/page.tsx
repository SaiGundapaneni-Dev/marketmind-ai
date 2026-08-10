"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { saveToken } from "@/lib/auth";

type RegisterResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    name: string;
    email: string;
    is_active: boolean;
  };
};

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to create account."
        );
        return;
      }

      const result = data as RegisterResponse;
      saveToken(result.access_token);

      window.localStorage.setItem(
        "vestora_user",
        JSON.stringify(result.user)
      );

      router.replace("/dashboard");
      router.refresh();
    } catch (requestError) {
      console.error("Register error:", requestError);
      setError("Unable to connect to Vestora AI.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#020817] px-5 py-12 text-white">
      <section className="w-full max-w-md rounded-[28px] border border-white/10 bg-[#0F172A] p-8">
        <Link href="/" className="mx-auto block w-fit font-semibold tracking-[0.14em]">
          VESTORA <span className="text-[#10B981]">AI</span>
        </Link>

        <div className="mt-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#10B981]">
            Get started
          </p>
          <h1 className="mt-3 text-3xl font-semibold">
            Create your Vestora account
          </h1>
        </div>

        <form onSubmit={submit} className="mt-8 space-y-5">
          <Field label="Full name" type="text" value={name} onChange={setName} />
          <Field label="Email address" type="email" value={email} onChange={setEmail} />
          <Field
            label="Password"
            type={show ? "text" : "password"}
            value={password}
            onChange={setPassword}
            minLength={8}
          />
          <Field
            label="Confirm password"
            type={show ? "text" : "password"}
            value={confirm}
            onChange={setConfirm}
            minLength={8}
          />

          <label className="flex items-center gap-2 text-sm text-slate-500">
            <input
              type="checkbox"
              checked={show}
              onChange={(e) => setShow(e.target.checked)}
            />
            Show passwords
          </label>

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          <button
            disabled={loading}
            className="w-full rounded-xl bg-[#3B82F6] px-5 py-3.5 font-semibold hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-7 text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link href="/login" className="font-semibold text-[#3B82F6]">
            Sign in
          </Link>
        </p>

        <p className="mt-5 text-center text-xs leading-5 text-slate-600">
          By creating an account, you agree to our{" "}
          <Link href="/terms" className="underline">Terms</Link>{" "}
          and{" "}
          <Link href="/privacy" className="underline">Privacy Policy</Link>.
        </p>
      </section>
    </main>
  );
}

function Field({
  label,
  type,
  value,
  onChange,
  minLength,
}: {
  label: string;
  type: string;
  value: string;
  onChange: (value: string) => void;
  minLength?: number;
}) {
  return (
    <label className="block">
      <span className="text-sm text-slate-300">{label}</span>
      <input
        type={type}
        required
        minLength={minLength}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-2 w-full rounded-xl border border-white/10 bg-[#020817] px-4 py-3 outline-none focus:border-[#3B82F6]/70"
      />
    </label>
  );
}
