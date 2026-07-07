type Holding = {
  asset_type: string;
  symbol: string;
  name: string;
  quantity: number;
  average_price: number;
  current_price: number;
  cost: number;
  current_value: number;
  profit: number;
  profit_percent: number;
};

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
    const response = await fetch(
      "http://127.0.0.1:8000/portfolio/",
      {
        cache: "no-store",
      }
    );

    if (!response.ok) {
      return null;
    }

    return response.json();
  } catch (error) {
    console.error("Portfolio API error:", error);
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
			<h1 className="text-2xl font-bold">
			  MarketMind AI
			</h1>

			<p className="mt-3 text-slate-400">
			  Unable to load portfolio data.
			</p>

			<p className="mt-1 text-sm text-slate-500">
			  Make sure the FastAPI backend is running.
			</p>
		  </div>
		</main>
	  );
	}

  return (
    <main className="min-h-screen bg-slate-950 text-white">

      <section className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}

        <div className="mb-8">
          <p className="text-sm font-medium text-blue-400">
            MarketMind AI
          </p>

          <h1 className="mt-1 text-3xl font-bold">
            Portfolio Dashboard
          </h1>

          <p className="mt-2 text-slate-400">
            Track holdings, performance, risk, and AI insights.
          </p>
        </div>


        {/* Summary Cards */}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Total Value
            </p>

            <h2 className="mt-2 text-2xl font-bold">
              ${formatMoney(portfolio.summary.total_value)}
            </h2>
          </div>


          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Total Profit
            </p>

            <h2 className="mt-2 text-2xl font-bold">
              ${formatMoney(portfolio.summary.total_profit)}
            </h2>
          </div>


          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Total Return
            </p>

            <h2 className="mt-2 text-2xl font-bold">
              {portfolio.summary.total_return_percent.toFixed(2)}%
            </h2>
          </div>


          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Holdings
            </p>

            <h2 className="mt-2 text-2xl font-bold">
              {portfolio.holdings.length}
            </h2>
          </div>

        </div>


        {/* Holdings Table */}

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">

          <div className="mb-5">
            <h2 className="text-xl font-semibold">
              Holdings
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Live portfolio holdings from the MarketMind API.
            </p>
          </div>


          <div className="overflow-x-auto">

            <table className="w-full min-w-[900px] text-left text-sm">

              <thead className="border-b border-slate-800 text-slate-400">

                <tr>
                  <th className="py-3 pr-4">
                    Symbol
                  </th>

                  <th className="py-3 pr-4">
                    Name
                  </th>

                  <th className="py-3 pr-4">
                    Asset
                  </th>

                  <th className="py-3 pr-4">
                    Qty
                  </th>

                  <th className="py-3 pr-4">
                    Avg Price
                  </th>

                  <th className="py-3 pr-4">
                    Current Price
                  </th>

                  <th className="py-3 pr-4">
                    Current Value
                  </th>

                  <th className="py-3 pr-4">
                    P/L
                  </th>

                  <th className="py-3">
                    P/L %
                  </th>
                </tr>

              </thead>


              <tbody>

                {portfolio.holdings.map((holding) => (

                  <tr
                    key={holding.symbol}
                    className="border-b border-slate-800 last:border-0"
                  >

                    <td className="py-4 pr-4 font-semibold">
                      {holding.symbol}
                    </td>

                    <td className="py-4 pr-4">
                      {holding.name}
                    </td>

                    <td className="py-4 pr-4">
                      {holding.asset_type}
                    </td>

                    <td className="py-4 pr-4">
                      {holding.quantity}
                    </td>

                    <td className="py-4 pr-4">
                      {formatMoney(holding.average_price)}
                    </td>

                    <td className="py-4 pr-4">
                      {formatMoney(holding.current_price)}
                    </td>

                    <td className="py-4 pr-4">
                      {formatMoney(holding.current_value)}
                    </td>

                    <td className="py-4 pr-4">
                      {formatMoney(holding.profit)}
                    </td>

                    <td className="py-4">
                      {holding.profit_percent.toFixed(2)}%
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </div>

      </section>

    </main>
  );
}