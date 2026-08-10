import asyncio
from app.core.events import DomainEventBus, DomainEvents

async def test_domain_event_bus():
    bus = DomainEventBus(use_redis=False)
    await bus.connect()
    
    received_payloads = []
    
    def handler(payload):
        received_payloads.append(payload)
        
    # Subscribe to an event
    bus.subscribe(DomainEvents.FORECAST_CREATED, handler)
    assert DomainEvents.FORECAST_CREATED in bus._handlers
    assert handler in bus._handlers[DomainEvents.FORECAST_CREATED]
    
    # Publish event
    test_payload = {"sku": "SKU-123", "qty": 50}
    await bus.publish(DomainEvents.FORECAST_CREATED, test_payload)
    
    # Verify the event is in the queue and can be dispatched to handlers
    event_data = await bus._queue.get()
    assert event_data["event"] == DomainEvents.FORECAST_CREATED
    assert event_data["payload"] == test_payload
    
    # Manually dispatch for the in-memory queue to test handler invocation
    for h in bus._handlers.get(event_data["event"], []):
        h(event_data["payload"])
        
    assert len(received_payloads) == 1
    assert received_payloads[0] == test_payload
