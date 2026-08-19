"""Wraps qsci_core.data (loaders + quality) for the /api/v1/data/* routes.
Every value returned here is read from real files on disk via qsci_core --
this module never fabricates record counts, date ranges, or quality
verdicts."""

from __future__ import annotations

from sqlalchemy.orm import Session

from qsci_core.data import loaders, quality
from qsci_core.persistence.models import DatasetRecord

SUPPORTED_DATASETS = {"m5", "cvrplib", "last_mile"}


def ingest_m5(db: Session) -> DatasetRecord:
    m5 = loaders.load_m5()
    report = quality.assess_m5(m5["sales"], m5["calendar"], m5["prices"])
    record = DatasetRecord(
        name="m5",
        source="M5 Forecasting - Accuracy (Kaggle competition)",
        version="sales_train_evaluation",
        record_count=report.n_rows,
        date_range_start=report.date_range[0] if report.date_range else None,
        date_range_end=report.date_range[1] if report.date_range else None,
        quality_status=report.status,
        quality_report=report.to_dict(),
    )
    _upsert(db, record)
    return record


def ingest_cvrplib(db: Session, instance_name: str = "A-n32-k5") -> DatasetRecord:
    instance, _solution = loaders.load_cvrplib_instance(instance_name)
    report = quality.assess_cvrplib_instance(instance, name=instance_name)
    record = DatasetRecord(
        name=f"cvrplib:{instance_name}",
        source="CVRPLIB benchmark instance",
        version=instance_name,
        record_count=report.n_rows,
        quality_status=report.status,
        quality_report=report.to_dict(),
    )
    _upsert(db, record)
    return record


def ingest_last_mile(db: Session) -> DatasetRecord:
    data = loaders.load_last_mile()
    route_count = len(data.get("route_data", {}))
    record = DatasetRecord(
        name="last_mile",
        source="Amazon Last-Mile Routing Research Challenge (CC BY-NC 4.0)",
        version="almrrc2021",
        record_count=route_count,
        quality_status="LIVE",
        quality_report={"files_loaded": list(data.keys()), "route_count": route_count},
    )
    _upsert(db, record)
    return record


def _upsert(db: Session, record: DatasetRecord) -> None:
    existing = db.query(DatasetRecord).filter_by(name=record.name).first()
    if existing:
        db.delete(existing)
        db.flush()
    db.add(record)
    db.commit()
    db.refresh(record)


def list_datasets(db: Session) -> list[DatasetRecord]:
    return db.query(DatasetRecord).order_by(DatasetRecord.ingested_at.desc()).all()
