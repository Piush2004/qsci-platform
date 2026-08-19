"""Test fixtures: an isolated temp-file SQLite DB per test session (never
the real experiments/qsci_dev.db), schema created via qsci_core's own
Base.metadata (equivalent to a fully-migrated DB for test purposes --
Alembic itself is exercised separately, not re-verified by every test)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for qsci_core
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/, for the `app` package

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["QSCI_DATABASE_URL"] = f"sqlite:///{Path(_tmp_db.name).as_posix()}"

from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from qsci_core.persistence.models import Base  # noqa: E402

Base.metadata.create_all(engine)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
