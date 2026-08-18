"""Assembles a Recommendation from the forecast, risk, financial, and
confidence layers — the point where QSCI turns a prediction into a proposed
decision a human can approve, reject, or modify."""

from __future__ import annotations

from dataclasses import dataclass

from qsci_core.confidence.decomposition import ConfidenceBreakdown
from qsci_core.risk.stockout_risk import StockoutRiskEstimate


def _risk_level(probability: float) -> str:
    if probability < 0.10:
        return "LOW"
    if probability < 0.30:
        return "MEDIUM"
    return "HIGH"


@dataclass(frozen=True)
class Recommendation:
    sku_id: str
    forecast_p10: float
    forecast_p50: float
    forecast_p90: float
    suggested_order_qty: float
    reorder_point: float
    risk: StockoutRiskEstimate
    confidence: ConfidenceBreakdown
    financial_impact: dict  # from qsci_core.financial.eoq.total_inventory_cost — ILLUSTRATIVE
    rationale: str

    @property
    def risk_level(self) -> str:
        return _risk_level(self.risk.probability)

    def to_dict(self) -> dict:
        return {
            "sku_id": self.sku_id,
            "forecast": {"p10": self.forecast_p10, "p50": self.forecast_p50, "p90": self.forecast_p90},
            "suggested_order_qty": self.suggested_order_qty,
            "reorder_point": self.reorder_point,
            "risk": {"probability": self.risk.probability, "level": self.risk_level, "method": self.risk.method},
            "confidence": self.confidence.to_dict(),
            "financial_impact": self.financial_impact,
            "rationale": self.rationale,
        }


def build_recommendation(
    sku_id: str,
    forecast_p10: float,
    forecast_p50: float,
    forecast_p90: float,
    suggested_order_qty: float,
    reorder_point: float,
    risk: StockoutRiskEstimate,
    confidence: ConfidenceBreakdown,
    financial_impact: dict,
) -> Recommendation:
    if not (forecast_p10 <= forecast_p50 <= forecast_p90):
        raise ValueError(f"forecast quantiles out of order: p10={forecast_p10}, p50={forecast_p50}, p90={forecast_p90}")
    if suggested_order_qty < 0:
        raise ValueError(f"suggested_order_qty must be non-negative, got {suggested_order_qty}")

    risk_level = _risk_level(risk.probability)
    rationale = (
        f"Median demand forecast is {forecast_p50:.1f} units (p10={forecast_p10:.1f}, p90={forecast_p90:.1f}). "
        f"Suggested order quantity is {suggested_order_qty:.1f} units to cover the reorder point of "
        f"{reorder_point:.1f} units. Estimated stockout risk is {risk.probability:.1%} ({risk_level}), "
        f"computed via {risk.method}. Overall confidence is {confidence.overall:.1%}, decomposed as "
        f"data quality={confidence.data_quality:.2f}, forecast stability={confidence.forecast_stability:.2f}, "
        f"model consensus={confidence.model_consensus:.2f}, backtest performance={confidence.backtest_performance:.2f}. "
        f"Financial impact figures are {financial_impact.get('status', 'ILLUSTRATIVE')} — based on documented cost "
        f"assumptions, not real per-unit cost data."
    )

    return Recommendation(
        sku_id=sku_id,
        forecast_p10=forecast_p10,
        forecast_p50=forecast_p50,
        forecast_p90=forecast_p90,
        suggested_order_qty=suggested_order_qty,
        reorder_point=reorder_point,
        risk=risk,
        confidence=confidence,
        financial_impact=financial_impact,
        rationale=rationale,
    )
