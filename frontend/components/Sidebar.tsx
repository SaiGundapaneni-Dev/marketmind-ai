"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  useEffect,
  useState,
} from "react";

import LogoutButton from "@/components/LogoutButton";

type StoredUser = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
};

const links = [
  { href: "/", label: "Dashboard" },
  {
    href: "/daily-brief",
    label: "Daily Brief",
  },
  {
    href: "/intelligence",
    label: "Portfolio Intelligence",
  },
  {
    href: "/stock-search",
    label: "Stock Search",
  },
  {
    href: "/watchlist",
    label: "AI Watchlist",
  },
  { href: "/news", label: "News" },
  {
    href: "/ipo-analyzer",
    label: "IPO Analyzer",
  },
  {
    href: "/copilot",
    label: "AI Copilot",
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  const [mounted, setMounted] =
    useState(false);

  const [user, setUser] =
    useState<StoredUser | null>(null);

  useEffect(() => {
    setMounted(true);

    try {
      const stored =
        localStorage.getItem("vestora_user");

      if (!stored) {
        setUser(null);
        return;
      }

      const parsedUser =
        JSON.parse(stored) as StoredUser;

      setUser(parsedUser);
    } catch {
      setUser(null);
    }
  }, []);

  if (!mounted) {
    return (
      <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-slate-800 bg-slate-950 p-6 text-white">
        <div className="flex h-full items-center justify-center">
          <p className="text-sm text-slate-500">
            Loading...
          </p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-slate-800 bg-slate-950 p-6 text-white">
      <div>
        <h1 className="text-xl font-bold">
          Vestora AI
        </h1>

        <p className="mt-1 text-xs text-slate-500">
          Investment Intelligence
        </p>
      </div>

      <nav className="mt-8 flex-1 space-y-2 overflow-y-auto text-sm">
        {links.map((link) => {
          const isActive =
            link.href === "/"
              ? pathname === "/"
              : pathname.startsWith(
                  link.href
                );

          return (
            <Link
              key={link.href}
              href={link.href}
              className={`block rounded-xl px-4 py-3 transition ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:bg-slate-900 hover:text-white"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-6 border-t border-slate-800 pt-5">
        {user && (
          <div className="mb-4 rounded-xl bg-slate-900 p-4">
            <p className="truncate text-sm font-semibold text-white">
              {user.name}
            </p>

            <p className="mt-1 truncate text-xs text-slate-400">
              {user.email}
            </p>
          </div>
        )}

        <LogoutButton />
      </div>
    </aside>
  );
}