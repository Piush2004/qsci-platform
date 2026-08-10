from fastapi import APIRouter
from backend.app.schemas.research import QuantumExperimentLog
from typing import List

router = APIRouter()

@router.get("/research", response_model=List[QuantumExperimentLog])
def get_research_logs():
    return [
        {
            "experiment_id": "exp_quantum_001",
            "circuit_config": "ZZFeatureMap + TwoLocal",
            "depth": 15,
            "optimizer": "SPSA",
            "shots": 1024,
            "noise_model": "ibm_oslo_noise",
            "backend": "ibm_oslo",
            "rmse": 12.4,
            "observations": "Faster convergence than classical baseline, but noise impacts precision.",
            "conclusion": "Promising for high-dimensional feature spaces."
        }
    ]
