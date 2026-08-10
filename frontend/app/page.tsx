import Link from "next/link";

const features = [
  {
    eyebrow: "UNDERSTAND",
    title: "Know how your portfolio is doing.",
    text: "Vestora brings your holdings, performance, allocation and portfolio context into one clear view.",
  },
  {
    eyebrow: "FILTER",
    title: "Ignore the market noise.",
    text: "Instead of showing every headline and every metric, Vestora focuses on changes that can actually matter to what you own.",
  },
  {
    eyebrow: "EXPLAIN",
    title: "Understand why it matters.",
    text: "Portfolio risks and market events are translated into plain English instead of another dashboard full of scores.",
  },
  {
    eyebrow: "DECIDE",
    title: "Know what deserves attention.",
    text: "Vestora gives you a focused next step: monitor, review your thesis, reconsider concentration, or simply do nothing.",
  },
];

const capabilities = [
  "Portfolio monitoring",
  "Plain-English portfolio health",
  "Material event filtering",
  "Investment thesis tracking",
  "Goal-based investing",
  "Scenario stress testing",
  "Watchlist intelligence",
  "Ask Vestora",
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#020817] text-white">
      <header className="relative z-20 border-b border-white/10">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-5 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <BrandMark />

            <div>
              <p className="text-sm font-semibold tracking-[0.14em]">
                VESTORA <span className="text-[#10B981]">AI</span>
              </p>
              <p className="mt-0.5 hidden text-[10px] uppercase tracking-[0.18em] text-slate-500 sm:block">
                Intelligent Investing Copilot
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-8 text-sm text-slate-400 md:flex">
            <a href="#how-it-works" className="transition hover:text-white">
              How it works
            </a>
            <a href="#features" className="transition hover:text-white">
              Features
            </a>
            <a href="#why-vestora" className="transition hover:text-white">
              Why Vestora
            </a>
          </nav>

          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/login"
              className="rounded-xl px-3 py-2 text-sm font-medium text-slate-300 transition hover:text-white sm:px-4"
            >
              Sign in
            </Link>

            <Link
              href="/register"
              className="rounded-xl bg-[#3B82F6] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      <section className="relative">
        <div className="pointer-events-none absolute left-1/2 top-0 h-[520px] w-[900px] -translate-x-1/2 rounded-full bg-[#3B82F6]/10 blur-[130px]" />
        <div className="pointer-events-none absolute right-[-180px] top-24 h-[420px] w-[420px] rounded-full bg-[#10B981]/10 blur-[130px]" />

        <div className="relative mx-auto grid max-w-7xl gap-14 px-5 pb-20 pt-20 lg:grid-cols-[1.02fr_0.98fr] lg:px-8 lg:pb-28 lg:pt-28">
          <div className="flex flex-col justify-center">
            <div className="inline-flex w-fit items-center gap-2 rounded-full border border-[#10B981]/20 bg-[#10B981]/10 px-3 py-1.5">
              <span className="h-2 w-2 rounded-full bg-[#10B981]" />
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-200">
                Portfolio clarity without the noise
              </span>
            </div>

            <h1 className="mt-7 max-w-3xl text-5xl font-semibold leading-[1.05] tracking-[-0.04em] sm:text-6xl lg:text-7xl">
              Investing clarity,
              <span className="block bg-gradient-to-r from-[#3B82F6] to-[#10B981] bg-clip-text text-transparent">
                without the overload.
              </span>
            </h1>

            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-400">
              Vestora watches your portfolio, explains what changed,
              tells you why it matters, and helps you understand what
              deserves your attention.
            </p>

            <div className="mt-9 flex flex-wrap gap-3">
              <Link
                href="/register"
                className="rounded-xl bg-[#3B82F6] px-6 py-3.5 text-sm font-semibold transition hover:bg-blue-500"
              >
                Create free account
              </Link>

              <a
                href="#how-it-works"
                className="rounded-xl border border-white/10 bg-white/[0.03] px-6 py-3.5 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:bg-white/[0.06]"
              >
                See how it works
              </a>
            </div>

            <p className="mt-5 text-xs text-slate-600">
              Built for investors who want better decisions, not more dashboards.
            </p>
          </div>

          <ProductPreview />
        </div>
      </section>

      <section
        id="why-vestora"
        className="border-y border-white/10 bg-white/[0.015]"
      >
        <div className="mx-auto max-w-7xl px-5 py-20 lg:px-8 lg:py-24">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#10B981]">
              Why Vestora
            </p>

            <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
              Not another dashboard full of scores.
            </h2>

            <p className="mt-5 text-lg leading-8 text-slate-400">
              Financial platforms are very good at giving investors more
              information. Vestora is designed to reduce that information
              into a simpler question: <span className="text-white">what actually matters to my portfolio?</span>
            </p>
          </div>

          <div className="mt-12 grid gap-4 md:grid-cols-3">
            <ProblemCard
              number="01"
              title="What happened?"
              text="See the portfolio change that actually deserves your attention."
            />
            <ProblemCard
              number="02"
              title="Why does it matter?"
              text="Understand the impact in the context of your holdings and portfolio."
            />
            <ProblemCard
              number="03"
              title="What should I consider?"
              text="Get a clear review point without being told to trade on every market move."
            />
          </div>
        </div>
      </section>

      <section
        id="how-it-works"
        className="mx-auto max-w-7xl px-5 py-20 lg:px-8 lg:py-28"
      >
        <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3B82F6]">
              How it works
            </p>

            <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
              Four layers.
              <span className="block text-slate-500">
                One clear experience.
              </span>
            </h2>

            <p className="mt-5 max-w-md leading-7 text-slate-400">
              Vestora keeps the analytics underneath the product and shows
              you the conclusion first. Deeper analysis is there when you
              want it.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {features.map((feature) => (
              <article
                key={feature.eyebrow}
                className="rounded-[24px] border border-white/10 bg-[#0F172A] p-6"
              >
                <p className="text-[11px] font-semibold tracking-[0.18em] text-[#3B82F6]">
                  {feature.eyebrow}
                </p>

                <h3 className="mt-4 text-xl font-semibold">
                  {feature.title}
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {feature.text}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="relative border-y border-white/10">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#0F172A]/50 to-transparent" />

        <div className="relative mx-auto max-w-7xl px-5 py-20 lg:px-8 lg:py-24">
          <div className="grid gap-12 lg:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#10B981]">
                Built around your portfolio
              </p>

              <h2 className="mt-4 max-w-xl text-3xl font-semibold tracking-tight sm:text-4xl">
                Intelligence that starts with what you own.
              </h2>

              <p className="mt-5 max-w-xl leading-7 text-slate-400">
                Vestora combines portfolio monitoring, context and AI into
                one private workspace designed for long-term investors.
              </p>

              <div className="mt-8 grid gap-3 sm:grid-cols-2">
                {capabilities.map((capability) => (
                  <div
                    key={capability}
                    className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.025] px-4 py-3"
                  >
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#10B981]/10 text-xs text-[#10B981]">
                      ✓
                    </span>
                    <span className="text-sm text-slate-300">
                      {capability}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <DailyExperience />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-5 py-24 text-center lg:py-32">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3B82F6]">
          Your portfolio. Less noise.
        </p>

        <h2 className="mx-auto mt-5 max-w-3xl text-4xl font-semibold tracking-[-0.03em] sm:text-5xl">
          Stop checking ten different signals to understand one portfolio.
        </h2>

        <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-400">
          Let Vestora surface what deserves your attention and keep the
          deeper analysis available when you need it.
        </p>

        <div className="mt-9 flex justify-center gap-3">
          <Link
            href="/register"
            className="rounded-xl bg-[#3B82F6] px-6 py-3.5 text-sm font-semibold transition hover:bg-blue-500"
          >
            Get started
          </Link>

          <Link
            href="/login"
            className="rounded-xl border border-white/10 px-6 py-3.5 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:text-white"
          >
            Sign in
          </Link>
        </div>
      </section>

      <footer className="border-t border-white/10">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <BrandMark small />
            <span>Vestora AI</span>
          </div>

          <p>
            Informational portfolio intelligence. Not personalized financial advice.
          </p>
        </div>
      </footer>
    </main>
  );
}

function BrandMark({ small = false }: { small?: boolean }) {
  return (
    <div
      className={`relative flex shrink-0 items-center justify-center overflow-hidden border border-white/10 bg-[#0F172A] ${
        small ? "h-8 w-8 rounded-lg" : "h-11 w-11 rounded-xl"
      }`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-[#3B82F6]/25 to-[#10B981]/25" />
      <span className={`relative font-black ${small ? "text-sm" : "text-xl"}`}>
        V
      </span>
    </div>
  );
}

function ProductPreview() {
  return (
    <div className="relative mx-auto w-full max-w-xl">
      <div className="absolute -inset-6 rounded-[40px] bg-gradient-to-br from-[#3B82F6]/10 to-[#10B981]/10 blur-2xl" />

      <div className="relative rounded-[28px] border border-white/10 bg-[#081120]/95 p-3 shadow-2xl shadow-black/40">
        <div className="rounded-[22px] border border-white/10 bg-[#0F172A] p-5 sm:p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs text-slate-500">Your portfolio</p>
              <p className="mt-1 text-3xl font-semibold">$24,860</p>
            </div>

            <div className="rounded-xl border border-[#10B981]/20 bg-[#10B981]/10 px-3 py-2 text-right">
              <p className="text-xs text-slate-500">Return</p>
              <p className="mt-1 text-sm font-semibold text-[#10B981]">
                +8.5%
              </p>
            </div>
          </div>

          <div className="mt-8 h-36 rounded-2xl border border-white/5 bg-[#020817]/70 p-4">
            <svg
              viewBox="0 0 500 120"
              className="h-full w-full"
              role="img"
              aria-label="Illustrative portfolio growth chart"
            >
              <defs>
                <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#3B82F6" />
                  <stop offset="100%" stopColor="#10B981" />
                </linearGradient>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.22" />
                  <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
                </linearGradient>
              </defs>

              <path
                d="M0 96 C40 88 65 92 100 78 C135 64 165 76 200 58 C240 37 260 52 300 38 C340 22 365 42 400 26 C435 10 466 24 500 8 L500 120 L0 120 Z"
                fill="url(#areaGradient)"
              />

              <path
                d="M0 96 C40 88 65 92 100 78 C135 64 165 76 200 58 C240 37 260 52 300 38 C340 22 365 42 400 26 C435 10 466 24 500 8"
                fill="none"
                stroke="url(#lineGradient)"
                strokeWidth="4"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <div className="mt-5 rounded-2xl border border-[#10B981]/20 bg-[#10B981]/[0.07] p-4">
            <div className="flex gap-3">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#10B981]/10 text-xs text-[#10B981]">
                ✓
              </span>

              <div>
                <p className="text-sm font-semibold">
                  Nothing urgent today
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-400">
                  No material event currently changes your portfolio outlook.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-3 rounded-2xl border border-[#F59E0B]/20 bg-[#F59E0B]/[0.06] p-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#F59E0B]">
              One thing to watch
            </p>
            <p className="mt-2 text-sm font-semibold">
              NVDA is becoming a large position.
            </p>
            <p className="mt-1 text-xs leading-5 text-slate-400">
              Review concentration before adding more.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProblemCard({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <article className="rounded-[24px] border border-white/10 bg-[#0F172A] p-6">
      <p className="text-xs font-semibold text-[#3B82F6]">{number}</p>
      <h3 className="mt-5 text-xl font-semibold">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-400">{text}</p>
    </article>
  );
}

function DailyExperience() {
  return (
    <div className="rounded-[28px] border border-white/10 bg-[#0F172A] p-6 lg:p-7">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#3B82F6]">
        A typical Vestora morning
      </p>

      <div className="mt-7 border-b border-white/10 pb-6">
        <p className="text-sm text-slate-500">Portfolio value</p>
        <div className="mt-2 flex flex-wrap items-end gap-3">
          <p className="text-4xl font-semibold">$24,860</p>
          <p className="pb-1 text-sm font-semibold text-[#10B981]">
            +8.5%
          </p>
        </div>
      </div>

      <div className="py-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#10B981]">
          Today
        </p>
        <p className="mt-3 text-xl font-semibold">
          Nothing urgent requires your attention.
        </p>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          Normal market movement. Your investment cases remain intact.
        </p>
      </div>

      <div className="border-t border-white/10 pt-6">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#F59E0B]">
          One thing to watch
        </p>
        <p className="mt-3 text-xl font-semibold">
          NVDA is 27% of your portfolio.
        </p>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          You do not need to sell, but consider other investments before adding more.
        </p>
      </div>
    </div>
  );
}
