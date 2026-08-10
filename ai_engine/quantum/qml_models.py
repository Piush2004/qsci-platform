import time
import tracemalloc
import sys
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def track_quantum_metrics(func):
    def wrapper(self, *args, **kwargs):
        tracemalloc.start()
        start_time = time.time()
        
        result = func(self, *args, **kwargs)
        
        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        duration = end_time - start_time
        peak_memory_mb = peak_memory / (1024 * 1024)
        
        if isinstance(result, tuple):
            return result + (duration, peak_memory_mb)
        return result, duration, peak_memory_mb
    return wrapper

class QuantumRegressionModels:
    """For demand forecasting (regression tasks). Uses VQR."""
    def __init__(self):
        self.model_type = 'regression'
        self.model_obj = None
        self.qiskit_available = True
        try:
            from qiskit_machine_learning.algorithms import VQR
            from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
            from qiskit_algorithms.optimizers import COBYLA
            self.VQR = VQR
            self.ZZFeatureMap = ZZFeatureMap
            self.RealAmplitudes = RealAmplitudes
            self.COBYLA = COBYLA
        except ImportError:
            self.qiskit_available = False
            print("Qiskit not installed. Quantum regression models will be skipped.")
            
    def train_and_evaluate(self, X_train, y_train, X_test, y_test):
        if not self.qiskit_available:
            return None
            
        # Downsample for simulation feasibility
        X_tr = np.array(X_train)[:50]
        y_tr = np.array(y_train)[:50]
        X_te = np.array(X_test)[:20]
        y_te = np.array(y_test)[:20]
        
        num_features = X_tr.shape[1] if len(X_tr.shape) > 1 else 1
        
        feature_map = self.ZZFeatureMap(feature_dimension=num_features, reps=1)
        ansatz = self.RealAmplitudes(num_qubits=num_features, reps=1)
        optimizer = self.COBYLA(maxiter=20)
        
        self.model_obj = self.VQR(
            feature_map=feature_map,
            ansatz=ansatz,
            optimizer=optimizer
        )
        
        tracemalloc.start()
        start_time = time.time()
        self.model_obj.fit(X_tr, y_tr)
        train_time = time.time() - start_time
        _, train_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        tracemalloc.start()
        start_time = time.time()
        predictions = self.model_obj.predict(X_te)
        infer_time = time.time() - start_time
        _, infer_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'RMSE': np.sqrt(mean_squared_error(y_te, predictions)),
            'MAE': mean_absolute_error(y_te, predictions),
            'MAPE': mean_absolute_percentage_error(y_te, predictions),
            'R2': r2_score(y_te, predictions),
            'Training Time (s)': train_time,
            'Inference Time (s)': infer_time,
            'Memory Usage (MB)': max(train_mem, infer_mem) / (1024 * 1024),
            'Model Size (KB)': sys.getsizeof(self.model_obj) / 1024,
            'model_type': self.model_type,
            'model_obj': self.model_obj,
            'circuit_depth': ansatz.depth() + feature_map.depth(),
            'num_qubits': num_features,
            'optimizer_name': 'COBYLA',
            'num_shots': 1024,
            'backend_name': 'aer_simulator'
        }

class QuantumClassificationModels:
    """For inventory classification tasks. Uses QSVM and VQC."""
    def __init__(self):
        self.model_type = 'classification'
        self.model_obj = None
        self.qiskit_available = True
        try:
            from qiskit_machine_learning.algorithms import VQC, QSVC
            from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
            from qiskit_algorithms.optimizers import COBYLA
            self.VQC = VQC
            self.QSVC = QSVC
            self.ZZFeatureMap = ZZFeatureMap
            self.RealAmplitudes = RealAmplitudes
            self.COBYLA = COBYLA
        except ImportError:
            self.qiskit_available = False
            print("Qiskit not installed. Quantum classification models will be skipped.")

    def train_and_evaluate(self, X_train, y_train, X_test, y_test, use_vqc=True):
        if not self.qiskit_available:
            return None
            
        X_tr = np.array(X_train)[:50]
        y_tr = np.array(y_train)[:50]
        X_te = np.array(X_test)[:20]
        y_te = np.array(y_test)[:20]
        
        num_features = X_tr.shape[1] if len(X_tr.shape) > 1 else 1
        feature_map = self.ZZFeatureMap(feature_dimension=num_features, reps=1)
        
        if use_vqc:
            ansatz = self.RealAmplitudes(num_qubits=num_features, reps=1)
            optimizer = self.COBYLA(maxiter=20)
            self.model_obj = self.VQC(
                feature_map=feature_map,
                ansatz=ansatz,
                optimizer=optimizer
            )
            model_name = 'VQC'
            depth = ansatz.depth() + feature_map.depth()
        else:
            from qiskit_machine_learning.kernels import FidelityQuantumKernel
            kernel = FidelityQuantumKernel(feature_map=feature_map)
            self.model_obj = self.QSVC(quantum_kernel=kernel)
            model_name = 'QSVC'
            depth = feature_map.depth()

        tracemalloc.start()
        start_time = time.time()
        self.model_obj.fit(X_tr, y_tr)
        train_time = time.time() - start_time
        _, train_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        tracemalloc.start()
        start_time = time.time()
        predictions = self.model_obj.predict(X_te)
        infer_time = time.time() - start_time
        _, infer_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'Accuracy': accuracy_score(y_te, predictions),
            'Precision': precision_score(y_te, predictions, average='weighted', zero_division=0),
            'Recall': recall_score(y_te, predictions, average='weighted', zero_division=0),
            'F1': f1_score(y_te, predictions, average='weighted', zero_division=0),
            'Training Time (s)': train_time,
            'Inference Time (s)': infer_time,
            'Memory Usage (MB)': max(train_mem, infer_mem) / (1024 * 1024),
            'Model Size (KB)': sys.getsizeof(self.model_obj) / 1024,
            'model_type': self.model_type,
            'model_obj': self.model_obj,
            'model_name': model_name,
            'circuit_depth': depth,
            'num_qubits': num_features,
            'optimizer_name': 'COBYLA' if use_vqc else 'None',
            'num_shots': 1024,
            'backend_name': 'aer_simulator'
        }
