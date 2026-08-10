class DecisionService:
    def get_recommendations(self):
        # Exception-based recommendations
        return [
            {
                "id": 1,
                "type": "Stockout Risk",
                "item": "Widget A",
                "confidence_drop": True,
                "status": "PENDING"
            }
        ]
