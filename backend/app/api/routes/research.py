from fastapi import APIRouter

from app.services import research_service

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
