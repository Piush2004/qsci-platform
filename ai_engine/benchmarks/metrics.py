class BenchmarkMetrics:
    """
    Standard metrics for evaluating both Quantum and Classical algorithms.
    """
    
    @staticmethod
    def collect_quantum_metrics(qpu_time_ms: float, circuit_depth: int, cnot_count: int, qubits_used: int):
        return {
            "qpu_time_ms": qpu_time_ms,
            "circuit_depth": circuit_depth,
            "cnot_count": cnot_count,
            "qubits_used": qubits_used
        }
        
    @staticmethod
    def collect_classical_metrics(cpu_time_ms: float, memory_mb: float):
        return {
            "cpu_time_ms": cpu_time_ms,
            "memory_mb": memory_mb
        }
