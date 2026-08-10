from fastapi import APIRouter

router = APIRouter()

@router.get("/risk")
def get_risk():
    return {
        "overall_risk": "Medium",
        "supplier_risk": [
            {"supplier_id": "SUP-01", "risk_score": 0.8, "factor": "Geopolitical"}
        ],
        "stockout_risk": [
            {"sku": "WIDGET-B", "probability": 0.6}
        ]
    }
