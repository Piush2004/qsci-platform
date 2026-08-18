import numpy as np
import pandas as pd

from qsci_core.data.quality import assess_cvrplib_instance, assess_dataframe, assess_m5


def test_assess_dataframe_flags_missing_and_negative():
    df = pd.DataFrame({"a": [1, 2, np.nan, -4], "b": [0, 0, 0, 1]})
    report = assess_dataframe(df, "toy")
    assert report.status == "LIVE"
    assert report.n_rows == 4
    assert report.missing_pct["a"] == 25.0
    assert report.negative_value_counts["a"] == 1
    assert report.zero_inflation_pct["b"] == 75.0


def test_assess_dataframe_empty():
    df = pd.DataFrame({"a": []})
    report = assess_dataframe(df, "empty")
    assert report.n_rows == 0
    assert report.missing_pct == {}


def test_assess_m5_detects_negative_sales_and_date_range():
    sales = pd.DataFrame({
        "id": ["item_1", "item_2"],
        "item_id": ["item_1", "item_2"],
        "d_1": [3, -1],
        "d_2": [0, 0],
    })
    calendar = pd.DataFrame({"date": pd.to_datetime(["2011-01-29", "2011-01-30"])})
    prices = pd.DataFrame({"sell_price": [9.99, -1.0, np.nan]})

    report = assess_m5(sales, calendar, prices)
    assert report.negative_value_counts["unit_sales (all d_ cols)"] == 1
    assert report.negative_value_counts["sell_price"] == 1
    assert report.date_range == ("2011-01-29", "2011-01-30")
    assert report.date_gaps == 0


def test_assess_cvrplib_instance_flags_capacity_violation():
    instance = {
        "node_coord": np.array([[0, 0], [1, 1], [2, 2]]),
        "demand": np.array([0, 5, 20]),
        "capacity": 10,
    }
    report = assess_cvrplib_instance(instance, name="toy")
    assert report.n_rows == 3
    assert "exceed vehicle capacity" in report.notes[0]
