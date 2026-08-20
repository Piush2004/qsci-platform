"use client";

const SERIES_COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24"];

interface Series {
  label: string;
  points: { x: number; y: number }[];
}

interface ScalabilityChartProps {
  title: string;
  xLabel: string;
  yLabel: string;
  series: Series[];
  yDomain?: [number, number];
}

/** A minimal, dependency-free SVG line chart -- deliberately not pulling
 * in a charting library for the small, bounded set of real series this
 * milestone needs (a charting-library decision is explicitly deferred to
 * Milestone 6 in docs/QSCI_PHASE_6_MASTER_PLAN.md). Every point plotted
 * is real data passed in by the caller; this component computes no
 * numbers of its own. */
export function ScalabilityChart({ title, xLabel, yLabel, series, yDomain }: ScalabilityChartProps) {
  const allX = series.flatMap((s) => s.points.map((p) => p.x));
  const allY = series.flatMap((s) => s.points.map((p) => p.y));
  const minX = Math.min(...allX), maxX = Math.max(...allX);
  const [minY, maxY] = yDomain ?? [Math.min(0, ...allY), Math.max(...allY)];

  const W = 560, H = 260, M = { top: 16, right: 16, bottom: 36, left: 48 };
  const plotW = W - M.left - M.right, plotH = H - M.top - M.bottom;

  const sx = (x: number) => M.left + ((x - minX) / Math.max(maxX - minX, 1)) * plotW;
  const sy = (y: number) => M.top + plotH - ((y - minY) / Math.max(maxY - minY, 1e-9)) * plotH;

  return (
    <div>
      <p className="mb-2 text-xs font-medium text-muted">{title}</p>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${title}: ${yLabel} vs. ${xLabel}`}>
        <line x1={M.left} y1={M.top} x2={M.left} y2={M.top + plotH} stroke="var(--border)" />
        <line x1={M.left} y1={M.top + plotH} x2={M.left + plotW} y2={M.top + plotH} stroke="var(--border)" />
        <text x={M.left + plotW / 2} y={H - 4} textAnchor="middle" fontSize="10" fill="var(--muted)">
          {xLabel}
        </text>
        <text x={12} y={M.top + plotH / 2} textAnchor="middle" fontSize="10" fill="var(--muted)" transform={`rotate(-90 12 ${M.top + plotH / 2})`}>
          {yLabel}
        </text>
        {series.map((s, si) => {
          const color = SERIES_COLORS[si % SERIES_COLORS.length];
          const sorted = [...s.points].sort((a, b) => a.x - b.x);
          return (
            <g key={s.label}>
              <polyline points={sorted.map((p) => `${sx(p.x)},${sy(p.y)}`).join(" ")} fill="none" stroke={color} strokeWidth={2} />
              {sorted.map((p, pi) => (
                <circle key={pi} cx={sx(p.x)} cy={sy(p.y)} r={3} fill={color}>
                  <title>{`${s.label}: ${xLabel}=${p.x}, ${yLabel}=${p.y}`}</title>
                </circle>
              ))}
            </g>
          );
        })}
      </svg>
      <div className="mt-2 flex flex-wrap gap-3 text-xs">
        {series.map((s, si) => (
          <span key={s.label} className="flex items-center gap-1.5">
            <span className="inline-block h-2 w-2 rounded-full" style={{ background: SERIES_COLORS[si % SERIES_COLORS.length] }} />
            {s.label}
          </span>
        ))}
      </div>
      <table className="sr-only">
        <caption>{title} (textual equivalent)</caption>
        <thead>
          <tr>
            <th>Series</th>
            <th>{xLabel}</th>
            <th>{yLabel}</th>
          </tr>
        </thead>
        <tbody>
          {series.flatMap((s) =>
            s.points.map((p, pi) => (
              <tr key={`${s.label}-${pi}`}>
                <td>{s.label}</td>
                <td>{p.x}</td>
                <td>{p.y}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
