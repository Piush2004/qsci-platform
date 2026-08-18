import numpy as np
import pytest

from qsci_core.forecasting.quantum.feature_reduction import reduce_features_pca


def _data(n_train=30, n_test=10, n_features=20, seed=0):
    rng = np.random.default_rng(seed)
    X_train = rng.normal(0, 1, (n_train, n_features))
    X_test = rng.normal(0, 1, (n_test, n_features))
    return X_train, X_test


def test_reduce_features_output_shape():
    X_train, X_test = _data()
    result = reduce_features_pca(X_train, X_test, n_components=4)
    assert result.X_train_reduced.shape == (30, 4)
    assert result.X_test_reduced.shape == (10, 4)
    assert result.n_components == 4


@pytest.mark.parametrize("n", [4, 8, 12, 16])
def test_reduce_features_all_valid_n_components(n):
    X_train, X_test = _data(n_train=40, n_test=10, n_features=20)
    result = reduce_features_pca(X_train, X_test, n_components=n)
    assert result.X_train_reduced.shape[1] == n
    assert len(result.explained_variance_ratio) == n


def test_reduce_features_fit_only_on_train_not_test():
    # Perturbing X_test must not change the fitted transform applied to X_train.
    X_train, X_test = _data()
    result_a = reduce_features_pca(X_train, X_test, n_components=4)
    X_test_perturbed = X_test + 1000  # wildly different test distribution
    result_b = reduce_features_pca(X_train, X_test_perturbed, n_components=4)
    np.testing.assert_allclose(result_a.X_train_reduced, result_b.X_train_reduced)


def test_reduce_features_empty_raises():
    X_train, X_test = _data()
    with pytest.raises(ValueError):
        reduce_features_pca(np.empty((0, 20)), X_test, n_components=4)


def test_reduce_features_nan_raises():
    X_train, X_test = _data()
    X_train[0, 0] = np.nan
    with pytest.raises(ValueError):
        reduce_features_pca(X_train, X_test, n_components=4)


def test_reduce_features_mismatched_feature_dims_raises():
    X_train, X_test = _data(n_features=20)
    with pytest.raises(ValueError):
        reduce_features_pca(X_train, X_test[:, :10], n_components=4)


def test_reduce_features_n_components_exceeds_available_features_raises():
    X_train, X_test = _data(n_features=10)
    with pytest.raises(ValueError):
        reduce_features_pca(X_train, X_test, n_components=16)


def test_reduce_features_n_components_exceeds_n_samples_raises():
    X_train, X_test = _data(n_train=3, n_features=20)
    with pytest.raises(ValueError):
        reduce_features_pca(X_train, X_test, n_components=4)


def test_reduce_features_invalid_n_components_raises():
    X_train, X_test = _data()
    with pytest.raises(ValueError):
        reduce_features_pca(X_train, X_test, n_components=0)


def test_reduce_features_reproducible():
    X_train, X_test = _data()
    result_a = reduce_features_pca(X_train, X_test, n_components=4)
    result_b = reduce_features_pca(X_train, X_test, n_components=4)
    np.testing.assert_allclose(result_a.X_train_reduced, result_b.X_train_reduced)
    np.testing.assert_allclose(result_a.explained_variance_ratio, result_b.explained_variance_ratio)
