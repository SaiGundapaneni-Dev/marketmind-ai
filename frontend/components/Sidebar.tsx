import Link from "next/link";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/stock-search", label: "Stock Search" },
  { href: "/watchlist", label: "AI Watchlist" },
  { href: "/news", label: "News" },
  { href: "/ipo-analyzer", label: "IPO Analyzer" },
  { href: "/copilot", label: "AI Copilot" },
];

export default function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 border-r border-slate-800 bg-slate-950 p-6 text-white lg:block">
      <h1 className="text-xl font-bold">MarketMind AI</h1>

      <nav className="mt-8 space-y-3 text-sm text-slate-400">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="block rounded-xl px-4 py-3 transition hover:bg-slate-900 hover:text-white"
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
