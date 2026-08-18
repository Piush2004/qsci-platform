import json

from qsci_core.forecasting.quantum.experiment import (
    ExperimentConfigResult, ExperimentManifest, save_results,
)


def test_manifest_captures_reproducibility_fields():
    manifest = ExperimentManifest(
        dataset="m5", dataset_version="m5-eval", series_id="FOODS_3_090_CA_1",
        train_start="2016-01-01", train_end="2016-04-01", test_start="2016-04-02",
        test_end="2016-04-15", forecast_horizon=14, seed=42, classical_feature_columns=["lag_1", "lag_7"],
    )
    d = manifest.to_dict()
    assert d["seed"] == 42
    assert d["series_id"] == "FOODS_3_090_CA_1"
    assert "qiskit" in d["software_versions"]
    assert d["git_commit"]  # non-empty -- either a real hash or "unknown", never blank


def test_manifest_software_versions_report_real_installed_versions():
    manifest = ExperimentManifest(
        dataset="m5", dataset_version="v1", series_id="x", train_start="2024-01-01",
        train_end="2024-01-02", test_start="2024-01-03", test_end="2024-01-04",
        forecast_horizon=1, seed=0, classical_feature_columns=[],
    )
    versions = manifest.to_dict()["software_versions"]
    import qiskit
    assert versions["qiskit"] == qiskit.__version__


def test_experiment_config_result_allows_none_for_classical_models():
    result = ExperimentConfigResult(
        model="seasonal_naive", feature_count=None, qubit_count=None, feature_map=None,
        ansatz=None, optimizer=None, optimizer_iterations=None, circuit_depth=None,
        gate_count=None, shots=None, simulator=None, execution_time_seconds=0.01,
        training_time_seconds=None, inference_time_seconds=0.01, rmse=1.0, mae=1.0, wmape=10.0, bias=0.0,
    )
    d = result.to_dict()
    assert d["qubit_count"] is None
    assert d["model"] == "seasonal_naive"


def test_save_results_writes_valid_json_and_csv(tmp_path):
    results = [
        ExperimentConfigResult(
            model="vqr", feature_count=4, qubit_count=4, feature_map="zz", ansatz="real_amplitudes",
            optimizer="cobyla", optimizer_iterations=10, circuit_depth=22, gate_count=37, shots="N/A",
            simulator="AerSimulator", execution_time_seconds=9.8, training_time_seconds=9.7,
            inference_time_seconds=0.08, rmse=24.6, mae=22.4, wmape=41.8, bias=9.3,
        ),
    ]
    json_path, csv_path = tmp_path / "results.json", tmp_path / "results.csv"
    save_results(results, json_path, csv_path)

    with open(json_path) as f:
        loaded = json.load(f)
    assert loaded[0]["model"] == "vqr"
    assert loaded[0]["qubit_count"] == 4

    csv_content = csv_path.read_text()
    assert "vqr" in csv_content
    assert "qubit_count" in csv_content


def test_save_results_empty_list_does_not_crash(tmp_path):
    json_path, csv_path = tmp_path / "empty.json", tmp_path / "empty.csv"
    save_results([], json_path, csv_path)
    with open(json_path) as f:
        assert json.load(f) == []
