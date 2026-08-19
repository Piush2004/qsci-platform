"""Phase 3 §4/§5 ground-truth re-verification -- reads the actual raw
files on disk directly, does not trust Phase 0/1's prior report numbers.
Produces experiments/results/routing_ground_truth.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qsci_core.data import loaders

CVRPLIB_INSTANCES = ["A-n32-k5", "A-n33-k5", "A-n37-k5", "B-n31-k5"]
PREVIOUSLY_REPORTED_BKS = {"A-n32-k5": 784, "A-n33-k5": 661, "A-n37-k5": 669, "B-n31-k5": 672}


def verify_cvrplib():
    rows = []
    for name in CVRPLIB_INSTANCES:
        instance, solution = loaders.load_cvrplib_instance(name)
        n_vehicles = int(name.rsplit("-k", 1)[1])
        published_bks = solution["cost"]
        row = {
            "instance": name,
            "number_of_customers": instance["dimension"] - 1,
            "number_of_vehicles": n_vehicles,
            "capacity": instance["capacity"],
            "published_bks": published_bks,
            "source": "raw .sol file, data/raw/cvrplib/",
            "verification_status": "MATCHES_PRIOR_REPORT" if published_bks == PREVIOUSLY_REPORTED_BKS[name] else "DISCREPANCY_FOUND",
        }
        rows.append(row)
        print(row)
        if row["verification_status"] == "DISCREPANCY_FOUND":
            print(f"  !!! STOP: {name} published_bks={published_bks} != previously reported {PREVIOUSLY_REPORTED_BKS[name]}")
    return rows


def verify_last_mile():
    base = Path(__file__).resolve().parents[1] / "data" / "raw" / "last_mile" / "almrrc2021-data-training" / "model_build_inputs"
    with open(base / "route_data.json") as f:
        routes = json.load(f)
    with open(base / "package_data.json") as f:
        packages = json.load(f)
    with open(base / "travel_times.json") as f:
        travel_times = json.load(f)
    with open(base / "actual_sequences.json") as f:
        sequences = json.load(f)
    with open(base / "invalid_sequence_scores.json") as f:
        scores = json.load(f)

    n_routes = len(routes)
    n_stops = sum(len(r["stops"]) for r in routes.values())
    station_codes = sorted(set(r["station_code"] for r in routes.values()))
    route_scores = sorted(set(r.get("route_score") for r in routes.values()))
    n_packages = sum(len(pkgs) for route in packages.values() for pkgs in route.values())

    result = {
        "directly_observed": {
            "route_count": n_routes,
            "total_stops_including_depot_per_route": n_stops,
            "unique_station_codes": len(station_codes),
            "station_codes": station_codes,
            "route_score_categories": route_scores,
            "routes_with_travel_times": len(travel_times),
            "routes_with_actual_sequences": len(sequences),
            "routes_with_package_data": len(packages),
            "routes_with_invalid_sequence_scores": len(scores),
            "total_package_count": n_packages,
        },
        "derived": {
            "avg_stops_per_route": round(n_stops / n_routes, 2),
        },
        "assumed": {
            "note": "no monetary, fuel, or driver-cost data present in this dataset -- any such figures used elsewhere in QSCI are ILLUSTRATIVE, not derived from this data",
        },
        "previously_reported_phase_0": {"routes": 6112, "stops": 904527, "match": n_routes == 6112 and n_stops == 904527},
    }
    print(result)
    return result


if __name__ == "__main__":
    print("=== CVRPLIB ground truth ===")
    cvrplib_rows = verify_cvrplib()
    print("\n=== Amazon Last-Mile ground truth ===")
    last_mile_result = verify_last_mile()

    results_dir = Path(__file__).resolve().parents[1] / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "routing_ground_truth.json", "w") as f:
        json.dump({"cvrplib": cvrplib_rows, "amazon_last_mile": last_mile_result}, f, indent=2, default=str)
    print(f"\nSaved to {results_dir / 'routing_ground_truth.json'}")
