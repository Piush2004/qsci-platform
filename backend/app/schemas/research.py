from pydantic import BaseModel
from typing import Optional

class QuantumExperimentLog(BaseModel):
    experiment_id: str
    circuit_config: str
    depth: int
    optimizer: str
    shots: int
    noise_model: str
    backend: str
    rmse: float
    observations: str
    conclusion: str
