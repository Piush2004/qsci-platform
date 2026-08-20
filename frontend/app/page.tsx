import Link from "next/link";

const PIPELINE = [
  "Data", "Quality", "Forecast", "Risk", "Optimization", "Financial Impact", "Confidence", "Recommendation",
  "Human Approval", "Audit", "Outcome",
];

const FLOW = ["Data", "Predict", "Optimize", "Quantify", "Explain", "Decide", "Learn"];

const EVIDENCE_LEGEND = [
  { label: "LIVE", color: "var(--live)", meaning: "computed from real data, right now" },
  { label: "RESEARCH", color: "var(--research)", meaning: "a real experiment, not yet production-integrated" },
  { label: "ILLUSTRATIVE", color: "var(--illustrative)", meaning: "a documented assumption standing in for data that doesn't exist" },
  { label: "PENDING", color: "var(--pending)", meaning: "not yet implemented or not yet run — said plainly" },
];

const FORECAST_ROW = [
  { model: "Seasonal Naive", wmape: "37.2%", note: "the honesty check", tone: "text-live" },
  { model: "LightGBM (full-history)", wmape: "25.6%", note: "production baseline", tone: "text-live" },
  { model: "VQR (quantum, leakage-corrected, N=4)", wmape: "34.9%", note: "research experiment", tone: "text-research" },
];

const ROUTING_ROW = [
  { method: "OR-Tools (on QUBO)", type: "Classical", cost: "380.01", runtime: "0.16s" },
  { method: "Simulated Annealing", type: "Quantum-inspired", cost: "380.01", runtime: "0.01s" },
  { method: "QAOA", type: "Quantum", cost: "380.01", runtime: "40.9s" },
];

function Section({ id, children, className = "" }: { id?: string; children: React.ReactNode; className?: string }) {
  return (
    <section id={id} className={`mx-auto max-w-5xl px-6 py-16 sm:py-20 ${className}`}>
      {children}
    </section>
  );
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return <p className="motion-rise-in mb-3 text-sm font-medium uppercase tracking-widest text-accent">{children}</p>;
}

function Pill({ label, color }: { label: string; color: string }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold uppercase tracking-wide"
      style={{ color, borderColor: `color-mix(in oklab, ${color} 40%, transparent)`, background: `color-mix(in oklab, ${color} 12%, transparent)` }}
    >
      {label}
    </span>
  );
}

