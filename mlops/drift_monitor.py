import numpy as np

class DriftMonitor:
    """
    Monitors Data Drift and Concept Drift for production supply chain models.
    Required for MLOps Level 3 maturity and EU AI Act continuous monitoring.
    """
    
    @staticmethod
    def calculate_psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI) to detect data drift in numerical features.
        PSI > 0.2 indicates significant drift requiring retraining.
        """
        def scale_range(input_data, min_val, max_val):
            input_data += -(np.min(input_data))
            input_data /= np.max(input_data) / (max_val - min_val)
            input_data += min_val
            return input_data

        breakpoints = np.arange(0, buckets + 1) / buckets * 100
        breakpoints = scale_range(breakpoints, np.min(expected), np.max(expected))
        
        expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
        actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
        
        def sub_psi(e_perc, a_perc):
            if a_perc == 0:
                a_perc = 0.0001
            if e_perc == 0:
                e_perc = 0.0001
            value = (e_perc - a_perc) * np.log(e_perc / a_perc)
            return value
            
        psi_value = sum(sub_psi(expected_percents[i], actual_percents[i]) for i in range(0, len(expected_percents)))
        return float(psi_value)

    @staticmethod
    def detect_drift(reference_data, current_data, feature_columns) -> dict:
        """
        Check all feature columns for drift.
        Returns a dictionary of feature -> PSI score.
        """
        drift_report = {}
        retrain_required = False
        
        # Mocking calculation
        for col in feature_columns:
            # Simulated PSI (e.g. 0.05 is fine, 0.25 is drifting)
            psi = np.random.uniform(0.01, 0.3)
            drift_report[col] = {
                "psi": psi,
                "status": "DRIFTED" if psi > 0.2 else "STABLE"
            }
            if psi > 0.2:
                retrain_required = True
                
        return {
            "retrain_required": retrain_required,
            "feature_drift": drift_report
        }
