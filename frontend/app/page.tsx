import Sidebar from "@/components/Sidebar";
import SummaryCard from "@/components/SummaryCard";
import AllocationChart from "@/components/AllocationChart";
import AddHoldingForm from "@/components/AddHoldingForm";
import HoldingsTable, { Holding } from "@/components/HoldingsTable";

type PortfolioData = {
  summary: {
    total_cost: number;
    total_value: number;
    total_profit: number;
    total_return_percent: number;
  };
  holdings: Holding[];
};

async function getPortfolio(): Promise<PortfolioData | null> {
  try {
    const response = await fetch("http://127.0.0.1:8000/portfolio/", {
      cache: "no-store",
    });

    if (!response.ok) {
      return null;
    }

    return response.json();
  } catch {
    return null;
  }
}

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export default async function Home() {
  const portfolio = await getPortfolio();

  if (!portfolio) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
          <h1 className="text-2xl font-bold">MarketMind AI</h1>
          <p className="mt-3 text-slate-400">Unable to load portfolio data.</p>
          <p className="mt-1 text-sm text-slate-500">
            Make sure the FastAPI backend is running.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <section className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8">
            <p className="text-sm font-medium text-blue-400">USA Portfolio</p>
            <h1 className="mt-1 text-3xl font-bold">Portfolio Dashboard</h1>
            <p className="mt-2 text-slate-400">
              Track your US holdings, performance, and future AI insights.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <SummaryCard
              title="Total Value"
              value={`$${formatMoney(portfolio.summary.total_value)}`}
            />

            <SummaryCard
              title="Total Profit"
              value={`$${formatMoney(portfolio.summary.total_profit)}`}
            />

            <SummaryCard
              title="Total Return"
              value={`${portfolio.summary.total_return_percent.toFixed(2)}%`}
            />

            <SummaryCard
              title="Holdings"
              value={`${portfolio.holdings.length}`}
            />
          </div>
		<AddHoldingForm />
		<AllocationChart holdings={portfolio.holdings} />
          <HoldingsTable holdings={portfolio.holdings} />
        </div>
      </section>
    </main>
  );
}