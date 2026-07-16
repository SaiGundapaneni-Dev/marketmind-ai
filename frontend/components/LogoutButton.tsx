"use client";

import { useRouter } from "next/navigation";

import { removeToken } from "@/lib/auth";

export default function LogoutButton() {
  const router = useRouter();

  function logout() {
    removeToken();

    window.localStorage.removeItem(
      "vestora_user"
    );

    router.replace("/login");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={logout}
      className="w-full rounded-xl border border-red-500/30 px-4 py-3 text-left text-sm text-red-300 transition hover:bg-red-500/10"
    >
      Log out
    </button>
  );
}