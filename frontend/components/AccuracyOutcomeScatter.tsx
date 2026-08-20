"use client";

import type { AccuracyOutcomePoint } from "@/lib/api";

const POINT_COLORS: Record<string, string> = {
  LIVE: "#34d399",
  RESEARCH: "#a78bfa",
};

/** Step 4: "accuracy does not automatically equal business value." A
 * scatter, not a line -- there is no ordering relationship between models
 * that would make connecting them meaningful, and a line would visually
 * imply a trend the data doesn't support. Each point is one real model's
 * (wMAPE, total_cost) pair; never interpolated or synthesized. */
export function AccuracyOutcomeScatter({ points }: { points: AccuracyOutcomePoint[] }) {
  const W = 560, H = 280, M = { top: 16, right: 16, bottom: 40, left: 56 };
  const plotW = W - M.left - M.right, plotH = H - M.top - M.bottom;

  const costs = points.map((p) => p.total_cost).filter((c): c is number => c !== null);
  const wmapes = points.map((p) => p.wmape);
  const minX = Math.min(...wmapes), maxX = Math.max(...wmapes);
  const minY = Math.min(0, ...costs), maxY = Math.max(...costs, 1);

  const sx = (x: number) => M.left + ((x - minX) / Math.max(maxX - minX, 1)) * plotW;
  const sy = (y: number) => M.top + plotH - ((y - minY) / Math.max(maxY - minY, 1e-9)) * plotH;

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Forecast accuracy (wMAPE) vs. financial impact (total cost) per model">
        <line x1={M.left} y1={M.top} x2={M.left} y2={M.top + plotH} stroke="var(--border)" />
        <line x1={M.left} y1={M.top + plotH} x2={M.left + plotW} y2={M.top + plotH} stroke="var(--border)" />
        <text x={M.left + plotW / 2} y={H - 6} textAnchor="middle" fontSize="10" fill="var(--muted)">
          wMAPE (%) — lower is more accurate
        </text>
        <text x={14} y={M.top + plotH / 2} textAnchor="middle" fontSize="10" fill="var(--muted)" transform={`rotate(-90 14 ${M.top + plotH / 2})`}>
          Total inventory cost ($/yr, ILLUSTRATIVE)
        </text>
        {points.map((p) => {
          if (p.total_cost === null) return null;
          const cx = sx(p.wmape);
          const nearRightEdge = cx > M.left + plotW - 60;
          return (
            <g key={p.model}>
              <circle cx={cx} cy={sy(p.total_cost)} r={6} fill={POINT_COLORS[p.label] ?? "#94a3b8"}>
                <title>{`${p.model}: wMAPE=${p.wmape.toFixed(1)}%, total_cost=$${p.total_cost.toFixed(0)}`}</title>
              </circle>
              <text
                x={nearRightEdge ? cx - 9 : cx + 9}
                y={sy(p.total_cost) + 4}
                fontSize="10"
                fill="var(--foreground)"
                textAnchor={nearRightEdge ? "end" : "start"}
              >
                {p.model}
              </text>
            </g>
          );
        })}
      </svg>
      {/* sr-only on a wrapping div, not the table itself -- see ScalabilityChart. */}
      <div className="sr-only">
        <table>
          <caption>Forecast accuracy vs. financial impact per model (textual equivalent)</caption>
          <thead>
            <tr>
              <th>Model</th>
              <th>wMAPE (%)</th>
              <th>Total cost ($/yr)</th>
              <th>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p) => (
              <tr key={p.model}>
                <td>{p.model}</td>
                <td>{p.wmape}</td>
                <td>{p.total_cost ?? "N/A"}</td>
                <td>{p.label}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
