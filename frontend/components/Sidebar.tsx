"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import LogoutButton from "@/components/LogoutButton";

type StoredUser = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
};

const primaryLinks = [
  { href: "/dashboard", label: "Home", icon: "⌂" },
  { href: "/intelligence", label: "Portfolio", icon: "▥" },
  { href: "/copilot", label: "Ask Vestora", icon: "✦" },
  { href: "/goals", label: "Goals", icon: "◎" },
  { href: "/watchlist", label: "Watchlist", icon: "☆" },
];

const moreLinks = [
  { href: "/daily-brief", label: "Daily Brief" },
  { href: "/scenario-simulator", label: "Scenario Simulator" },
  { href: "/stock-search", label: "Stock Search" },
  { href: "/news", label: "News" },
  { href: "/ipo-analyzer", label: "IPO Analyzer" },
  { href: "/watchtower", label: "Watchtower" },
];

export default function Sidebar() {
  const pathname = usePathname();

  const [mounted, setMounted] = useState(false);
  const [user, setUser] = useState<StoredUser | null>(null);
  const [moreOpen, setMoreOpen] = useState(false);

  useEffect(() => {
    setMounted(true);

    try {
      const stored = localStorage.getItem("vestora_user");
      setUser(stored ? (JSON.parse(stored) as StoredUser) : null);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    if (moreLinks.some((link) => pathname.startsWith(link.href))) {
      setMoreOpen(true);
    }
  }, [pathname]);

  if (!mounted) {
    return (
      <aside className="sticky top-0 hidden h-screen w-72 shrink-0 border-r border-white/10 bg-[#020817] p-6 text-white md:flex md:flex-col">
        <div className="flex h-full items-center justify-center">
          <p className="text-sm text-slate-500">Loading...</p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="sticky top-0 hidden h-screen w-72 shrink-0 border-r border-white/10 bg-[#020817] p-6 text-white md:flex md:flex-col">
      <div className="flex items-center gap-3">
        <div className="relative flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-[#0F172A]">
          <div className="absolute inset-0 bg-gradient-to-br from-[#3B82F6]/20 to-[#10B981]/20" />
          <span className="relative text-2xl font-black tracking-tighter">
            V
          </span>
        </div>

        <div>
          <h1 className="text-lg font-semibold tracking-[0.12em]">
            VESTORA
            <span className="ml-1 text-[#10B981]">AI</span>
          </h1>

          <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-500">
            Intelligent Investing Copilot
          </p>
        </div>
      </div>

      <nav className="mt-10 flex-1 overflow-y-auto">
        <div className="space-y-2">
          {primaryLinks.map((link) => (
            <SidebarLink
              key={link.href}
              href={link.href}
              label={link.label}
              icon={link.icon}
              pathname={pathname}
            />
          ))}
        </div>

        <div className="mt-8 border-t border-white/10 pt-6">
          <button
            type="button"
            onClick={() => setMoreOpen((value) => !value)}
            className="flex w-full items-center justify-between rounded-xl px-4 py-3 text-left text-sm text-slate-400 transition hover:bg-white/5 hover:text-white"
          >
            <span>More</span>
            <span className="text-base">{moreOpen ? "−" : "+"}</span>
          </button>

          {moreOpen && (
            <div className="mt-2 space-y-1 pl-3">
              {moreLinks.map((link) => (
                <SidebarLink
                  key={link.href}
                  href={link.href}
                  label={link.label}
                  pathname={pathname}
                  compact
                />
              ))}
            </div>
          )}
        </div>
      </nav>

      <div className="mt-6 border-t border-white/10 pt-5">
        {user && (
          <div className="mb-4 rounded-2xl border border-white/10 bg-[#0F172A] p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#3B82F6] to-[#10B981] text-sm font-bold">
                {user.name?.charAt(0)?.toUpperCase() || "U"}
              </div>

              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">
                  {user.name}
                </p>

                <p className="mt-1 truncate text-xs text-slate-500">
                  {user.email}
                </p>
              </div>
            </div>
          </div>
        )}

        <LogoutButton />
      </div>
    </aside>
  );
}

function SidebarLink({
  href,
  label,
  pathname,
  icon,
  compact = false,
}: {
  href: string;
  label: string;
  pathname: string;
  icon?: string;
  compact?: boolean;
}) {
  const isActive = pathname.startsWith(href);

  return (
    <Link
      href={href}
      className={`group flex items-center gap-3 rounded-xl transition ${
        compact ? "px-4 py-2.5 text-xs" : "px-4 py-3 text-sm"
      } ${
        isActive
          ? "bg-[#3B82F6]/15 text-white"
          : "text-slate-400 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon && (
        <span
          className={`flex h-8 w-8 items-center justify-center rounded-lg ${
            isActive
              ? "bg-[#3B82F6] text-white"
              : "bg-white/5 text-slate-500 group-hover:text-white"
          }`}
        >
          {icon}
        </span>
      )}

      <span className="font-medium">{label}</span>
    </Link>
  );
}
