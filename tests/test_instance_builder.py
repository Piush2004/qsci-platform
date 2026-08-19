import numpy as np
import pytest

from qsci_core.optimization.quantum.instance_builder import STATUS_LABEL, build_derived_instance


def test_derived_instance_labeled_research_not_live():
    di = build_derived_instance("A-n32-k5", 4)
    assert di.status == STATUS_LABEL
    assert "LIVE" not in di.status
    assert "RESEARCH" in di.status


def test_derived_instance_uses_real_source_coordinates():
    di = build_derived_instance("A-n32-k5", 4)
    from qsci_core.data import loaders
    instance, _ = loaders.load_cvrplib_instance("A-n32-k5")
    full_coords = np.asarray(instance["node_coord"], dtype=float)
    # first 4 non-depot customers (index 0 is depot) must match exactly
    np.testing.assert_array_equal(di.coords, full_coords[1:5])


def test_derived_instance_feasible_by_construction():
    for n in (4, 6, 8, 10, 12, 16):
        di = build_derived_instance("A-n32-k5", n)
        assert di.demands.sum() <= di.capacity * di.n_vehicles
        assert np.all(di.demands <= di.capacity)


def test_derived_instance_too_large_raises():
    with pytest.raises(ValueError):
        build_derived_instance("A-n32-k5", 31)  # A-n32-k5 has only 31 customers (32 nodes incl depot)


def test_derived_instance_deterministic_not_random():
    di1 = build_derived_instance("A-n32-k5", 6)
    di2 = build_derived_instance("A-n32-k5", 6)
    np.testing.assert_array_equal(di1.coords, di2.coords)
    np.testing.assert_array_equal(di1.demands, di2.demands)
