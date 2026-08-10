import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-[#020817] px-5 py-12 text-white">
      <div className="mx-auto max-w-3xl">
        <Link href="/" className="text-sm font-semibold tracking-[0.14em]">
          VESTORA <span className="text-[#10B981]">AI</span>
        </Link>

        <h1 className="mt-10 text-4xl font-semibold">Privacy Policy</h1>
        <p className="mt-2 text-sm text-slate-600">Last updated August 10, 2026</p>

        <article className="mt-10 space-y-6 leading-7 text-slate-400 [&_h2]:pt-4 [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:text-white">
          <p>
            Vestora AI is designed to provide private portfolio intelligence.
            This policy describes the categories of information the service may
            process and the purposes for which that information is used.
          </p>

          <h2>Information you provide</h2>
          <p>
            This can include your name, email address, account credentials,
            portfolio holdings, investment goals, watchlist entries, investment
            theses, and questions submitted to Vestora.
          </p>

          <h2>How information is used</h2>
          <p>
            Information is used to authenticate your account, operate portfolio
            features, generate requested insights, maintain application security,
            and improve reliability.
          </p>

          <h2>Financial accounts</h2>
          <p>
            Vestora does not ask for your brokerage password in the current
            product. Portfolio positions you enter are stored as part of your
            private Vestora account.
          </p>

          <h2>Service providers</h2>
          <p>
            Vestora may rely on infrastructure and data providers to host the
            application, store data, deliver email, and provide market data.
          </p>

          <h2>Security</h2>
          <p>
            Reasonable technical safeguards are used, but no online service can
            guarantee absolute security. Use a unique password and protect access
            to your account.
          </p>

          <h2>Your choices</h2>
          <p>
            You can update account details from Settings. Additional data export
            and deletion controls should be added before broad commercial launch.
          </p>

          <h2>Pre-launch notice</h2>
          <p>
            This is an initial product policy draft and should be reviewed by
            qualified counsel before a broad commercial launch.
          </p>
        </article>
      </div>
    </main>
  );
}
