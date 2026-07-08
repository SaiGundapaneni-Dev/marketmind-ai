import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 border-r border-slate-800 bg-slate-950 p-6 text-white lg:block">
      <h1 className="text-xl font-bold">MarketMind AI</h1>

      <nav className="mt-8 space-y-3 text-sm text-slate-400">
        <Link href="/" className="block rounded-xl bg-slate-900 px-4 py-3 text-white">
          Dashboard
        </Link>

        <Link href="/stock-search" className="block px-4 py-3 hover:text-white">
          Stock Search
        </Link>
		
		<Link href="/news" className="block px-4 py-3 hover:text-white">
			News
		</Link>
        <p className="px-4 py-3">IPO Analyzer</p>
        <p className="px-4 py-3">AI Copilot</p>
      </nav>
    </aside>
  );
}