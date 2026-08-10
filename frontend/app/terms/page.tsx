import Link from "next/link";

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-[#020817] px-5 py-12 text-white">
      <div className="mx-auto max-w-3xl">
        <Link href="/" className="text-sm font-semibold tracking-[0.14em]">
          VESTORA <span className="text-[#10B981]">AI</span>
        </Link>

        <h1 className="mt-10 text-4xl font-semibold">Terms of Service</h1>
        <p className="mt-2 text-sm text-slate-600">Last updated August 10, 2026</p>

        <article className="mt-10 space-y-6 leading-7 text-slate-400 [&_h2]:pt-4 [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:text-white">
          <p>
            These terms govern use of Vestora AI. By creating an account, you
            agree to use the service lawfully and to provide accurate account
            information.
          </p>

          <h2>Informational service</h2>
          <p>
            Vestora provides portfolio analytics, market information and
            AI-generated explanations for informational purposes. Vestora is not
            a broker, investment adviser, tax adviser, or legal adviser, and the
            service does not provide personalized financial advice.
          </p>

          <h2>Your decisions</h2>
          <p>
            Investment decisions remain your responsibility. Market data and
            generated analysis can be delayed, incomplete, or incorrect.
          </p>

          <h2>Your account</h2>
          <p>
            You are responsible for maintaining the confidentiality of your
            credentials and for activity under your account.
          </p>

          <h2>Acceptable use</h2>
          <p>
            You may not misuse the service, interfere with its operation, attempt
            unauthorized access, or use it to violate applicable law.
          </p>

          <h2>Availability</h2>
          <p>
            Features may change, be suspended, or be discontinued as the product
            evolves. Vestora does not guarantee uninterrupted service.
          </p>

          <h2>Pre-launch notice</h2>
          <p>
            These terms are an initial product draft and should be reviewed by
            qualified counsel before broad commercial launch.
          </p>
        </article>
      </div>
    </main>
  );
}
