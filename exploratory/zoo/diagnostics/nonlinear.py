"""Nonlinear descriptor-collapse diagnostics.

Pearson correlation catches linear collapse. It misses:
  - U-shaped / parabolic dependence (Pearson ~= 0, but the axes are
    totally dependent)
  - monotonic nonlinear relationships with heavy tails

This module adds two complementary checks:

  distance_correlation: Szekely-Rizzo-Bakirov. Zero iff the two variables
  are independent; strictly positive under any dependence, linear or not.
  Scale-invariant after normalization. Cost O(n^2) but n is small (250
  per function in our runs), so this is fine.

  knn_mutual_information: Kraskov-Stogbauer-Grassberger (KSG) estimator.
  Directly measures I(X; Y) without assuming distribution form. When
  I(X;Y) ~ H(X) or H(Y), the axes have collapsed (one is a deterministic
  function of the other).

Both are complementary to Pearson, not replacements. A pair flagged by
any of (Pearson, dCor, MI) above their respective thresholds is a
candidate collapsed axis.
"""
from __future__ import annotations
from itertools import combinations
import numpy as np


def distance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Szekely-Rizzo-Bakirov distance correlation. Range [0, 1].

    Zero iff X and Y are independent (under finite-moment assumptions).
    Strictly positive under any dependence, including nonlinear.
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    n = len(x)
    if n < 2 or len(y) != n:
        return 0.0

    # Pairwise distance matrices
    a = np.abs(x[:, None] - x[None, :])
    b = np.abs(y[:, None] - y[None, :])

    # Double-centering
    A = a - a.mean(axis=0, keepdims=True) - a.mean(axis=1, keepdims=True) + a.mean()
    B = b - b.mean(axis=0, keepdims=True) - b.mean(axis=1, keepdims=True) + b.mean()

    dcov2_xy = (A * B).mean()
    dvar2_x = (A * A).mean()
    dvar2_y = (B * B).mean()

    denom = np.sqrt(dvar2_x * dvar2_y)
    if denom <= 0:
        return 0.0
    return float(np.sqrt(max(0.0, dcov2_xy / denom)))


def knn_mutual_information(x: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    """Kraskov-Stogbauer-Grassberger KSG-1 estimator of I(X; Y).

    Returns MI in nats. Reference: Kraskov, Stogbauer, Grassberger,
    "Estimating mutual information," Phys Rev E 69, 066138 (2004).

    Implementation: KSG-1 with Chebyshev (max) distance. For each point,
    find the k-th nearest neighbor in joint (X, Y) space (Chebyshev),
    then count neighbors within that distance in each marginal.
    """
    from scipy.special import digamma
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    n = len(x)
    if n < k + 1 or len(y) != n:
        return 0.0

    # Small jitter to avoid ties (zero-variance descriptors wreck KNN)
    rng = np.random.default_rng(0)
    x_std = x.std() if x.std() > 0 else 1.0
    y_std = y.std() if y.std() > 0 else 1.0
    x = x + rng.normal(0, x_std * 1e-10, n)
    y = y + rng.normal(0, y_std * 1e-10, n)

    # Joint Chebyshev distance
    dx = np.abs(x[:, None] - x[None, :])
    dy = np.abs(y[:, None] - y[None, :])
    joint = np.maximum(dx, dy)
    np.fill_diagonal(joint, np.inf)

    # kth nearest neighbor distance for each point
    eps_k = np.partition(joint, k, axis=1)[:, k - 1]

    # Count in marginals: strictly less than eps_k
    n_x = (dx < eps_k[:, None]).sum(axis=1) - 1  # exclude self
    n_y = (dy < eps_k[:, None]).sum(axis=1) - 1
    n_x = np.maximum(n_x, 0)
    n_y = np.maximum(n_y, 0)

    mi = digamma(k) + digamma(n) - np.mean(digamma(n_x + 1) + digamma(n_y + 1))
    return float(max(0.0, mi))


def nonlinear_audit(cols: dict[str, np.ndarray],
                    dcor_threshold: float = 0.5,
                    mi_threshold: float = 0.5,
                    k_mi: int = 3) -> dict:
    """Compute pairwise distance correlation and KSG MI across descriptor
    columns. Flag pairs above either threshold.

    dcor_threshold = 0.5 is conservative: values above ~0.3 are already
    suggestive on moderate n. 0.5 catches strong dependence reliably.

    mi_threshold is in nats; 0.5 nats ~ 0.72 bits of shared information,
    a fairly tight dependence.
    """
    keys = list(cols)
    dcor_matrix: dict[str, float] = {}
    mi_matrix: dict[str, float] = {}
    flagged: list[dict] = []
    for a, b in combinations(keys, 2):
        x, y = cols[a], cols[b]
        if x.std() == 0 or y.std() == 0:
            dcor_matrix[f"{a}|{b}"] = 0.0
            mi_matrix[f"{a}|{b}"] = 0.0
            continue
        # Standardize for scale-invariance of dCor (already scale-invariant,
        # but normalization improves numerical conditioning)
        xn = (x - x.mean()) / x.std()
        yn = (y - y.mean()) / y.std()
        d = distance_correlation(xn, yn)
        m = knn_mutual_information(xn, yn, k=k_mi)
        dcor_matrix[f"{a}|{b}"] = d
        mi_matrix[f"{a}|{b}"] = m
        if d >= dcor_threshold or m >= mi_threshold:
            flagged.append({
                "pair": [a, b],
                "distance_correlation": d,
                "ksg_mi_nats": m,
                "triggered_by": (
                    ["dcor"] if d >= dcor_threshold and m < mi_threshold
                    else ["mi"] if m >= mi_threshold and d < dcor_threshold
                    else ["dcor", "mi"]
                ),
            })
    return {
        "distance_correlation_matrix": dcor_matrix,
        "ksg_mi_matrix": mi_matrix,
        "flagged": flagged,
        "dcor_threshold": dcor_threshold,
        "mi_threshold_nats": mi_threshold,
        "k_mi": k_mi,
    }