export default function Home() {
  return (
    <>
      <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          <Link href="/" className="text-h3 tracking-wide">
            QSCI
          </Link>
          <Link
            href="/dashboard"
            className="rounded-md border border-border px-3 py-1.5 text-sm font-medium transition-colors duration-[var(--duration-fast)] hover:bg-border/30"
          >
            Open Decision Center
          </Link>
        </div>
      </header>
      <main className="min-h-screen">
      {/* 1. HERO */}
      <Section className="pb-12 pt-24 sm:pt-32">
        <Eyebrow>Quantum SupplyChain Intelligence</Eyebrow>
        <h1 className="motion-rise-in text-display sm:text-6xl">
          Forecast is not a decision.
          <br />
          <span className="text-muted">Decision Intelligence is.</span>
        </h1>
        <p className="motion-rise-in mt-6 max-w-2xl text-body text-muted sm:text-lg">
          From supply-chain signals to intelligent decisions — QSCI connects demand data, forecasting, risk,
          optimization, financial impact, and confidence into a single evidence chain. Every recommendation is
          inspectable, every number traceable back to a real computation.
        </p>
        <div className="motion-rise-in mt-10 flex flex-wrap gap-3">
          <Link
            href="/dashboard"
            className="rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-black transition-opacity duration-[var(--duration-fast)] hover:opacity-90"
          >
            Open Decision Center
          </Link>
          <Link
            href="/research"
            className="rounded-md border border-border px-5 py-2.5 text-sm font-medium transition-colors duration-[var(--duration-fast)] hover:bg-border/30"
          >
            See the Research Evidence
          </Link>
        </div>
        <div className="motion-rise-in mt-14 flex flex-wrap items-center gap-x-2 gap-y-3 text-sm">
          {FLOW.map((stage, i) => (
            <div key={stage} className="flex items-center gap-2">
              <span className="rounded-full border border-border bg-surface px-3 py-1.5 transition-colors duration-[var(--duration-fast)] hover:border-accent/50">
                {stage}
              </span>
              {i < FLOW.length - 1 && <span className="text-muted">→</span>}
            </div>
          ))}
        </div>
      </Section>

      {/* 2. PROBLEM */}
      <Section className="border-t border-border">
        <Eyebrow>The Problem</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">A forecast is a number. A decision has consequences.</h2>
        <p className="mt-4 max-w-3xl text-body text-muted">
          Most supply-chain tools stop at a demand prediction and call it intelligence. But a forecast alone
          doesn&apos;t tell you what to order, what it will cost, how confident to be, or what happens if the
          forecast is wrong. Better accuracy doesn&apos;t automatically mean a better business outcome — QSCI treats
          that gap as the actual research question, not an inconvenience to paper over.
        </p>
      </Section>

      {/* 3. DECISION CHAIN */}
      <Section className="border-t border-border">
        <Eyebrow>The Decision Chain</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">Every recommendation exposes its full evidence chain</h2>
        <p className="mt-4 max-w-3xl text-body text-muted">
          No stage is shown as complete without real backend evidence behind it. Click any recommendation in the
          Decision Center and inspect all eleven stages yourself.
        </p>
        <div className="mt-8 flex flex-wrap gap-2">
          {PIPELINE.map((stage) => (
            <span key={stage} className="rounded-md border border-border bg-surface px-3 py-2 text-sm">
              {stage}
            </span>
          ))}
        </div>
      </Section>

      {/* 4. REAL DATA EVIDENCE */}
      <Section className="border-t border-border">
        <Eyebrow>Real Data, Not Demo Data</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">Three verified, real-world datasets</h2>
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-lg border border-border bg-surface p-5">
            <p className="text-h3">M5 Forecasting — Accuracy</p>
            <p className="mt-2 text-supporting">
              ~30,490 series, 1,947 days (2011-01-29 → 2016-06-19). Real Walmart daily unit sales.
            </p>
            <div className="mt-3"><Pill label="LIVE" color="var(--live)" /></div>
          </div>
          <div className="rounded-lg border border-border bg-surface p-5">
            <p className="text-h3">CVRPLIB</p>
            <p className="mt-2 text-supporting">
              4 verified instances, published best-known route costs used as ground truth.
            </p>
            <div className="mt-3"><Pill label="LIVE" color="var(--live)" /></div>
          </div>
          <div className="rounded-lg border border-border bg-surface p-5">
            <p className="text-h3">Amazon Last-Mile</p>
            <p className="mt-2 text-supporting">
              6,112 real historical delivery routes, ~904,527 stops, 5 US metro areas.
            </p>
            <div className="mt-3"><Pill label="LIVE" color="var(--live)" /></div>
          </div>
        </div>
      </Section>

      {/* 5. CLASSICAL VS QUANTUM (FORECASTING) */}
      <Section className="border-t border-border">
        <Eyebrow>Classical vs. Quantum — Forecasting</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">Same data, same test window, no shortcuts</h2>
        <p className="mt-4 max-w-3xl text-body text-muted">
          RQ1/H1: classical production-grade models are expected to outperform current QML forecasting under
          realistic compute constraints. That is exactly what was measured.
        </p>
        <div className="mt-6 overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[520px] text-sm">
            <thead>
              <tr className="border-b border-border bg-surface text-left text-caption uppercase">
                <th className="px-4 py-3">Model</th>
                <th className="px-4 py-3">wMAPE</th>
                <th className="px-4 py-3">Role</th>
              </tr>
            </thead>
            <tbody>
              {FORECAST_ROW.map((r) => (
                <tr key={r.model} className="border-b border-border/50 last:border-0">
                  <td className="px-4 py-3">{r.model}</td>
                  <td className="px-4 py-3 text-data font-medium">{r.wmape}</td>
                  <td className={`px-4 py-3 ${r.tone}`}>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-caption">
          Diebold-Mariano test: not statistically significant at n=14 (insufficient statistical power, disclosed —
          not hidden). Full leakage audit, corrected results, and limitations in the Research Lab.
        </p>
      </Section>

      {/* 6. OPTIMIZATION */}
      <Section className="border-t border-border">
        <Eyebrow>Classical vs. Quantum-Inspired — Routing</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">The identical QUBO, three solvers, no winner declared</h2>
        <p className="mt-4 max-w-3xl text-body text-muted">
          OR-Tools-on-QUBO, simulated annealing, and QAOA all solved the exact same formulation — a genuinely fair
          comparison. (Native OR-Tools solves a different, non-QUBO problem — that methodological distinction is
          preserved everywhere in this product, never blurred for a cleaner-looking chart.)
        </p>
        <div className="mt-6 overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[480px] text-sm">
            <thead>
              <tr className="border-b border-border bg-surface text-left text-caption uppercase">
                <th className="px-4 py-3">Method</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Cost</th>
                <th className="px-4 py-3">Runtime</th>
              </tr>
            </thead>
            <tbody>
              {ROUTING_ROW.map((r) => (
                <tr key={r.method} className="border-b border-border/50 last:border-0">
                  <td className="px-4 py-3">{r.method}</td>
                  <td className="px-4 py-3 text-muted">{r.type}</td>
                  <td className="px-4 py-3 text-data font-medium">{r.cost}</td>
                  <td className="px-4 py-3 text-data">{r.runtime}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-caption">
          All three matched the same optimum when feasible at N=4. QAOA required real, measured quantum resources
          (8 qubits, circuit depth 34) and its runtime grew steeply with problem size — a real, reportable limit,
          not a hidden one.
        </p>
      </Section>

      {/* 7. FINANCIAL IMPACT */}
      <Section className="border-t border-border">
        <Eyebrow>Financial Impact</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">Real math, disclosed assumptions</h2>
        <p className="mt-4 max-w-3xl text-body text-muted">
          Holding cost, ordering cost, and stockout cost use standard, real operations-research formulas — that
          computation is LIVE. The per-unit dollar inputs feeding those formulas are ILLUSTRATIVE: no public dataset
          gives QSCI real per-unit cost data for M5 or Last-Mile items, so every dollar figure in this product is
          labeled accordingly and never rendered as a measured real-world saving.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Pill label="LIVE" color="var(--live)" />
          <span className="text-supporting">the formulas and the computation</span>
          <span className="mx-2 text-border">·</span>
          <Pill label="ILLUSTRATIVE" color="var(--illustrative)" />
          <span className="text-supporting">the dollar inputs</span>
        </div>
      </Section>

      {/* 8. EXPLAINABILITY */}
      <Section className="border-t border-border">
        <Eyebrow>Explainability</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">Confidence is never a bare percentage</h2>
        <p className="mt-4 max-w-3xl text-body text-muted">
          RQ5/H4: is multi-factor confidence a better reliability signal than accuracy alone? QSCI decomposes
          confidence into four independent components — Data Quality, Forecast Stability, Model Consensus, and
          Backtest Performance — and shows all four every time, never a single collapsed number. When a component is
          genuinely unavailable (VQR has no native quantile output, so it cannot produce Forecast Stability), the UI
          says <span className="text-pending font-medium">NOT AVAILABLE</span>, not a guessed value.
        </p>
      </Section>

      {/* 9. RESEARCH QUESTIONS */}
      <Section className="border-t border-border">
        <Eyebrow>Research Questions</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">What this project is actually testing</h2>
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {[
            ["RQ1 / H1", "Quantum vs. classical forecasting under identical conditions — classical is expected to win."],
            ["RQ2 / H2", "Does better forecast accuracy guarantee better inventory outcomes? Not necessarily."],
            ["RQ3", "What computational overhead does quantum encoding/execution add?"],
            ["RQ4 / H3", "Does forecasting + optimization + constraints beat forecasting alone?"],
            ["RQ5 / H4", "Is multi-factor confidence a better reliability signal than accuracy alone?"],
            ["RQ6 / H5", "At what problem size does quantum/quantum-inspired routing become competitive?"],
          ].map(([tag, text]) => (
            <div key={tag} className="rounded-lg border border-border bg-surface p-4">
              <p className="text-caption uppercase text-accent">{tag}</p>
              <p className="mt-1 text-sm text-foreground/90">{text}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* 10. ARCHITECTURE */}
      <Section className="border-t border-border">
        <Eyebrow>Architecture</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">One engine, two consumers</h2>
        <p className="mt-4 max-w-2xl text-body text-muted">
          Research notebooks and the production web app both import from the same <code className="text-data">qsci_core</code> package.
          The frontend never recreates a formula — it consumes real backend results.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4 text-sm">
          <span className="rounded-md border border-border bg-surface px-4 py-2">qsci_core</span>
          <span className="text-muted">→</span>
          <span className="rounded-md border border-border bg-surface px-4 py-2">FastAPI backend</span>
          <span className="text-muted">→</span>
          <span className="rounded-md border border-border bg-surface px-4 py-2">Next.js frontend</span>
        </div>
      </Section>

      {/* 11. EVIDENCE LABELS */}
      <Section className="border-t border-border">
        <Eyebrow>Evidence Standard</Eyebrow>
        <h2 className="text-h1 sm:text-3xl">Every number on this product carries one of four labels</h2>
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {EVIDENCE_LEGEND.map((e) => (
            <div key={e.label} className="flex items-start gap-3 rounded-lg border border-border bg-surface p-4">
              <Pill label={e.label} color={e.color} />
              <p className="text-sm text-muted">{e.meaning}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* 12. CTA */}
      <Section className="border-t border-border text-center">
        <h2 className="text-h1 sm:text-3xl">See the evidence yourself</h2>
        <p className="mx-auto mt-4 max-w-xl text-body text-muted">
          Open a live recommendation, inspect every stage of its evidence chain, and decide whether to approve,
          modify, or reject it — backed by the real engine, not a mockup.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link
            href="/dashboard"
            className="rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-black transition-opacity duration-[var(--duration-fast)] hover:opacity-90"
          >
            Open Decision Center
          </Link>
          <Link
            href="/research"
            className="rounded-md border border-border px-5 py-2.5 text-sm font-medium transition-colors duration-[var(--duration-fast)] hover:bg-border/30"
          >
            Research Lab
          </Link>
        </div>
      </Section>
      </main>
    </>
  );
}
