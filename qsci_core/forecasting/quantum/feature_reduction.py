"""Leakage-safe feature reduction for quantum encoding.

NISQ simulators/hardware can't consume the full classical feature space —
this reduces to N in {4, 8, 12, 16} components via PCA. The scaler and PCA
transform are fit ONLY on the training split; the test split is transformed
with those already-fitted parameters, never refit. This is the standard
leakage-safety rule and is enforced structurally here, not left to the
caller to remember.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

VALID_N_COMPONENTS = (4, 8, 12, 16)


@dataclass(frozen=True)
class FeatureReductionResult:
    X_train_reduced: np.ndarray
    X_test_reduced: np.ndarray
    n_components: int
    explained_variance_ratio: np.ndarray
    method: str = "pca_on_train_only"


def reduce_features_pca(X_train: np.ndarray, X_test: np.ndarray, n_components: int) -> FeatureReductionResult:
    X_train = np.asarray(X_train, dtype=float)
    X_test = np.asarray(X_test, dtype=float)

    if X_train.size == 0 or X_test.size == 0:
        raise ValueError("X_train/X_test must not be empty")
    if np.isnan(X_train).any() or np.isnan(X_test).any():
        raise ValueError("X_train/X_test contain NaN values")
    if X_train.shape[1] != X_test.shape[1]:
        raise ValueError(f"X_train has {X_train.shape[1]} features but X_test has {X_test.shape[1]}")
    if n_components > X_train.shape[1]:
        raise ValueError(f"n_components={n_components} exceeds available features ({X_train.shape[1]})")
    if n_components > X_train.shape[0]:
        raise ValueError(f"n_components={n_components} exceeds number of training samples ({X_train.shape[0]})")
    if n_components < 1:
        raise ValueError(f"n_components must be positive, got {n_components}")

    scaler = StandardScaler().fit(X_train)  # fit on train only
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    pca = PCA(n_components=n_components, random_state=0).fit(X_train_scaled)  # fit on train only
    X_train_reduced = pca.transform(X_train_scaled)
    X_test_reduced = pca.transform(X_test_scaled)

    return FeatureReductionResult(
        X_train_reduced=X_train_reduced,
        X_test_reduced=X_test_reduced,
        n_components=n_components,
        explained_variance_ratio=pca.explained_variance_ratio_,
    )
