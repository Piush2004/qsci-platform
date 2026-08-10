import re

class IntentDetector:
    """
    NLP Intent Detector for the Supply Chain Copilot.
    Routes user natural language queries to the appropriate backend engine
    (Forecasting, Routing, Inventory, Scenario, Graph).
    """
    
    INTENTS = {
        "FORECAST": [r"forecast", r"predict", r"demand", r"sales next", r"what will we sell"],
        "INVENTORY": [r"inventory", r"stock", r"safety stock", r"reorder", r"stockout", r"running out"],
        "ROUTING": [r"route", r"delivery", r"vehicles", r"truck", r"vrp"],
        "SCENARIO": [r"what if", r"scenario", r"simulate", r"if we change"],
        "GRAPH": [r"supplier", r"who supplies", r"where does.*come from", r"impact", r"upstream", r"downstream"]
    }
    
    @staticmethod
    def detect_intent(query: str) -> str:
        """
        Detect the primary intent of the user query.
        Returns the intent string, or "GENERAL" if no specific match is found.
        """
        query_lower = query.lower()
        
        for intent, patterns in IntentDetector.INTENTS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
                    
        return "GENERAL"
        
    @staticmethod
    def extract_entities(query: str) -> dict:
        """
        Extract key entities (SKUs, Locations, Dates) from the query using basic NER or regex.
        """
        entities = {}
        
        # Mocking SKU extraction (e.g., looking for SKU-123 or known product names)
        sku_match = re.search(r'(sku-\d+|iphone|widget|laptop)', query.lower())
        if sku_match:
            entities['sku'] = sku_match.group(1).upper()
            
        # Mocking Location extraction
        loc_match = re.search(r'(new york|berlin|tokyo|warehouse \w)', query.lower())
        if loc_match:
            entities['location'] = loc_match.group(1).title()
            
        return entities
