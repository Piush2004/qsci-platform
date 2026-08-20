/**
 * Typed client for the QSCI FastAPI backend. Every function here is a thin
 * fetch wrapper -- NO business logic, NO computed metrics, NO fabricated
 * fallback data. If the backend is unreachable or returns an error, that
 * error propagates to the caller; components must render it honestly
 * (e.g. "backend unavailable"), never substitute a fake number.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* body wasn't JSON -- keep statusText */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export type RunStatus = "PENDING" | "RUNNING" | "COMPLETE" | "FAILED";

export interface DatasetInfo {
  id: number;
  name: string;
  source: string;
  version: string;
  record_count: number;
  date_range_start: string | null;
  date_range_end: string | null;
  quality_status: string;
  quality_report: Record<string, unknown>;
  ingested_at: string;
}

export interface ForecastRun {
  id: number;
  dataset: string;
  series_id: string;
  model: string;
  horizon: number;
  run_status: RunStatus;
  label: string;
  predictions: Record<string, number[]> | null;
  metrics: Record<string, number> | null;
  runtime_seconds: number | null;
  model_metadata: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface OptimizationRun {
  id: number;
  problem_type: string;
  method: string;
  run_status: RunStatus;
  label: string;
  input_params: Record<string, unknown>;
  objective: number | null;
  solution: Record<string, unknown> | null;
  feasible: boolean | null;
  optimality_gap_pct: number | null;
  resource_metrics: Record<string, unknown> | null;
  runtime_seconds: number | null;
  error: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface CvrplibInstance {
  instance: string;
  num_nodes: number;
  num_customers: number;
  capacity: number;
  n_vehicles_published: number;
  coords: [number, number][];
  demands: number[];
  depot_index: number;
  published_bks: number;
  published_route_cost: number | null;
  status: string;
}

export interface ConfidenceBreakdown {
  data_quality: number;
  forecast_stability: number | string;
  model_consensus: number;
  backtest_performance: number;
  overall: number;
  weights: Record<string, number>;
  status: string;
}

export interface Recommendation {
  id: number;
  sku_id: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "MODIFIED";
  created_at: string;
  forecast_p10: number;
  forecast_p50: number;
  forecast_p90: number;
  suggested_order_qty: number;
  reorder_point: number;
  risk_probability: number;
  risk_level: string;
  confidence_overall: number;
  confidence_breakdown: ConfidenceBreakdown;
  financial_impact: Record<string, unknown>;
  rationale: string;
}

export interface AuditEvent {
  id: number;
  recommendation_id: number;
  event_type: string;
  event_payload: Record<string, unknown>;
  created_at: string;
}

export const api = {
  health: () => request<{ status: string; qsci_core_importable: boolean }>("/health"),

  ingestDataset: (dataset: string, cvrplibInstance?: string) =>
    request<DatasetInfo>("/data/ingest", {
      method: "POST",
      body: JSON.stringify({ dataset, cvrplib_instance: cvrplibInstance }),
    }),
  dataSources: () => request<DatasetInfo[]>("/data/sources"),

  createForecast: (model: string, seriesId?: string, horizon?: number) =>
    request<ForecastRun>("/forecast", {
      method: "POST",
      body: JSON.stringify({ model, series_id: seriesId, horizon }),
    }),
  getForecast: (runId: number) => request<ForecastRun>(`/forecast/${runId}`),

  createOptimization: (problemType: string, method: string, params: Record<string, unknown>) =>
    request<OptimizationRun>("/optimize", {
      method: "POST",
      body: JSON.stringify({ problem_type: problemType, method, params }),
    }),
  getOptimization: (runId: number) => request<OptimizationRun>(`/optimization/${runId}`),
  listOptimizations: (problemType?: string) =>
    request<OptimizationRun[]>(`/optimization${problemType ? `?problem_type=${problemType}` : ""}`),
  getInstance: (name: string) => request<CvrplibInstance>(`/optimize/instances/${name}`),
  researchRouting: () => request<Record<string, unknown>>("/research/routing"),

  createRecommendation: (forecastRunId: number, leadTimeDays = 3.0) =>
    request<Recommendation>("/recommend", {
      method: "POST",
      body: JSON.stringify({ forecast_run_id: forecastRunId, lead_time_days: leadTimeDays }),
    }),
  listRecommendations: () => request<Recommendation[]>("/recommendations"),
  getRecommendation: (id: number) => request<Recommendation>(`/recommendations/${id}`),
  approve: (id: number, approver: string, notes?: string) =>
    request<Recommendation>(`/recommendations/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({ approver, notes }),
    }),
  reject: (id: number, approver: string, notes?: string) =>
    request<Recommendation>(`/recommendations/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ approver, notes }),
    }),
  modify: (id: number, approver: string, modifiedQty: number, notes?: string) =>
    request<Recommendation>(`/recommendations/${id}/modify`, {
      method: "POST",
      body: JSON.stringify({ approver, modified_qty: modifiedQty, notes }),
    }),

  audit: (recommendationId?: number) =>
    request<AuditEvent[]>(`/audit${recommendationId ? `?recommendation_id=${recommendationId}` : ""}`),

  researchBenchmarks: () => request<Record<string, unknown>>("/research/benchmarks"),
  researchExperiments: () => request<Record<string, unknown>>("/research/experiments"),
  researchScalability: () => request<Record<string, unknown>>("/research/scalability"),
  researchNoise: () => request<Record<string, unknown>>("/research/noise"),
};
