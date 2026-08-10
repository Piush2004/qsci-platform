class ErrorMitigationConfig:
    """
    Configuration manager for IBM Qiskit Runtime V2 Resilience Levels.
    """
    
    @staticmethod
    def get_resilience_level(level: int):
        """
        Returns Qiskit Runtime configuration for the specified level.
        
        Level 0: No mitigation
        Level 1: Readout Error Mitigation (TREX/M3)
        Level 2: Zero Noise Extrapolation (ZNE) + Pauli Twirling
        Level 3: Probabilistic Error Cancellation (PEC)
        """
        if level not in [0, 1, 2, 3]:
            raise ValueError("Resilience level must be 0, 1, 2, or 3.")
            
        config = {"resilience_level": level}
        
        if level == 2:
            config["resilience_options"] = {
                "noise_amplifier": "LocalFoldingAmplifier",
                "extrapolator": "LinearExtrapolator"
            }
            
        return config
