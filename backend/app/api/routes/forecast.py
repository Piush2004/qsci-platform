from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.schemas.schemas import ForecastRequest, ForecastRunResponse
from app.services import forecast_service

router = APIRouter(prefix="/forecast", tags=["forecast"])

SYNCHRONOUS_MODELS = {"seasonal_naive", "lightgbm"}


def _run_in_own_session(run_id: int) -> None:
    """Background tasks must not reuse the request's `db` session -- it may
    already be closed by the get_db dependency's teardown by the time this
    runs. Opens and closes its own session instead."""
    session = SessionLocal()
    try:
        forecast_service.execute_run(session, run_id)
    finally:
        session.close()


@router.post("", response_model=ForecastRunResponse)
def create_forecast(req: ForecastRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> ForecastRunResponse:
    try:
        run = forecast_service.create_run(db, req.series_id, req.model, req.horizon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if req.model in SYNCHRONOUS_MODELS:
        forecast_service.execute_run(db, run.id)
        db.refresh(run)
    else:
        background_tasks.add_task(_run_in_own_session, run.id)
    return ForecastRunResponse.model_validate(run)


@router.get("/{run_id}", response_model=ForecastRunResponse)
def get_forecast(run_id: int, db: Session = Depends(get_db)) -> ForecastRunResponse:
    run = forecast_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"no forecast run with id={run_id}")
    return ForecastRunResponse.model_validate(run)
