# Quantum SupplyChain Intelligence (QSCI)
## Technical Report & Research Summary

### 1. Abstract
The Quantum SupplyChain Intelligence (QSCI) platform introduces an enterprise-grade Decision Intelligence framework that bridges predictive Machine Learning with prescriptive Operations Research. Crucially, QSCI incorporates a **Hybrid Intelligence Layer** that allows for side-by-side benchmarking of Classical production models (XGBoost, Random Forest, ARIMA) against exploratory Quantum Machine Learning (QML) models (Variational Quantum Regressor via Qiskit). This architecture isolates experimental quantum workloads from mission-critical business systems while enabling academic evaluation of quantum feature spaces in high-volatility environments.

### 2. Multi-Agent Framework Architecture
QSCI leverages a modular, agent-based architecture to mimic enterprise supply chain operations:
- **Demand Agent:** Autonomously executes the Adaptive Model Selection Engine to forecast demand.
- **Inventory Agent:** Translates demand into stock constraints and monitors reorder points.
- **Optimization Agent:** Applies operations research (EOQ, Linear Programming) to optimize constraints.
- **Quantum Agent:** Manages execution and tracking of Qiskit circuits, pushing metrics to the Research Benchmark Portal.
- **Executive Agent:** Consolidates data into business outcomes (holding cost, savings) and presents actionable insights to a human-in-the-loop.

### 3. Business Rules and Decision Intelligence
While predictive ML forms the foundation, real-world supply chain management requires strict adherence to non-ML business rules. QSCI implements a **Business Rules Engine** that evaluates state conditions (e.g., supplier delay > 5 days AND inventory < safety stock) to generate prescriptive overrides.

These rules feed into the **Business Value Assessment Engine**, which estimates financial impact (Expected Savings vs Naive Heuristic) and calculates a Recommendation Confidence score based on forecast reliability and risk level.

### 4. Human-in-the-Loop (HITL) Execution
Decisions are not automated blindly. The Executive Agent structures a `PENDING_REVIEW` payload displayed on the Executive Control Tower Dashboard. Planners can review the AI's logic, confidence score, and expected savings before choosing to APPROVE, MODIFY, or REJECT the action. This mirrors production deployments in systems like SAP IBP or Blue Yonder.

### 5. Quantum Research Benchmarking
The platform uses **MLflow** to track and compare Classical vs. Quantum models on identical dataset splits.
Preliminary architectures utilize `ZZFeatureMap` and `RealAmplitudes` ansatz to construct a Variational Quantum Regressor. The **Research Benchmark Portal** UI exposes RMSE, MAPE, and Inference Times, allowing researchers to evaluate when quantum algorithms might offer a comparative advantage (e.g., during severe demand spikes with highly complex non-linear correlations) versus when classical algorithms remain strictly superior.

### 6. Conclusion
QSCI represents a state-of-the-art methodology for integrating exploratory quantum research into a robust, enterprise-ready software ecosystem. By emphasizing business value, prescriptive analytics, and strict Human-in-the-Loop workflows, it successfully grounds advanced AI/QML in practical, real-world applicability.
