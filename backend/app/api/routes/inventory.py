from fastapi import APIRouter

router = APIRouter()

@router.get("/inventory")
def get_inventory():
    return {
        "inventory_health": "Good",
        "items": [
            {"sku": "WIDGET-A", "safety_stock": 500, "reorder_point": 1200, "current_stock": 1500}
        ]
    }
