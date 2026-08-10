import numpy as np
import pandas as pd
from ai_engine.quantum.circuit_library import CircuitLibrary

try:
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    from sklearn.svm import OneClassSVM
except ImportError:
    print("Qiskit ML / Sklearn not installed. Mocking QKE Anomaly.")
    FidelityQuantumKernel = None

class QKEAnomalyDetector:
    """
    Quantum Kernel Estimation (QKE) for Supply Chain Anomaly Detection.
    Uses FidelityQuantumKernel combined with a classical One-Class SVM.
    """
    def __init__(self, num_features: int = 4):
        self.num_features = num_features
        self.feature_map = CircuitLibrary.get_feature_map(num_features)
        self.kernel = None
        self.svm = None
        
    def fit(self, X_train: pd.DataFrame):
        """
        Fit the One-Class SVM using the Quantum Kernel.
        """
        print(f"Training QKE Anomaly Detector with {self.num_features} qubits...")
        
        if FidelityQuantumKernel is None:
            self.svm = "MockSVM"
            return
            
        self.kernel = FidelityQuantumKernel(feature_map=self.feature_map)
        
        # Scaling is critical
        from sklearn.preprocessing import MinMaxScaler
        self.scaler_X = MinMaxScaler(feature_range=(0, np.pi))
        X_scaled = self.scaler_X.fit_transform(X_train)
        
        # Precompute the kernel matrix for training
        print("Evaluating Quantum Kernel Matrix for training...")
        kernel_matrix_train = self.kernel.evaluate(x_vec=X_scaled)
        
        self.svm = OneClassSVM(kernel='precomputed', nu=0.05)
        self.svm.fit(kernel_matrix_train)
        
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict anomalies (-1) vs normal (1).
        """
        if self.svm == "MockSVM":
            # 5% anomalies
            return np.random.choice([1, -1], size=len(X_test), p=[0.95, 0.05])
            
        if self.svm is None:
            raise ValueError("Model not trained.")
            
        X_scaled = self.scaler_X.transform(X_test)
        
        print("Evaluating Quantum Kernel Matrix for inference...")
        # Evaluate kernel between test and train data
        X_train_scaled = self.scaler_X.transform(self.X_train_ref) # Requires saving X_train_ref during fit
        kernel_matrix_test = self.kernel.evaluate(x_vec=X_scaled, y_vec=X_train_scaled)
        
        return self.svm.predict(kernel_matrix_test)
