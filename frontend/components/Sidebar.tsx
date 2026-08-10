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
  const [mobileOpen, setMobileOpen] = useState(false);

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
    setMobileOpen(false);
  }, [pathname]);

  if (!mounted) return null;

  return (
    <>
      <aside className="sticky top-0 hidden h-screen w-72 shrink-0 flex-col border-r border-white/10 bg-[#020817] p-6 text-white md:flex">
        <Brand />
        <Nav pathname={pathname} moreOpen={moreOpen} setMoreOpen={setMoreOpen} />
        <Account user={user} />
      </aside>

      <div className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-white/10 bg-[#020817]/95 px-4 backdrop-blur md:hidden">
        <Brand compact />
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300"
        >
          Menu
        </button>
      </div>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            aria-label="Close navigation"
            onClick={() => setMobileOpen(false)}
            className="absolute inset-0 bg-black/70"
          />

          <aside className="absolute right-0 top-0 flex h-full w-[86%] max-w-sm flex-col border-l border-white/10 bg-[#020817] p-6 text-white shadow-2xl">
            <div className="flex items-center justify-between">
              <Brand />
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-400"
              >
                Close
              </button>
            </div>

            <Nav pathname={pathname} moreOpen={moreOpen} setMoreOpen={setMoreOpen} />
            <Account user={user} />
          </aside>
        </div>
      )}
    </>
  );
}

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/dashboard" className="flex items-center gap-3">
      <div
        className={`flex items-center justify-center rounded-xl border border-white/10 bg-gradient-to-br from-[#3B82F6]/20 to-[#10B981]/20 font-black ${
          compact ? "h-9 w-9" : "h-11 w-11"
        }`}
      >
        V
      </div>

      <div>
        <p className="text-sm font-semibold tracking-[0.12em]">
          VESTORA <span className="text-[#10B981]">AI</span>
        </p>
        {!compact && (
          <p className="mt-1 text-[10px] uppercase tracking-[0.16em] text-slate-600">
            Investing Copilot
          </p>
        )}
      </div>
    </Link>
  );
}

function Nav({
  pathname,
  moreOpen,
  setMoreOpen,
}: {
  pathname: string;
  moreOpen: boolean;
  setMoreOpen: (value: boolean) => void;
}) {
  return (
    <nav className="mt-9 flex-1 overflow-y-auto">
      <div className="space-y-2">
        {primaryLinks.map((link) => (
          <NavLink key={link.href} {...link} pathname={pathname} />
        ))}
      </div>

      <div className="mt-7 border-t border-white/10 pt-5">
        <button
          type="button"
          onClick={() => setMoreOpen(!moreOpen)}
          className="flex w-full items-center justify-between rounded-xl px-4 py-3 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
        >
          <span>More</span>
          <span>{moreOpen ? "−" : "+"}</span>
        </button>

        {moreOpen && (
          <div className="mt-2 space-y-1 pl-2">
            {moreLinks.map((link) => (
              <NavLink
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
  );
}

function NavLink({
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
  const active = pathname.startsWith(href);

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 rounded-xl transition ${
        compact ? "px-4 py-2.5 text-xs" : "px-4 py-3 text-sm"
      } ${
        active
          ? "bg-[#3B82F6]/15 text-white"
          : "text-slate-400 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon && (
        <span
          className={`flex h-8 w-8 items-center justify-center rounded-lg ${
            active ? "bg-[#3B82F6]" : "bg-white/5"
          }`}
        >
          {icon}
        </span>
      )}
      <span className="font-medium">{label}</span>
    </Link>
  );
}

function Account({ user }: { user: StoredUser | null }) {
  return (
    <div className="mt-5 border-t border-white/10 pt-5">
      {user && (
        <div className="mb-3 rounded-2xl border border-white/10 bg-[#0F172A] p-4">
          <p className="truncate text-sm font-semibold">{user.name}</p>
          <p className="mt-1 truncate text-xs text-slate-500">{user.email}</p>
        </div>
      )}

      <Link
        href="/settings"
        className="mb-2 block rounded-xl px-4 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
      >
        Account settings
      </Link>

      <LogoutButton />
    </div>
  );
}
