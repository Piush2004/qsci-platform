try:
    from qiskit.circuit.library import ZZFeatureMap, EfficientSU2
except ImportError:
    print("Qiskit not installed. Mocking circuit library.")
    ZZFeatureMap = None
    EfficientSU2 = None

class CircuitLibrary:
    """
    Reusable Quantum Ansatz circuits for QML and QAOA.
    Pre-configured for IBM Heavy-Hex topologies.
    """
    
    @staticmethod
    def get_vqr_ansatz(num_features: int, reps: int = 3):
        """
        Hardware-efficient ansatz for Variational Quantum Regression.
        """
        if EfficientSU2 is None:
            return {"name": "EfficientSU2 (Mock)", "qubits": num_features, "depth": reps * 2}
            
        # Linear entanglement reduces SWAP gate overhead on Heavy-Hex
        return EfficientSU2(num_qubits=num_features, reps=reps, entanglement="linear")
        
    @staticmethod
    def get_feature_map(num_features: int, reps: int = 2):
        """
        Non-linear feature map for data embedding (VQR and QKE).
        """
        if ZZFeatureMap is None:
            return {"name": "ZZFeatureMap (Mock)", "qubits": num_features}
            
        return ZZFeatureMap(feature_dimension=num_features, reps=reps)
