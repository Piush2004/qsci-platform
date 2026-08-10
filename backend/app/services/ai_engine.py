"""
AI Engine Service — Mock inference for Phase 2.

Simulates TFT/LightGBM/Chronos forecast outputs and the 4-factor
Recommendation Confidence Framework (PRD §9.1).
"""
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.schemas.domain import (
    ConfidenceComponent,
    ConfidenceDecomposition,
    DriverAttribution,
)


# SKU catalog for realistic mock data
_SKU_CATALOG = [
    {"sku_id": "SKU-98421", "name": "High-Tech Semiconductor Assembly", "location": "Shanghai-DC1", "base_demand": 12500},
    {"sku_id": "SKU-44102", "name": "Industrial Bearing Set (Type-IV)", "location": "Munich-WH3", "base_demand": 8200},
    {"sku_id": "SKU-10923", "name": "Lithium Battery Module 48V", "location": "Detroit-FC2", "base_demand": 5600},
    {"sku_id": "SKU-77310", "name": "Organic LED Panel 15.6\"", "location": "Shenzhen-DC5", "base_demand": 9800},
    {"sku_id": "SKU-55201", "name": "Precision Valve Assembly", "location": "Houston-WH1", "base_demand": 3400},
    {"sku_id": "SKU-33089", "name": "Fiber Optic Cable Spool (500m)", "location": "Frankfurt-DC2", "base_demand": 7100},
    {"sku_id": "SKU-21456", "name": "Pharmaceutical Grade Vial (10mL)", "location": "Basel-WH2", "base_demand": 22000},
    {"sku_id": "SKU-66743", "name": "Automotive ECU Module v3", "location": "Nagoya-FC1", "base_demand": 4100},
]

_SHAP_FEATURES = [
    ("Promotional Lift", "positive"),
    ("Seasonal Baseline", "positive"),
    ("Economic Index", "positive"),
    ("Weather Disruption", "negative"),
    ("Supplier Lead Time", "negative"),
    ("Port Congestion Risk", "negative"),
    ("Inventory Rebalancing", "positive"),
    ("Customer Sentiment", "positive"),
]


class AIEngine:
    """
    Mock AI Engine for Phase 2.
    In production, this service calls the trained TFT/LightGBM models
    via MLflow Model Registry.
    """

    def generate_mock_forecasts(self, count: int = 8) -> List[Dict[str, Any]]:
        """Generate realistic forecast data for each SKU."""
        forecasts = []
        for i, sku in enumerate(_SKU_CATALOG[:count]):
            noise = random.gauss(0, 0.08)
            demand = sku["base_demand"] * (1 + noise)
            spread = demand * random.uniform(0.06, 0.18)
            
            forecasts.append({
                "id": f"fc-{2026080900 + i}",
                "tenant_id": "mock_tenant_456",
                "sku_id": sku["sku_id"],
                "location_id": sku["location"],
                "predicted_demand": round(demand, 1),
                "p10": round(demand - spread * 1.5, 1),
                "p50": round(demand, 1),
                "p90": round(demand + spread * 1.5, 1),
                "timestamp": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
            })
        return forecasts

    def decompose_confidence(self, sku_id: str = "") -> ConfidenceDecomposition:
        """
        Calculate the 4-factor confidence decomposition (PRD §9.1).
        
        Components:
        1. Forecast Uncertainty (30%) — P10/P90 spread
        2. Data Quality (20%) — completeness, recency
        3. Model Agreement (25%) — ensemble consensus
        4. Historical Accuracy (25%) — rolling FVA
        """
        forecast_uncertainty = round(random.uniform(0.65, 0.95), 2)
        data_quality = round(random.uniform(0.80, 0.99), 2)
        model_agreement = round(random.uniform(0.70, 0.98), 2)
        historical_accuracy = round(random.uniform(0.72, 0.96), 2)

        components = [
            ConfidenceComponent(
                name="Forecast Uncertainty",
                score=forecast_uncertainty,
                weight=0.30,
                detail=f"P10/P90 spread: ±{round((1 - forecast_uncertainty) * 100, 1)}%"
            ),
            ConfidenceComponent(
                name="Data Quality",
                score=data_quality,
                weight=0.20,
                detail=f"Completeness: {round(data_quality * 100)}% | 0 NaN features"
            ),
            ConfidenceComponent(
                name="Model Consensus",
                score=model_agreement,
                weight=0.25,
                detail=f"{3 + int(model_agreement > 0.85)}/4 models agree"
            ),
            ConfidenceComponent(
                name="Historical Backtest",
                score=historical_accuracy,
                weight=0.25,
                detail=f"12-wk rolling MAPE: {round((1 - historical_accuracy) * 100, 1)}%"
            ),
        ]

        composite = sum(c.score * c.weight for c in components)
        composite = round(composite, 3)

        if composite >= 0.80:
            level = "HIGH"
        elif composite >= 0.60:
            level = "MODERATE"
        else:
            level = "REVIEW_REQUIRED"

        return ConfidenceDecomposition(
            composite_score=composite,
            confidence_level=level,
            components=components,
            auto_approval_eligible=(composite >= 0.85),
        )

    def generate_shap_drivers(self, top_n: int = 5) -> List[DriverAttribution]:
        """Generate mock SHAP feature attribution for a recommendation."""
        selected = random.sample(_SHAP_FEATURES, min(top_n, len(_SHAP_FEATURES)))
        drivers = []
        for feature, direction in selected:
            impact = round(random.uniform(3, 22), 1)
            if direction == "negative":
                impact = -impact
            drivers.append(DriverAttribution(
                feature=feature,
                impact=impact,
                direction=direction,
            ))
        drivers.sort(key=lambda d: abs(d.impact), reverse=True)
        return drivers

    def generate_recommendations(self, count: int = 8) -> List[Dict[str, Any]]:
        """Generate a full set of mock recommendations with confidence decomposition."""
        action_types = ["increase_order", "expedite_shipment", "reallocate_inventory", "reduce_buffer", "switch_supplier"]
        recommendations = []

        for i, sku in enumerate(_SKU_CATALOG[:count]):
            confidence = self.decompose_confidence(sku["sku_id"])
            qty = round(sku["base_demand"] * random.uniform(0.8, 1.3))
            risk = round(sku["base_demand"] * random.uniform(5, 25), 2)

            recommendations.append({
                "id": f"rec-{2026080900 + i}",
                "tenant_id": "mock_tenant_456",
                "forecast_id": f"fc-{2026080900 + i}",
                "action_type": random.choice(action_types),
                "status": "pending",
                "confidence": confidence.model_dump(),
                "sku_id": sku["sku_id"],
                "sku_name": sku["name"],
                "location_id": sku["location"],
                "recommended_quantity": qty,
                "revenue_at_risk": risk,
                "created_at": datetime.utcnow().isoformat(),
            })

        # Sort by revenue at risk descending (highest priority first)
        recommendations.sort(key=lambda r: r["revenue_at_risk"], reverse=True)
        return recommendations


# Singleton
ai_engine = AIEngine()
