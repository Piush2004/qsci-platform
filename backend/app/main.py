"""FastAPI entry point. Architecture: Next.js -> FastAPI -> service layer ->
qsci_core -> DB/experiment results. No business logic lives here or in
app/api/routes/* -- routes call app/services/*, which call qsci_core."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for `import qsci_core`

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import data, forecast, health, optimize, recommend, research

app = FastAPI(title="QSCI API", version="0.1.0")

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
