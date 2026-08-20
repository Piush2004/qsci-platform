"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type AccuracyVsOutcome } from "@/lib/api";
import { StatusPill } from "@/components/StatusPill";
import { PageHeader } from "@/components/PageHeader";
import { Card } from "@/components/Card";
import { AccuracyOutcomeScatter } from "@/components/AccuracyOutcomeScatter";

type Json = Record<string, unknown>;

function Section({ title, status, children }: { title: string; status?: string; children: React.ReactNode }) {
  return (
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-h3">{title}</h2>
        {status && <StatusPill label={status} />}
      </div>
      {children}
    </Card>
  );
}

export default function ResearchPage() {
  const [benchmarks, setBenchmarks] = useState<Json | null>(null);
  const [scalability, setScalability] = useState<Json | null>(null);
  const [noise, setNoise] = useState<Json | null>(null);
  const [accuracyVsOutcome, setAccuracyVsOutcome] = useState<AccuracyVsOutcome | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.researchBenchmarks(), api.researchScalability(), api.researchNoise(), api.researchAccuracyVsOutcome(),
    ])
      .then(([b, s, n, a]) => {
        setBenchmarks(b);
        setScalability(s);
        setNoise(n);
        setAccuracyVsOutcome(a);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : "Backend unavailable"));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <PageHeader
        title="Research Lab"
        description="Evidence, not marketing. Classical vs. quantum, across forecasting, routing, noise, and scalability (Phases 2–5). No unqualified “quantum advantage” claim exists anywhere in this codebase."
      />

      {error && (
        <div className="mb-6 rounded-md border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
      )}

      <div className="space-y-6">
        <Section title="Master benchmark (Phase 5)" status={(benchmarks?.status as string) ?? "PENDING"}>
          <p className="mb-2 text-sm text-muted">{String(benchmarks?.note ?? "Loading…")}</p>
          {Array.isArray(benchmarks?.results) && (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <tbody>
                  {(benchmarks!.results as Json[]).slice(0, 12).map((row, i) => (
                    <tr key={i} className="border-t border-border/50">
                      {Object.entries(row).slice(0, 6).map(([k, v]) => (
                        <td key={k} className="whitespace-nowrap px-2 py-1">
                          {String(v)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Section>

        <Section title="QAOA depth tradeoff (Phase 4)" status={(scalability?.status as string) ?? "PENDING"}>
          <p className="text-sm text-muted">
            p=2/p=3 did not improve solution quality over p=1 on the evaluated instance, while runtime grew
            1.85–2.66x. &ldquo;Deeper is better&rdquo; is not supported by this evidence.
          </p>
          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-background/60 p-2 text-xs">
            {JSON.stringify(scalability?.qaoa_depth_tradeoff, null, 2)}
          </pre>
        </Section>

        <Section title="Noise sensitivity (Phase 4)" status="RESEARCH">
          <p className="text-sm text-muted">{String(noise?.caveat ?? "Loading…")}</p>
          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-background/60 p-2 text-xs">
            {JSON.stringify(noise?.noise_sensitivity, null, 2)}
          </pre>
        </Section>

        <Section title="Forecast accuracy vs. business outcome (RQ2/H2)" status={accuracyVsOutcome?.status ?? "PENDING"}>
          <p className="mb-2 text-sm text-muted">
            {accuracyVsOutcome?.note ?? "Loading…"}
          </p>
          {accuracyVsOutcome && accuracyVsOutcome.points.length >= 2 ? (
            <AccuracyOutcomeScatter points={accuracyVsOutcome.points} />
          ) : (
            <p className="text-sm text-pending">
              PENDING — paired business-outcome experiment. Run at least two forecast models (e.g. Seasonal Naive
              and LightGBM) on /demand for the same series to populate this chart.
            </p>
          )}
        </Section>

        <Section title="Known limitations" status="PENDING">
          <ul className="list-inside list-disc space-y-1 text-sm text-muted">
            <li>VQR cannot produce a forecast_stability signal (point forecaster, no native quantile output).</li>
            <li>QAOA statistics exist only at N=4 (8 qubits) — larger sizes hit a measured runtime wall.</li>
            <li>Annealing&apos;s feasibility collapse at N≥10 is a sampling artifact, recoverable with more reads.</li>
            <li>No real D-Wave QPU or quantum hardware was used anywhere in this project.</li>
          </ul>
        </Section>
      </div>
    </div>
  );
}
