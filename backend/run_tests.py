import asyncio
import sys

from tests.test_models import test_models_relationships
from tests.test_events import test_domain_event_bus

async def main():
    print("Running test_models_relationships...")
    try:
        await test_models_relationships()
        print("test_models_relationships PASSED")
    except Exception as e:
        print(f"test_models_relationships FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("Running test_domain_event_bus...")
    try:
        await test_domain_event_bus()
        print("test_domain_event_bus PASSED")
    except Exception as e:
        print(f"test_domain_event_bus FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
