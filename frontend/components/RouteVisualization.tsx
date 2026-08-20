"use client";

import { useState } from "react";

const ROUTE_COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f87171", "#60a5fa"];

interface RouteVisualizationProps {
  depot: [number, number];
  nodes: [number, number][]; // customer coordinates, 0-indexed
  routes: number[][]; // each inner array: 0-indexed customer indices into `nodes`, in visit order
}

/** Real Euclidean planning coordinates from the CVRPLIB instance -- not a
 * geographic map (CVRPLIB coordinates are synthetic 2D planning units, no
 * lat/lon exists for these benchmark instances). Every point plotted here
 * traces to a real coordinate the backend returned, never a decorative
 * placeholder. A textual route table below is the accessible equivalent
 * (Milestone 2's a11y requirement: charts must have textual equivalents). */
export function RouteVisualization({ depot, nodes, routes }: RouteVisualizationProps) {
  const [selectedRoute, setSelectedRoute] = useState<number | null>(null);

  const allPoints = [depot, ...nodes];
  const xs = allPoints.map((p) => p[0]);
  const ys = allPoints.map((p) => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const pad = Math.max(maxX - minX, maxY - minY, 1) * 0.1;
  const viewMinX = minX - pad, viewMinY = minY - pad;
  const viewW = maxX - minX + pad * 2, viewH = maxY - minY + pad * 2;

  // SVG y grows downward; flip so the plot reads like a standard chart.
  const sy = (y: number) => viewMinY + (viewH - (y - viewMinY));

  return (
    <div>
      <svg
        viewBox={`${viewMinX} ${viewMinY} ${viewW} ${viewH}`}
        className="h-80 w-full rounded-md border border-border bg-background/40"
        role="img"
        aria-label={`Route map: depot plus ${nodes.length} customers across ${routes.length} vehicle routes`}
      >
        {routes.map((route, ri) => {
          const color = ROUTE_COLORS[ri % ROUTE_COLORS.length];
          const pts = [depot, ...route.map((i) => nodes[i]), depot];
          const path = pts.map((p) => `${p[0]},${sy(p[1])}`).join(" ");
          const dimmed = selectedRoute !== null && selectedRoute !== ri;
          return (
            <polyline
              key={ri}
              points={path}
              fill="none"
              stroke={color}
              strokeWidth={viewW * 0.004}
              opacity={dimmed ? 0.15 : 0.85}
              className="cursor-pointer transition-opacity duration-[var(--duration-fast)]"
              onClick={() => setSelectedRoute(selectedRoute === ri ? null : ri)}
            >
              <title>{`Route ${ri + 1}: ${route.length} stops`}</title>
            </polyline>
          );
        })}
        <circle cx={depot[0]} cy={sy(depot[1])} r={viewW * 0.014} fill="var(--foreground)">
          <title>Depot</title>
        </circle>
        {nodes.map((n, i) => {
          const routeIdx = routes.findIndex((r) => r.includes(i));
          const color = routeIdx >= 0 ? ROUTE_COLORS[routeIdx % ROUTE_COLORS.length] : "var(--muted)";
          const dimmed = selectedRoute !== null && selectedRoute !== routeIdx;
          return (
            <circle
              key={i}
              cx={n[0]}
              cy={sy(n[1])}
              r={viewW * 0.01}
              fill={color}
              opacity={dimmed ? 0.25 : 1}
            >
              <title>{`Customer ${i} — route ${routeIdx >= 0 ? routeIdx + 1 : "unassigned"}`}</title>
            </circle>
          );
        })}
      </svg>
      <p className="mt-1 text-caption">
        Real Euclidean planning coordinates from the CVRPLIB instance — not a geographic map. Click a route to
        highlight it.
      </p>

      <table className="sr-only">
        <caption>Route assignments (textual equivalent of the map above)</caption>
        <thead>
          <tr>
            <th>Route</th>
            <th>Stops (customer index, visit order)</th>
          </tr>
        </thead>
        <tbody>
          {routes.map((route, ri) => (
            <tr key={ri}>
              <td>Route {ri + 1}</td>
              <td>{route.join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
