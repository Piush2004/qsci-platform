"""API tests: valid request, invalid request, missing data, malformed
data, invalid recommendation ID, duplicate approval, invalid state
transition, per CLAUDE.md Phase 6's API-testing requirement. Uses the
real qsci_core pipeline (real M5/CVRPLIB data, real LightGBM/OR-Tools/
annealing runs) against an isolated temp DB -- no mocking of qsci_core
itself, since the whole point is verifying the backend wires the already-
validated engine correctly."""

from __future__ import annotations

import pytest


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["qsci_core_importable"] is True


def test_ingest_m5_is_real_data(client):
    r = client.post("/api/v1/data/ingest", json={"dataset": "m5"})
    assert r.status_code == 200
    body = r.json()
    assert body["quality_status"] == "LIVE"
    assert body["record_count"] > 1000  # real M5 has 30,490 series -- not a placeholder count
    assert body["date_range_start"] is not None


def test_ingest_cvrplib_is_real_data(client):
    r = client.post("/api/v1/data/ingest", json={"dataset": "cvrplib", "cvrplib_instance": "A-n32-k5"})
    assert r.status_code == 200
    body = r.json()
    assert body["record_count"] == 32  # A-n32-k5: 31 customers + depot, verified in Phase 0/3


def test_ingest_unsupported_dataset_rejected(client):
    r = client.post("/api/v1/data/ingest", json={"dataset": "not_a_real_dataset"})
    assert r.status_code == 422


def test_ingest_missing_dataset_field_rejected(client):
    r = client.post("/api/v1/data/ingest", json={})
    assert r.status_code == 422


def test_sources_lists_ingested_datasets(client):
    client.post("/api/v1/data/ingest", json={"dataset": "cvrplib", "cvrplib_instance": "B-n31-k5"})
    r = client.get("/api/v1/data/sources")
    assert r.status_code == 200
    names = [d["name"] for d in r.json()]
    assert "cvrplib:B-n31-k5" in names


def test_forecast_seasonal_naive_synchronous_and_real(client):
    r = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14})
    assert r.status_code == 200
    body = r.json()
    assert body["run_status"] == "COMPLETE"
    assert body["label"] == "LIVE"
    assert len(body["predictions"]["p50"]) == 14
    assert body["metrics"]["wmape"] > 0


def test_forecast_lightgbm_has_real_quantiles(client):
    r = client.post("/api/v1/forecast", json={"model": "lightgbm", "horizon": 14})
    assert r.status_code == 200
    body = r.json()
    assert body["run_status"] == "COMPLETE"
    p10, p50, p90 = body["predictions"]["p10"], body["predictions"]["p50"], body["predictions"]["p90"]
    assert all(a <= b <= c for a, b, c in zip(p10, p50, p90))  # quantile-crossing fix verified end-to-end


def test_forecast_invalid_model_rejected(client):
    r = client.post("/api/v1/forecast", json={"model": "not_a_real_model", "horizon": 14})
    assert r.status_code == 422


def test_forecast_invalid_horizon_rejected(client):
    r = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": -5})
    assert r.status_code == 422


def test_forecast_unknown_series_id_is_a_clean_422(client):
    r = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "series_id": "NOT_A_REAL_SERIES", "horizon": 14})
    body = r.json()
    # the model runs synchronously; the series-not-found ValueError is
    # caught inside execute_run and recorded as a FAILED run, not a 500
    assert r.status_code == 200
    assert body["run_status"] == "FAILED"
    assert "not found" in body["error"]


