import json
from datetime import datetime
import os

class FeedbackLoopService:
    """
    Manages the Human-in-the-Loop continuous learning process.
    Collects planner overrides and approvals to form a labeled dataset for retraining.
    """
    def __init__(self, data_dir: str = "data/feedback"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.feedback_file = os.path.join(self.data_dir, "human_feedback.jsonl")
        
    def record_override(self, recommendation_id: str, original_value: float, overridden_value: float, reason: str, user_id: str):
        """
        Record a human override on an AI recommendation.
        """
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "recommendation_id": recommendation_id,
            "type": "override",
            "original_value": original_value,
            "overridden_value": overridden_value,
            "reason": reason,
            "user_id": user_id
        }
        self._append_to_log(feedback)
        
    def record_approval(self, recommendation_id: str, value: float, user_id: str):
        """
        Record a human approval of an AI recommendation (implicit positive feedback).
        """
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "recommendation_id": recommendation_id,
            "type": "approval",
            "value": value,
            "user_id": user_id
        }
        self._append_to_log(feedback)
        
    def _append_to_log(self, data: dict):
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
            
    def get_feedback_stats(self) -> dict:
        """
        Return statistics on human feedback.
        """
        if not os.path.exists(self.feedback_file):
            return {"total_overrides": 0, "total_approvals": 0}
            
        overrides = 0
        approvals = 0
        
        with open(self.feedback_file, 'r') as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                if data['type'] == 'override':
                    overrides += 1
                elif data['type'] == 'approval':
                    approvals += 1
                    
        return {
            "total_overrides": overrides,
            "total_approvals": approvals,
            "override_rate": overrides / (overrides + approvals) if (overrides + approvals) > 0 else 0
        }
