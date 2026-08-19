from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import DataIngestRequest, DatasetResponse
from app.services import data_service

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/ingest", response_model=DatasetResponse)
def ingest(req: DataIngestRequest, db: Session = Depends(get_db)) -> DatasetResponse:
    try:
        if req.dataset == "m5":
            record = data_service.ingest_m5(db)
        elif req.dataset == "cvrplib":
            record = data_service.ingest_cvrplib(db, req.cvrplib_instance or "A-n32-k5")
        elif req.dataset == "last_mile":
            record = data_service.ingest_last_mile(db)
        else:
            raise HTTPException(status_code=422, detail=f"unsupported dataset '{req.dataset}', must be one of {sorted(data_service.SUPPORTED_DATASETS)}")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DatasetResponse.model_validate(record)


@router.get("/sources", response_model=list[DatasetResponse])
def sources(db: Session = Depends(get_db)) -> list[DatasetResponse]:
    return [DatasetResponse.model_validate(r) for r in data_service.list_datasets(db)]
