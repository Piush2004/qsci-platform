from fastapi import APIRouter

from app.schemas.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        import qsci_core  # noqa: F401
        importable = True
    except ImportError:
        importable = False
    return HealthResponse(status="ok", qsci_core_importable=importable)
