import time
import random
import threading
import json

class BackendLoadTester:
    """Agent 1: Backend Load Tester (API & Throughput)"""
    def __init__(self, endpoints: list, concurrency: int = 50):
        self.endpoints = endpoints
        self.concurrency = concurrency
        self.results = {"success": 0, "failures": 0, "latencies": []}

    def _simulate_request(self):
        # Mocking an API request to FastAPI
        start = time.time()
        time.sleep(random.uniform(0.01, 0.1)) # simulated network/processing delay
        
        # 1% chance of failure under load
        if random.random() < 0.01:
            self.results["failures"] += 1
        else:
            self.results["success"] += 1
            
        self.results["latencies"].append(time.time() - start)

    def stress_test(self):
        print(f"🕵️ BackendLoadTester: Commencing stress test with {self.concurrency} concurrent threads...")
        threads = []
        for _ in range(self.concurrency):
            t = threading.Thread(target=self._simulate_request)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        avg_latency = sum(self.results["latencies"]) / len(self.results["latencies"])
        print(f"✅ BackendLoadTester: Completed. {self.results['success']} Success | {self.results['failures']} Fails | {avg_latency*1000:.1f}ms Avg Latency")
        return self.results["failures"] == 0

if __name__ == "__main__":
    agent = BackendLoadTester(["/api/forecast", "/api/recommendations"])
    agent.stress_test()
