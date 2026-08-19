"""FastAPI entry point. Architecture: Next.js -> FastAPI -> service layer ->
qsci_core -> DB/experiment results. No business logic lives here or in
app/api/routes/* -- routes call app/services/*, which call qsci_core."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for `import qsci_core`

import math

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import data, forecast, health, optimize, recommend, research

app = FastAPI(title="QSCI API", version="0.1.0")


def _sanitize_non_finite(value):
    """Starlette's JSONResponse enforces strict JSON (allow_nan=False) --
    FastAPI's default validation-error handler echoes back the rejected
    input verbatim, so a non-finite float (inf/-inf/nan) sent by a client
    would otherwise crash the error response itself with a 500 instead of
    cleanly reporting the 422 that rejected it. Recurses through the
    error-detail structure and stringifies only non-finite floats."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: _sanitize_non_finite(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_non_finite(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content=_sanitize_non_finite(jsonable_encoder({"detail": exc.errors()})))

app.add_middleware(
    CORSMiddleware,
    # Dev-only: Next.js falls back to the next free port (3001, 3002, ...)
    # when 3000 is taken, so a fixed origin list is too brittle here.
    # Production must replace this with an explicit allowlist.
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")
app.include_router(forecast.router, prefix="/api/v1")
app.include_router(optimize.router, prefix="/api/v1")
app.include_router(recommend.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")
