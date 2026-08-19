"""DB session wiring for the FastAPI app -- reuses qsci_core.persistence's
engine/models (the shared engine is the source of truth for schema; this
module only adds the FastAPI dependency-injection glue). Table creation is
NOT done here -- schema is owned by Alembic migrations
(backend/migrations/), run explicitly (`alembic upgrade head`), never
silently invoked on app startup."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "experiments" / "qsci_dev.db"
DB_URL = os.environ.get("QSCI_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
