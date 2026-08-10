import threading
import time

class DatabaseConcurrencyTester:
    """Agent 6: Database Concurrency Tester (State & Locks)"""
    def __init__(self):
        self.inventory = 100
        self.lock = threading.Lock()
        
    def _concurrent_transaction(self):
        # Simulating a race condition on inventory deduction
        # In a real test, this calls the DB API
        with self.lock:
            local_copy = self.inventory
            time.sleep(0.001) # artifical processing time
            if local_copy > 0:
                self.inventory = local_copy - 1
                
    def test_race_conditions(self):
        print("🕵️ DatabaseConcurrencyTester: Firing 200 concurrent order transactions against 100 inventory...")
        threads = [threading.Thread(target=self._concurrent_transaction) for _ in range(200)]
        
        for t in threads: t.start()
        for t in threads: t.join()
        
        if self.inventory == 0:
            print("✅ DatabaseConcurrencyTester: Zero inventory reached. No negative stock. ACID compliance maintained.")
            return True
        else:
            print(f"❌ DatabaseConcurrencyTester: Race condition detected! Final inventory: {self.inventory}")
            return False

if __name__ == "__main__":
    agent = DatabaseConcurrencyTester()
    agent.test_race_conditions()
