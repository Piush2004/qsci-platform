import json
import logging
from typing import Any, Dict, Callable
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class DomainEventBus:
    """
    A lightweight Domain Event Bus. 
    In production (Phase 1), this wraps Redis Pub/Sub. 
    For local development/mocking, it can use an in-memory asyncio Queue.
    """
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis
        self.redis_client = None
        self._handlers = {}
        self._queue = asyncio.Queue()

    async def connect(self):
        if self.use_redis:
            import redis.asyncio as redis
            self.redis_client = redis.from_url("redis://localhost:6379")
            logger.info("Connected to Redis Event Bus")
        else:
            logger.info("Using in-memory Event Bus")

    async def publish(self, event_name: str, payload: Dict[str, Any]):
        """Publish a domain event to the bus."""
        event_data = {
            "event": event_name,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.use_redis and self.redis_client:
            await self.redis_client.publish(event_name, json.dumps(event_data))
        else:
            await self._queue.put(event_data)
            
        logger.info(f"Published event: {event_name}")

    def subscribe(self, event_name: str, handler: Callable):
        """Subscribe to a domain event."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
        logger.info(f"Subscribed handler to {event_name}")

# Singleton instance
event_bus = DomainEventBus(use_redis=False)

# Standard Domain Events (from PRD Section 5.2)
class DomainEvents:
    FORECAST_CREATED = "ForecastCreated"
    INVENTORY_RISK_DETECTED = "InventoryRiskDetected"
    SUPPLIER_DELAY_REPORTED = "SupplierDelayReported"
    RECOMMENDATION_GENERATED = "RecommendationGenerated"
    RECOMMENDATION_APPROVED = "RecommendationApproved"
    RECOMMENDATION_OVERRIDDEN = "RecommendationOverridden"
    SCENARIO_EXECUTED = "ScenarioExecuted"
    MODEL_RETRAINED = "ModelRetrained"
    DRIFT_DETECTED = "DriftDetected"
