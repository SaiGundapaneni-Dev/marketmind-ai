"use client";

import { FormEvent, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { apiFetch } from "@/lib/api";

type User = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
};

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [profileMessage, setProfileMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const response = await apiFetch("/auth/me");
      if (!response.ok) {
        setError("Unable to load account.");
        return;
      }

      const data = (await response.json()) as User;
      setUser(data);
      setName(data.name);
      setEmail(data.email);
    }

    void load();
  }, []);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    setError("");
    setProfileMessage("");

    const response = await apiFetch("/auth/me", {
      method: "PUT",
      body: JSON.stringify({ name, email }),
    });

    const data = await response.json();

    if (!response.ok) {
      setError(data.detail || "Unable to update account.");
      return;
    }

    setUser(data);
    window.localStorage.setItem("vestora_user", JSON.stringify(data));
    setProfileMessage("Account details updated.");
  }

  async function changePassword(event: FormEvent) {
    event.preventDefault();
    setError("");
    setPasswordMessage("");

    const response = await apiFetch("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      setError(data.detail || "Unable to update password.");
      return;
    }

    setCurrentPassword("");
    setNewPassword("");
    setPasswordMessage(data.message || "Password updated.");
  }

  return (
    <main className="flex min-h-screen bg-[#020817] text-white">
      <Sidebar />

      <section className="min-w-0 flex-1 px-5 py-8 lg:px-10">
        <div className="mx-auto max-w-4xl">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3B82F6]">
            Account
          </p>
          <h1 className="mt-3 text-3xl font-semibold">Settings</h1>
          <p className="mt-3 text-slate-400">
            Manage your profile and account security.
          </p>

          {error && (
            <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <form
              onSubmit={saveProfile}
              className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6"
            >
              <h2 className="text-xl font-semibold">Profile</h2>
              <p className="mt-2 text-sm text-slate-500">
                Signed in as {user?.email || "..."}
              </p>

              <Field label="Name" type="text" value={name} onChange={setName} />
              <Field label="Email" type="email" value={email} onChange={setEmail} />

              {profileMessage && (
                <p className="mt-4 text-sm text-[#10B981]">{profileMessage}</p>
              )}

              <button className="mt-6 rounded-xl bg-[#3B82F6] px-5 py-3 text-sm font-semibold hover:bg-blue-500">
                Save profile
              </button>
            </form>

            <form
              onSubmit={changePassword}
              className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6"
            >
              <h2 className="text-xl font-semibold">Password</h2>
              <p className="mt-2 text-sm text-slate-500">
                Update your password without leaving your account.
              </p>

              <Field
                label="Current password"
                type="password"
                value={currentPassword}
                onChange={setCurrentPassword}
                minLength={1}
              />
              <Field
                label="New password"
                type="password"
                value={newPassword}
                onChange={setNewPassword}
                minLength={8}
              />

              {passwordMessage && (
                <p className="mt-4 text-sm text-[#10B981]">{passwordMessage}</p>
              )}

              <button className="mt-6 rounded-xl border border-white/10 px-5 py-3 text-sm font-semibold hover:border-[#3B82F6]/50">
                Update password
              </button>
            </form>
          </div>
        </div>
      </section>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  type,
  minLength,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type: string;
  minLength?: number;
}) {
  return (
    <label className="mt-5 block">
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
