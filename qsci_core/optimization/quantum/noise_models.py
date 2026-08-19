"""Aer noise-model presets for the Phase 4 QAOA noise-sensitivity study.

Every preset is a real `qiskit_aer.noise.NoiseModel`, applied via Aer's
`AerSimulator`/`SamplerV2` -- never hand-waved as an accuracy penalty.
Error rates are documented, literature-typical superconducting-qubit
magnitudes (not tuned to produce a particular result): 1Q gate error
~1e-4 to 1e-3, 2Q gate error ~1e-2 to 5e-2, readout error ~1-5%, per
IBM/Google/Rigetti public hardware specs circa 2020s NISQ devices. No
noise model is calibrated against real hardware in this environment --
labeled RESEARCH, not a hardware-derived model.
"""

from __future__ import annotations

from dataclasses import dataclass

from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

BASIS_GATES = ["rz", "sx", "x", "cx"]
ONE_Q_GATES = ["rz", "sx", "x"]
TWO_Q_GATES = ["cx"]


@dataclass(frozen=True)
class NoisePreset:
    label: str
    description: str
    error_1q: float | None
    error_2q: float | None
    readout_p01: float | None
    readout_p10: float | None


PRESETS: dict[str, NoisePreset] = {
    "noiseless": NoisePreset("noiseless", "no noise (statevector-equivalent)", None, None, None, None),
    "depolarizing_low": NoisePreset(
        "depolarizing_low", "1Q=1e-3, 2Q=1e-2 depolarizing (typical current NISQ gate fidelity)", 1e-3, 1e-2, None, None
    ),
    "depolarizing_high": NoisePreset(
        "depolarizing_high", "1Q=1e-2, 2Q=5e-2 depolarizing (pessimistic NISQ gate fidelity)", 1e-2, 5e-2, None, None
    ),
    "readout": NoisePreset(
        "readout", "2% symmetric readout bit-flip error, no gate noise", None, None, 0.02, 0.02
    ),
}


def build_noise_model(preset_name: str) -> NoiseModel | None:
    """Returns None for 'noiseless' (caller should skip Aer and use the
    existing StatevectorSampler path). Raises on unknown preset name --
    never silently falls back to a default."""
    if preset_name not in PRESETS:
        raise ValueError(f"unknown noise preset '{preset_name}', must be one of {list(PRESETS)}")
    p = PRESETS[preset_name]
    if preset_name == "noiseless":
        return None

    nm = NoiseModel(basis_gates=BASIS_GATES)
    if p.error_1q is not None:
        nm.add_all_qubit_quantum_error(depolarizing_error(p.error_1q, 1), ONE_Q_GATES)
    if p.error_2q is not None:
        nm.add_all_qubit_quantum_error(depolarizing_error(p.error_2q, 2), TWO_Q_GATES)
    if p.readout_p01 is not None:
        ro = ReadoutError([[1 - p.readout_p01, p.readout_p01], [p.readout_p10, 1 - p.readout_p10]])
        nm.add_all_qubit_readout_error(ro)
    return nm
