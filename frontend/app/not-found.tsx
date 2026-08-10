import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#020817] px-5 text-center text-white">
      <div className="max-w-xl">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3B82F6]">
          404
        </p>
        <h1 className="mt-4 text-4xl font-semibold">
          This page isn&apos;t here.
        </h1>
        <p className="mt-4 leading-7 text-slate-400">
          The link may be outdated, or the page may have moved.
        </p>
        <Link
          href="/"
          className="mt-8 inline-block rounded-xl bg-[#3B82F6] px-5 py-3 text-sm font-semibold hover:bg-blue-500"
        >
          Go to Vestora
        </Link>
      </div>
    </main>
  );
}
