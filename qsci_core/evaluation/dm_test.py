"""Diebold-Mariano test for comparing two forecasts' accuracy.

Tests H0: the two forecasts have equal expected loss, against a two-sided
alternative. Uses a Newey-West (HAC) variance estimate on the loss
differential series to account for autocorrelation in multi-step-ahead
forecast errors, per Diebold & Mariano (1995) and the Harvey/Leybourne/
Newbold (1997) small-sample correction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class DMTestResult:
    statistic: float
    p_value: float
    mean_loss_diff: float
    n_obs: int
    h_horizon: int
    alternative: str = "two-sided: forecast errors are NOT equal"
    significance_level: float = 0.05
    reliable: bool = True
    reliability_note: str = ""

    @property
    def significant(self) -> bool:
        return self.reliable and self.p_value < self.significance_level

    def interpretation(self) -> str:
        if not self.reliable:
            return f"UNRELIABLE: {self.reliability_note}"
        if self.significant:
            direction = "forecast A" if self.mean_loss_diff < 0 else "forecast B"
            return (
                f"Reject H0 at alpha={self.significance_level}: the two forecasts' accuracy "
                f"differs significantly (DM={self.statistic:.3f}, p={self.p_value:.4f}). "
                f"{direction} had the lower average loss."
            )
        return (
            f"Fail to reject H0 at alpha={self.significance_level}: no significant accuracy "
            f"difference detected (DM={self.statistic:.3f}, p={self.p_value:.4f})."
        )


def diebold_mariano_test(
    y_true: np.ndarray,
    y_pred_a: np.ndarray,
    y_pred_b: np.ndarray,
    h_horizon: int = 1,
    loss: str = "squared",
    significance_level: float = 0.05,
) -> DMTestResult:
    """Compare forecast A vs. forecast B on the same actuals.

    Negative mean_loss_diff means A had lower average loss than B.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred_a = np.asarray(y_pred_a, dtype=float)
    y_pred_b = np.asarray(y_pred_b, dtype=float)

    if not (y_true.shape == y_pred_a.shape == y_pred_b.shape):
        raise ValueError(f"shape mismatch: y_true={y_true.shape}, y_pred_a={y_pred_a.shape}, y_pred_b={y_pred_b.shape}")
    n = len(y_true)
    if n == 0:
        raise ValueError("empty input")

    if loss == "squared":
        loss_a = (y_true - y_pred_a) ** 2
        loss_b = (y_true - y_pred_b) ** 2
    elif loss == "absolute":
        loss_a = np.abs(y_true - y_pred_a)
        loss_b = np.abs(y_true - y_pred_b)
    else:
        raise ValueError(f"loss must be 'squared' or 'absolute', got {loss!r}")

    d = loss_a - loss_b
    d_mean = float(np.mean(d))

    if n < 10:
        return DMTestResult(
            statistic=float("nan"), p_value=float("nan"), mean_loss_diff=d_mean, n_obs=n, h_horizon=h_horizon,
            significance_level=significance_level, reliable=False,
            reliability_note=f"only {n} observations (<10) — the DM test's asymptotic normality assumption is unreliable at this sample size.",
        )

    # Newey-West long-run variance of the loss differential, with (h-1) lags
    # to account for the autocorrelation induced by h-step-ahead forecasts.
    gamma_0 = float(np.var(d, ddof=0))
    var_d = gamma_0
    for lag in range(1, h_horizon):
        if lag >= n:
            break
        gamma_lag = float(np.mean((d[lag:] - d_mean) * (d[:-lag] - d_mean)))
        var_d += 2 * gamma_lag

    if var_d <= 0:
        return DMTestResult(
            statistic=float("nan"), p_value=float("nan"), mean_loss_diff=d_mean, n_obs=n, h_horizon=h_horizon,
            significance_level=significance_level, reliable=False,
            reliability_note="estimated long-run variance of the loss differential is non-positive — forecasts may be identical or the sample too short/autocorrelated for a stable estimate.",
        )

    dm_stat = d_mean / np.sqrt(var_d / n)

    # Harvey, Leybourne & Newbold (1997) small-sample correction
    correction = np.sqrt((n + 1 - 2 * h_horizon + h_horizon * (h_horizon - 1) / n) / n)
    dm_stat_corrected = dm_stat * correction

    p_value = 2 * (1 - stats.t.cdf(np.abs(dm_stat_corrected), df=n - 1))

    return DMTestResult(
        statistic=float(dm_stat_corrected), p_value=float(p_value), mean_loss_diff=d_mean,
        n_obs=n, h_horizon=h_horizon, significance_level=significance_level, reliable=True,
    )
