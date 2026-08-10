from fastapi import APIRouter
from backend.app.services.mlflow_service import MLFlowService
from pydantic import BaseModel

router = APIRouter()
mlflow_service = MLFlowService()

class PromoteRequest(BaseModel):
    target_stage: str
    approved_by: str

@router.get("/models")
def get_models():
    return mlflow_service.get_leaderboard()

@router.post("/models/{run_id}/promote")
def promote_model(run_id: str, req: PromoteRequest):
    # Model promotion requires human approval
    mlflow_service.approve_promotion(run_id, req.approved_by)
    return {"status": "success", "message": f"Model {run_id} promoted to {req.target_stage}"}
