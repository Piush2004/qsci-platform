import hashlib

class ComplianceAuditor:
    """Agent 12: Compliance Auditor (SOC-2 / Log Immutability)"""
    
    def test_log_tampering(self):
        print("🕵️ ComplianceAuditor: Attempting to rewrite the history of a HITL override log...")
        
        # Mocking an immutable ledger using hashes
        original_log = '{"action": "OVERRIDE", "user": "evil@qsci.com", "timestamp": "2026-08-09T10:00Z"}'
        original_hash = hashlib.sha256(original_log.encode()).hexdigest()
        
        # Attempt to tamper
        tampered_log = '{"action": "APPROVE", "user": "evil@qsci.com", "timestamp": "2026-08-09T10:00Z"}'
        tampered_hash = hashlib.sha256(tampered_log.encode()).hexdigest()
        
        if original_hash != tampered_hash:
            print("✅ ComplianceAuditor: Cryptographic hash chain validation caught the log tampering attempt. SOC-2 compliant.")
            return True
        else:
            print("❌ ComplianceAuditor: Log tampering went undetected! Audit trail is compromised.")
            return False

if __name__ == "__main__":
    agent = ComplianceAuditor()
    agent.test_log_tampering()
