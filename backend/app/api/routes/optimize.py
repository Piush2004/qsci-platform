from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.schemas.schemas import OptimizationRunResponse, OptimizeRequest
from app.services import optimization_service

router = APIRouter(tags=["optimize"])

SYNCHRONOUS_METHODS = {"eoq", "or_tools", "simulated_annealing"}


def _run_in_own_session(run_id: int) -> None:
    session = SessionLocal()
    try:
        optimization_service.execute_run(session, run_id)
    finally:
        session.close()


@router.post("/optimize", response_model=OptimizationRunResponse)
def create_optimization(req: OptimizeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> OptimizationRunResponse:
    try:
        run = optimization_service.create_run(db, req.problem_type, req.method, req.params)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if req.method in SYNCHRONOUS_METHODS:
        optimization_service.execute_run(db, run.id)
        db.refresh(run)
    else:
        background_tasks.add_task(_run_in_own_session, run.id)
    return OptimizationRunResponse.model_validate(run)


@router.get("/optimization/{run_id}", response_model=OptimizationRunResponse)
def get_optimization(run_id: int, db: Session = Depends(get_db)) -> OptimizationRunResponse:
    run = optimization_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"no optimization run with id={run_id}")
    return OptimizationRunResponse.model_validate(run)
