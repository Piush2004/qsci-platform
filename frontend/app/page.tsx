import Link from "next/link";

const PIPELINE = ["Data", "Forecast", "Risk", "Optimization", "Financial Impact", "Confidence", "Decision"];

export default function Home() {
  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center px-6 py-20">
      <p className="motion-rise-in mb-3 text-sm font-medium uppercase tracking-widest text-accent">
        Supply Chain Decision Intelligence
      </p>
      <h1 className="motion-rise-in text-display sm:text-5xl">
        Forecast is not a decision.
        <br />
        <span className="text-muted">From signals to intelligent decisions.</span>
      </h1>
      <p className="motion-rise-in mt-6 max-w-2xl text-body text-muted">
        QSCI connects demand data, forecasting, risk, optimization, financial impact, and confidence into a single
        evidence chain — every recommendation is inspectable, every number traceable back to a real computation.
      </p>

      <div className="motion-rise-in mt-10 flex flex-wrap items-center gap-2 text-sm">
        {PIPELINE.map((stage, i) => (
          <div key={stage} className="flex items-center gap-2">
            <span className="rounded-full border border-border bg-surface px-3 py-1.5 transition-colors duration-[var(--duration-fast)] hover:border-accent/50">
              {stage}
            </span>
            {i < PIPELINE.length - 1 && <span className="text-muted">→</span>}
          </div>
        ))}
      </div>

      <div className="motion-rise-in mt-10 flex gap-3">
        <Link
          href="/dashboard"
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-black transition-opacity duration-[var(--duration-fast)] hover:opacity-90"
        >
          Open Decision Center
        </Link>
        <Link
          href="/research"
          className="rounded-md border border-border px-4 py-2 text-sm font-medium transition-colors duration-[var(--duration-fast)] hover:bg-border/30"
        >
          Research Lab
        </Link>
      </div>

      <p className="motion-rise-in mt-10 max-w-2xl text-caption">
        Quantum computing is a research layer inside this pipeline, not the product&apos;s identity — QSCI evaluates
        whether quantum and quantum-inspired approaches provide measurable value for supply-chain forecasting and
        routing under realistic computational constraints. See the Research Lab for the evidence, including where
        quantum does <em>not</em> currently help.
      </p>
    </div>
  );
}
