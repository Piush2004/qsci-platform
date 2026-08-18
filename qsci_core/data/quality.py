"""Data quality assessment for QSCI datasets.

Every check here runs against real loaded data (LIVE). There is no synthetic
fallback: if a dataset isn't present, the loader raises rather than this
module silently reporting on fabricated rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class DataQualityReport:
    dataset_name: str
    status: str  # always "LIVE" for this module — see qsci_core/data/quality.py docstring
    n_rows: int
    n_cols: int
    missing_pct: dict[str, float] = field(default_factory=dict)
    duplicate_rows: int = 0
    date_range: tuple[str, str] | None = None
    date_gaps: int = 0
    negative_value_counts: dict[str, int] = field(default_factory=dict)
    zero_inflation_pct: dict[str, float] = field(default_factory=dict)
    outlier_pct: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "status": self.status,
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "missing_pct": self.missing_pct,
            "duplicate_rows": self.duplicate_rows,
            "date_range": self.date_range,
            "date_gaps": self.date_gaps,
            "negative_value_counts": self.negative_value_counts,
            "zero_inflation_pct": self.zero_inflation_pct,
            "outlier_pct": self.outlier_pct,
            "notes": self.notes,
        }

    def to_markdown(self) -> str:
        lines = [
            f"### Data Quality Report — {self.dataset_name} [{self.status}]",
            f"- rows: {self.n_rows:,}  cols: {self.n_cols}",
            f"- duplicate rows: {self.duplicate_rows:,}",
        ]
        if self.date_range:
            lines.append(f"- date range: {self.date_range[0]} to {self.date_range[1]} (gaps: {self.date_gaps})")
        if self.missing_pct:
            worst = sorted(self.missing_pct.items(), key=lambda kv: -kv[1])[:10]
            lines.append("- missing % (top 10 columns): " + ", ".join(f"{c}={p:.2f}%" for c, p in worst if p > 0) or "- missing %: none")
        if self.negative_value_counts:
            lines.append("- negative values: " + ", ".join(f"{c}={n}" for c, n in self.negative_value_counts.items() if n))
        if self.zero_inflation_pct:
            lines.append("- zero-inflation %: " + ", ".join(f"{c}={p:.2f}%" for c, p in self.zero_inflation_pct.items()))
        if self.outlier_pct:
            lines.append("- IQR outlier %: " + ", ".join(f"{c}={p:.2f}%" for c, p in self.outlier_pct.items()))
        if self.notes:
            lines.append("- notes: " + "; ".join(self.notes))
        return "\n".join(lines)


def _missing_pct(df: pd.DataFrame) -> dict[str, float]:
    return {c: float(df[c].isna().mean() * 100) for c in df.columns}


def _iqr_outlier_pct(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return 0.0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return float(((s < lo) | (s > hi)).mean() * 100)


def assess_m5(sales: pd.DataFrame, calendar: pd.DataFrame, prices: pd.DataFrame) -> DataQualityReport:
    """Quality-check the three M5 tables jointly."""
    notes = []

    day_cols = [c for c in sales.columns if c.startswith("d_")]
    id_cols = [c for c in sales.columns if c not in day_cols]

    report = DataQualityReport(
        dataset_name="M5 Forecasting - Accuracy (sales_train)",
        status="LIVE",
        n_rows=len(sales),
        n_cols=len(sales.columns),
    )
    report.missing_pct = {c: p for c, p in _missing_pct(sales[id_cols]).items() if p > 0}
    report.duplicate_rows = int(sales.duplicated(subset=["id"]).sum()) if "id" in sales.columns else int(sales.duplicated().sum())

    sales_matrix = sales[day_cols].to_numpy()
    neg_count = int((sales_matrix < 0).sum())
    report.negative_value_counts = {"unit_sales (all d_ cols)": neg_count}
    report.zero_inflation_pct = {"unit_sales (all d_ cols)": float((sales_matrix == 0).mean() * 100)}

    if not calendar.empty:
        dmin, dmax = calendar["date"].min(), calendar["date"].max()
        report.date_range = (str(dmin.date()), str(dmax.date()))
        expected_days = pd.date_range(dmin, dmax, freq="D")
        report.date_gaps = int(len(expected_days) - calendar["date"].nunique())
        if len(day_cols) != len(calendar):
            notes.append(
                f"sales has {len(day_cols)} day columns but calendar has {len(calendar)} rows "
                "(expected: evaluation file covers more days than validation)"
            )

    if not prices.empty:
        report.negative_value_counts["sell_price"] = int((prices["sell_price"] < 0).sum())
        report.outlier_pct["sell_price"] = _iqr_outlier_pct(prices["sell_price"])
        price_missing = float(prices["sell_price"].isna().mean() * 100)
        if price_missing:
            report.missing_pct["sell_price"] = price_missing

    report.notes = notes
    return report


def assess_cvrplib_instance(instance: dict, name: str = "cvrplib_instance") -> DataQualityReport:
    """Quality-check a parsed CVRPLIB instance (as returned by vrplib.read_instance)."""
    coords = np.asarray(instance.get("node_coord", []))
    demands = np.asarray(instance.get("demand", []))
    capacity = instance.get("capacity")

    n_nodes = len(coords) if coords.size else len(demands)
    report = DataQualityReport(
        dataset_name=f"CVRPLIB {name}",
        status="LIVE",
        n_rows=n_nodes,
        n_cols=coords.shape[1] if coords.ndim == 2 else 0,
    )
    if demands.size:
        report.negative_value_counts = {"demand": int((demands < 0).sum())}
        if capacity is not None and (demands > capacity).any():
            report.notes.append(f"{int((demands > capacity).sum())} node(s) exceed vehicle capacity {capacity}")
    if coords.size and np.unique(coords, axis=0).shape[0] != coords.shape[0]:
        report.duplicate_rows = int(coords.shape[0] - np.unique(coords, axis=0).shape[0])
    return report


def assess_dataframe(df: pd.DataFrame, dataset_name: str, numeric_cols: list[str] | None = None) -> DataQualityReport:
    """Generic dataframe quality check, used for anything without a dataset-specific assessor."""
    report = DataQualityReport(
        dataset_name=dataset_name,
        status="LIVE",
        n_rows=len(df),
        n_cols=len(df.columns),
    )
    report.missing_pct = {c: p for c, p in _missing_pct(df).items() if p > 0}
    report.duplicate_rows = int(df.duplicated().sum())

    numeric_cols = numeric_cols or df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col not in df.columns:
            continue
        report.negative_value_counts[col] = int((df[col] < 0).sum())
        report.zero_inflation_pct[col] = float((df[col] == 0).mean() * 100)
        report.outlier_pct[col] = _iqr_outlier_pct(df[col])
    return report
