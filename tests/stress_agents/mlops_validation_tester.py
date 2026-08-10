import numpy as np

class MLOpsValidationTester:
    """Agent 3: MLOps Validation Tester (Drift & Promotion)"""
    
    def test_drift_monitor(self):
        print("🕵️ MLOpsValidationTester: Injecting shifted distributions into Feature Store...")
        # Simulate Drift
        baseline = np.random.normal(loc=100, scale=15, size=1000)
        shifted = np.random.normal(loc=120, scale=20, size=1000) # Covariate Shift
        
        from mlops.drift_monitor import DriftMonitor
        psi = DriftMonitor.calculate_psi(baseline, shifted)
        
        if psi > 0.2:
            print(f"✅ MLOpsValidationTester: Drift correctly detected (PSI: {psi:.3f} > 0.2). Triggering retrain.")
            return True
        else:
            print(f"❌ MLOpsValidationTester: Failed to detect severe drift! PSI: {psi:.3f}")
            return False

if __name__ == "__main__":
    agent = MLOpsValidationTester()
    agent.test_drift_monitor()
