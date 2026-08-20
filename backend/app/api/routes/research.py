from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import recommendation_service, research_service

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/benchmarks")
def benchmarks() -> dict:
    return research_service.get_benchmarks()


@router.get("/experiments")
def experiments() -> dict:
    return research_service.get_experiments()


@router.get("/scalability")
def scalability() -> dict:
    return research_service.get_scalability()


@router.get("/noise")
def noise() -> dict:
    return research_service.get_noise()


@router.get("/routing")
def routing() -> dict:
    return research_service.get_routing()


@router.get("/accuracy-vs-outcome")
def accuracy_vs_outcome(series_id: str = "FOODS_3_090_CA_1_evaluation", db: Session = Depends(get_db)) -> dict:
    return recommendation_service.get_accuracy_vs_outcome(db, series_id)