def test_get_forecast_by_id(client):
    created = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    r = client.get(f"/api/v1/forecast/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_forecast_invalid_id_404(client):
    r = client.get("/api/v1/forecast/999999")
    assert r.status_code == 404


def test_optimize_eoq_is_illustrative(client):
    r = client.post("/api/v1/optimize", json={
        "problem_type": "inventory", "method": "eoq",
        "params": {"annual_demand": 1000, "holding_cost_per_unit_per_year": 2.5,
                   "ordering_cost_per_order": 50, "stockout_cost_per_unit": 15,
                   "demand_std": 10, "lead_time_days": 3},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "ILLUSTRATIVE"
    assert body["run_status"] == "COMPLETE"
    assert body["objective"] > 0


def test_optimize_or_tools_routing_is_live(client):
    r = client.post("/api/v1/optimize", json={
        "problem_type": "routing", "method": "or_tools",
        "params": {"cvrplib_instance": "A-n32-k5", "n_vehicles": 5, "time_limit_seconds": 10},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "LIVE"
    assert body["feasible"] is True
    assert body["objective"] > 0


def test_optimize_or_tools_qubo_is_live_and_fair_reference(client):
    """OR-Tools-on-QUBO (not native OR-Tools) is the actually-fair
    classical reference for the QUBO-track comparison -- Phase 3's own
    fairness audit finding, now exposed via the API for Milestone 2."""
    r = client.post("/api/v1/optimize", json={
        "problem_type": "routing", "method": "or_tools_qubo",
        "params": {"cvrplib_instance": "A-n32-k5", "n_customers": 4},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "LIVE"
    assert body["feasible"] is True
    assert body["objective"] == pytest.approx(380.00755017228636, abs=1e-4)  # matches Phase 3's recorded N=4 result


def test_optimize_annealing_routing_is_research(client):
    r = client.post("/api/v1/optimize", json={
        "problem_type": "routing", "method": "simulated_annealing",
        "params": {"cvrplib_instance": "A-n32-k5", "n_customers": 4, "num_reads": 200, "seed": 42},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "RESEARCH"
    assert "SIMULATED ANNEALING" in body["resource_metrics"]["backend"]
    assert "hardware" not in body["resource_metrics"]["backend"].lower()


def test_optimize_invalid_method_rejected(client):
    r = client.post("/api/v1/optimize", json={"problem_type": "routing", "method": "not_a_real_method", "params": {}})
    assert r.status_code == 422


def test_optimize_qaoa_is_not_in_the_synchronous_method_set(client):
    """QAOA is documented-slow (up to ~630s/run, Phase 3/4 measurements) --
    it must never be handled as a blocking call. Asserted directly against
    the route's own dispatch table rather than by racing a real
    background task's completion time (which would make this test flaky:
    Starlette TestClient's background-task timing relative to the assert
    is an implementation detail, not something a test should depend on)."""
    from app.api.routes.optimize import SYNCHRONOUS_METHODS
    assert "qaoa" not in SYNCHRONOUS_METHODS


def test_optimize_qaoa_run_created_pending_before_execution(client, db_session):
    from app.services import optimization_service
    run = optimization_service.create_run(db_session, "routing", "qaoa", {"n_customers": 4})
    assert run.run_status.value == "PENDING"
    assert run.label == "RESEARCH"


def test_or_tools_solution_includes_coords_for_visualization(client):
    r = client.post("/api/v1/optimize", json={
        "problem_type": "routing", "method": "or_tools",
        "params": {"cvrplib_instance": "A-n32-k5", "n_vehicles": 5, "time_limit_seconds": 10},
    })
    body = r.json()
    assert "coords" in body["solution"]
    assert len(body["solution"]["coords"]) == 32  # 31 customers + depot, verified Phase 0/3
    assert body["solution"]["depot_index"] == 0


def test_annealing_solution_includes_coords_for_visualization(client):
    r = client.post("/api/v1/optimize", json={
        "problem_type": "routing", "method": "simulated_annealing",
        "params": {"cvrplib_instance": "A-n32-k5", "n_customers": 4, "num_reads": 200, "seed": 42},
    })
    body = r.json()
    assert "coords" in body["solution"]
    assert "depot_coord" in body["solution"]
    assert len(body["solution"]["coords"]) == 4


def test_list_optimizations(client):
    client.post("/api/v1/optimize", json={
        "problem_type": "routing", "method": "or_tools",
        "params": {"cvrplib_instance": "A-n32-k5", "n_vehicles": 5, "time_limit_seconds": 10},
    })
    r = client.get("/api/v1/optimization")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_list_optimizations_filters_by_problem_type(client):
    r = client.get("/api/v1/optimization?problem_type=routing")
    assert r.status_code == 200
    assert all(row["problem_type"] == "routing" for row in r.json())


def test_get_instance_returns_real_cvrplib_data(client):
    r = client.get("/api/v1/optimize/instances/A-n32-k5")
    assert r.status_code == 200
    body = r.json()
    assert body["num_customers"] == 31
    assert body["published_bks"] == 784
    assert len(body["coords"]) == 32
    assert len(body["demands"]) == 32
    assert body["status"] == "LIVE"


def test_get_instance_unknown_name_404(client):
    r = client.get("/api/v1/optimize/instances/not-a-real-instance")
    assert r.status_code == 404


def test_research_routing_labeled_research_with_fairness_note(client):
    r = client.get("/api/v1/research/routing")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "RESEARCH"
    assert len(body["results"]) == 76  # Phase 3's full N-sweep, verified this session
    assert "NOT directly comparable" in body["note"]


def test_optimization_get_invalid_id_404(client):
    r = client.get("/api/v1/optimization/999999")
    assert r.status_code == 404


def test_recommend_full_golden_path(client):
    fc = client.post("/api/v1/forecast", json={"model": "lightgbm", "horizon": 14}).json()
    r = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "PENDING"
    assert 0.0 <= body["confidence_overall"] <= 1.0
    assert body["financial_impact"]["status"] == "ILLUSTRATIVE"
    assert body["confidence_breakdown"]["data_quality"] == 1.0


def test_recommend_reorder_point_is_plausible_relative_to_daily_demand(client):
    """Regression test for a real bug caught via manual browser verification:
    reorder_point must be on the same order of magnitude as daily demand
    (roughly lead_time_days worth, plus safety stock) -- not a tiny fraction
    of it. The bug divided the already-daily p50 by horizon a second time,
    producing a reorder point far below daily demand and a ~93% stockout
    risk for an ordinary forecast."""
    fc = client.post("/api/v1/forecast", json={"model": "lightgbm", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    daily_demand = rec["forecast_p50"]
    # reorder_point covers lead_time_days (default 3) of demand plus safety
    # stock -- it must be at least comparable to 1 day of demand, not <10%.
    assert rec["reorder_point"] > 0.5 * daily_demand
    assert rec["risk_probability"] < 0.95  # a well-formed forecast shouldn't imply near-certain stockout


def test_recommend_vqr_forecast_has_no_forecast_stability(client):
    """Phase 5's real finding: VQR is a point forecaster and cannot
    produce forecast_stability -- the API must not fabricate one. VQR
    dispatches as a genuine, non-blocking BackgroundTask (confirmed: this
    POST returns PENDING/RUNNING immediately, not COMPLETE) -- poll until
    it finishes rather than assuming any particular completion timing."""
    import time

    fc = client.post("/api/v1/forecast", json={"model": "vqr", "horizon": 14}).json()
    assert fc["run_status"] in ("PENDING", "RUNNING")

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        fc = client.get(f"/api/v1/forecast/{fc['id']}").json()
        if fc["run_status"] in ("COMPLETE", "FAILED"):
            break
        time.sleep(0.5)

    assert fc["run_status"] == "COMPLETE", fc.get("error")
    assert fc["model_metadata"]["forecast_stability"] == (
        "NOT AVAILABLE FOR THIS MODEL (point forecaster, no native quantile output -- Phase 5 finding)"
    )


def test_recommend_incomplete_forecast_run_rejected(client, db_session):
    from app.services import forecast_service
    # Constructed directly (not via POST /forecast) so the run is genuinely
    # left PENDING -- TestClient would otherwise run it to completion
    # synchronously before this assertion could observe the PENDING state.
    run = forecast_service.create_run(db_session, "FOODS_3_090_CA_1_evaluation", "vqr", 14)
    r = client.post("/api/v1/recommend", json={"forecast_run_id": run.id})
    assert r.status_code == 422  # run is PENDING, not COMPLETE


def test_recommend_invalid_forecast_run_id_rejected(client):
    r = client.post("/api/v1/recommend", json={"forecast_run_id": 999999})
    assert r.status_code == 422


def test_approve_reject_modify_workflow(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()

    r = client.post(f"/api/v1/recommendations/{rec['id']}/approve", json={"approver": "test_planner"})
    assert r.status_code == 200
    assert r.json()["status"] == "APPROVED"


def test_duplicate_approval_rejected(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    client.post(f"/api/v1/recommendations/{rec['id']}/approve", json={"approver": "planner_a"})

    r = client.post(f"/api/v1/recommendations/{rec['id']}/approve", json={"approver": "planner_b"})
    assert r.status_code == 409
    assert "already decided" in r.json()["detail"]


def test_invalid_state_transition_reject_after_approve(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    client.post(f"/api/v1/recommendations/{rec['id']}/approve", json={"approver": "planner_a"})

    r = client.post(f"/api/v1/recommendations/{rec['id']}/reject", json={"approver": "planner_b"})
    assert r.status_code == 409


def test_modify_requires_modified_qty(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()

    r = client.post(f"/api/v1/recommendations/{rec['id']}/modify", json={"approver": "planner_a"})
    assert r.status_code == 422


def test_modify_negative_quantity_rejected(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    r = client.post(f"/api/v1/recommendations/{rec['id']}/modify", json={"approver": "planner_a", "modified_qty": -5})
    assert r.status_code == 422


def test_modify_infinite_quantity_rejected(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    # httpx's `json=` param refuses to serialize inf/nan itself (ValueError
    # before the request is even sent) -- send the raw body directly so the
    # non-finite value actually reaches the server's own validation.
    r = client.post(
        f"/api/v1/recommendations/{rec['id']}/modify",
        content='{"approver": "planner_a", "modified_qty": Infinity}',
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 422  # rejected by _finite_qty validator


def test_modify_valid_quantity_and_reason_succeeds(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    r = client.post(f"/api/v1/recommendations/{rec['id']}/modify", json={
        "approver": "planner_a", "modified_qty": 200, "notes": "Adjusted for known upcoming promotion",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "MODIFIED"


def test_modify_audit_event_records_reason(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    client.post(f"/api/v1/recommendations/{rec['id']}/modify", json={
        "approver": "planner_a", "modified_qty": 200, "notes": "Adjusted for known upcoming promotion",
    })
    events = client.get(f"/api/v1/audit?recommendation_id={rec['id']}").json()
    modify_event = next(e for e in events if e["event_type"] == "APPROVAL_MODIFY")
    assert modify_event["event_payload"]["notes"] == "Adjusted for known upcoming promotion"
    assert modify_event["event_payload"]["modified_qty"] == 200


def test_approve_invalid_recommendation_id_404(client):
    r = client.post("/api/v1/recommendations/999999/approve", json={"approver": "planner_a"})
    assert r.status_code == 404


def test_approve_missing_approver_rejected(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    r = client.post(f"/api/v1/recommendations/{rec['id']}/approve", json={"approver": ""})
    assert r.status_code == 422


def test_list_recommendations(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]})
    r = client.get("/api/v1/recommendations")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_recommendation_invalid_id_404(client):
    r = client.get("/api/v1/recommendations/999999")
    assert r.status_code == 404


def test_audit_records_recommendation_creation_and_approval(client):
    fc = client.post("/api/v1/forecast", json={"model": "seasonal_naive", "horizon": 14}).json()
    rec = client.post("/api/v1/recommend", json={"forecast_run_id": fc["id"]}).json()
    client.post(f"/api/v1/recommendations/{rec['id']}/approve", json={"approver": "planner_a"})

    r = client.get(f"/api/v1/audit?recommendation_id={rec['id']}")
    assert r.status_code == 200
    events = [e["event_type"] for e in r.json()]
    assert "RECOMMENDATION_CREATED" in events
    assert "APPROVAL_APPROVE" in events


def test_research_benchmarks_labeled_research_not_live(client):
    r = client.get("/api/v1/research/benchmarks")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("RESEARCH", "PENDING")


def test_research_experiments_index(client):
    r = client.get("/api/v1/research/experiments")
    assert r.status_code == 200
    assert "phase3_routing" in r.json()["experiments"]


def test_research_scalability_from_phase4(client):
    r = client.get("/api/v1/research/scalability")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "RESEARCH"
    assert body["qaoa_depth_tradeoff"] is not None


def test_research_noise_discloses_caveat(client):
    r = client.get("/api/v1/research/noise")
    assert r.status_code == 200
    body = r.json()
    assert "caveat" in body
    assert "PENDING" in body["caveat"]
