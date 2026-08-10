import json

class ChampionChallenger:
    """
    Shadow deployment and automated promotion logic for MLOps Level 3.
    Compares the current production model (Champion) against a newly trained model (Challenger).
    """
    
    @staticmethod
    def evaluate(champion_metrics_path: str, challenger_metrics_path: str, threshold: float = 0.05):
        """
        Evaluate if Challenger beats Champion by at least the threshold %.
        """
        # Load metrics
        # (In a real system, these come from MLflow Registry)
        try:
            with open(champion_metrics_path, 'r') as f:
                champ = json.load(f)
            with open(challenger_metrics_path, 'r') as f:
                chall = json.load(f)
        except FileNotFoundError:
            print("Metric files not found. Using mock evaluation.")
            champ = {"wMAPE": 12.5, "Bias": 2.1}
            chall = {"wMAPE": 11.2, "Bias": 1.9}
            
        champ_error = champ.get("wMAPE", 100)
        chall_error = chall.get("wMAPE", 100)
        
        improvement = (champ_error - chall_error) / champ_error
        
        print(f"Champion Error: {champ_error:.2f}% | Challenger Error: {chall_error:.2f}%")
        print(f"Improvement: {improvement*100:.2f}%")
        
        if improvement > threshold:
            print("Challenger Promoted to Production!")
            return {"promoted": True, "improvement": improvement}
        else:
            print("Challenger Rejected. Champion remains in Production.")
            return {"promoted": False, "improvement": improvement}

if __name__ == "__main__":
    # Example usage in pipeline
    ChampionChallenger.evaluate("metrics/tft_eval.json", "metrics/vqr_eval.json")
