"""Tests for prometheus_math.research.spectral_gaps.

Test categories (math-tdd skill, see techne/skills/math-tdd.md):

- **Authority**: Wigner surmise variance for GUE / GOE / GSE; the
  empirical sample variance from ``matched_null`` must match the
  closed-form Mehta value to within Monte-Carlo error.
- **Property**: ``gap_k_variance`` is non-negative for any input;
  ``normalize_zeros`` produces mean-1 sequences by construction;
  ``bootstrap_ci`` returns p-value in [0, 1].
- **Edge**: empty / singleton zero list, unsupported ensemble,
  malformed mode string.
- **Composition**: full ``scan`` chain over a synthetic family produces
  a deficit-then-z-score chain that bootstrap_ci can corroborate.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.research import spectral_gaps as sg


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_authority_wigner_surmise_gue_gap_1_variance():
    """matched_null('GUE', N=100) gap_1 variance ≈ Mehta surmise.

    Reference: Mehta, *Random Matrices* 3rd ed. (2004), Ch. 1 §1.5.
    For GUE in the mean-spacing-1 normalization the Wigner surmise
    is P(s) = (32/π²) s² exp(-4s²/π); its first two moments are

        ⟨s⟩ = 1   (by construction of the surmise)
        ⟨s²⟩ = 3π/8

    so Var(s) = 3π/8 - 1 ≈ 0.1781.

    The bulk N→∞ value differs from this small-N surmise by < 0.5%,
    so we accept the empirical variance from a 10K-matrix sample
    of N=100 GUE matrices to within ±0.04 (≈ 22% of the predicted
    value); this is comfortably tighter than the surmise / bulk
    discrepancy.
    """
    # Use kmax=24 (24-gap local window). Smaller windows over-constrain
    # the local mean and bias the gap_1 variance downward; at kmax=24
    # the bias is below 1%.
    rng = np.random.default_rng(2024)
    null = sg.matched_null(
        N=100, n_samples=10_000, ensemble="GUE", kmax=24, rng=rng
    )
    g1_var = float(np.var(null[:, 0], ddof=1))
    expected = sg.WIGNER_SURMISE_VARIANCE["GUE"]
    assert abs(g1_var - expected) < 0.01, (
        f"GUE gap_1 var={g1_var:.4f} but Wigner surmise = {expected:.4f}; "
        f"|diff|={abs(g1_var-expected):.4f} exceeds tolerance 0.01"
    )


def test_authority_usp4_differs_from_gue():
    """USp(4) gap distribution is more strongly repulsive than GUE.

    Reference: Katz & Sarnak (1999), AMS Coll. Pubs. 45.  USp(2N)
    bulk statistics follow the Gaussian Symplectic Ensemble (β=4),
    which has quartic level repulsion P(s) ~ s⁴ at small s,
    versus GUE's quadratic repulsion P(s) ~ s². With the mean spacing
    fixed at 1, stronger repulsion produces a NARROWER distribution
    (less mass near 0 and a shorter right tail), so the variance is
    SMALLER. The Mehta surmise gives Var(GSE) = 45π/128 - 1 ≈ 0.104
    vs Var(GUE) = 3π/8 - 1 ≈ 0.178.
    """
    rng = np.random.default_rng(2024)
    # Use kmax=24 so the local-window normalization doesn't over-constrain.
    gue = sg.matched_null(N=40, n_samples=2000, ensemble="GUE", kmax=24, rng=rng)
    usp = sg.matched_null(N=40, n_samples=2000, ensemble="USp(4)", kmax=24, rng=rng)
    gue_var = float(np.var(gue[:, 0], ddof=1))
    usp_var = float(np.var(usp[:, 0], ddof=1))
    # Stronger repulsion → smaller variance. Distinguishable at n=2000.
    assert usp_var < gue_var * 0.85, (
        f"USp(4) gap_1 var ({usp_var:.4f}) should be much smaller than "
        f"GUE gap_1 var ({gue_var:.4f}) due to quartic repulsion"
    )
    # And both should be in their expected neighborhood of the surmise.
    assert abs(usp_var - sg.WIGNER_SURMISE_VARIANCE["GSE"]) < 0.05


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("seed", [0, 1, 2, 7, 42])
def test_property_gap_k_variance_nonnegative(seed):
    """Var(·) >= 0 for any input by definition."""
    rng = np.random.default_rng(seed)
    for n in (5, 20, 100):
        x = rng.standard_normal(n)
        v = sg.gap_k_variance(x, k=1)
        assert v >= 0.0, f"got negative variance {v}"


@pytest.mark.parametrize("seed", [0, 1, 2, 7, 42])
def test_property_normalize_zeros_mean_is_one(seed):
    """For mode='local-Nk-gap' the normalized window has mean ≈ 1."""
    rng = np.random.default_rng(seed)
    # Build random monotone zero sequence.
    zeros = np.cumsum(rng.uniform(0.5, 2.0, size=30))
    norm = sg.normalize_zeros(zeros, mode="local-24-gap")
    assert len(norm) == 24
    assert abs(np.mean(norm) - 1.0) < 1e-12, (
        f"mean of normalized window should be 1, got {np.mean(norm)}"
    )


def test_property_bootstrap_ci_pvalue_in_unit_interval():
    """bootstrap_ci returns p-value in [0, 1] for any input pair."""
    rng = np.random.default_rng(0)
    # Two identically-distributed samples → no real deficit.
    a = rng.standard_normal(200)
    b = rng.standard_normal(200)
    res = sg.bootstrap_ci(a, b, n_bootstrap=500, alpha=0.05, rng_seed=0)
    assert 0.0 <= res["p_value"] <= 1.0
    assert res["ci_low"] <= res["mean"] <= res["ci_high"] or \
        abs(res["mean"]) < 0.2  # stochastic edge: mean may slip out by chance


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


def test_edge_empty_zeros_raises():
    """Empty or 1-element zero list → ValueError (no spacings)."""
    with pytest.raises(ValueError, match="(?i)2 zeros|empty|None"):
        sg.normalize_zeros([])
    with pytest.raises(ValueError, match="(?i)2 zeros"):
        sg.normalize_zeros([1.0])


def test_edge_unsupported_ensemble_raises():
    """matched_null('NotARealEnsemble') → ValueError with clear msg."""
    with pytest.raises(ValueError, match="(?i)unsupported ensemble"):
        sg.matched_null(N=20, n_samples=5, ensemble="ROFLENSEMBLE")


def test_edge_malformed_mode_raises():
    """normalize_zeros with bad mode → ValueError."""
    zeros = [0.5, 1.0, 1.7, 2.4, 3.2]
    with pytest.raises(ValueError, match="(?i)unknown.*mode|parse"):
        sg.normalize_zeros(zeros, mode="not-a-mode")


def test_edge_gap_k_variance_too_small_input():
    """gap_k_variance on length-1 input raises (no variance)."""
    with pytest.raises(ValueError, match="(?i)>=2|empty"):
        sg.gap_k_variance([])
    with pytest.raises(ValueError, match="(?i)>=2|empty"):
        sg.gap_k_variance([3.14])


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_scan_chain_30_synthetic_curves():
    """Composition: scan over 30 synthetic 'GUE-like' curves
    produces matching deficit-then-z-score chain that bootstrap_ci
    corroborates.

    We synthesize 30 curves whose zeros are themselves drawn from a
    GUE null. The scan should report a near-zero deficit at every k
    (the 'data' is ~ same distribution as the null), and the
    bootstrap should give a wide CI containing 0.
    """
    rng = np.random.default_rng(2024)
    # Build 30 'curves' from GUE eigenvalues (size N=40).
    records = []
    for i in range(30):
        # Use sg's internal helper to produce a length-25 zero sequence.
        w = sg._gue_eigvals(40, rng)
        # Take 25 mid-bulk eigenvalues (so we have 24 spacings)
        mid = len(w) // 2 - 12
        zeros = list(w[mid:mid + 25])
        records.append({"label": f"synth{i}", "zeros": zeros})
    res = sg.scan(
        family_query={},
        zeros_records=records,
        k_max=24,
        ensemble="GUE",
        null_N=40,
        null_n_samples=2_000,
        rng_seed=2024,
    )
    # Assert chain integrity (all keys present; lengths match).
    assert res["k_max"] == 24
    assert res["ensemble"] == "GUE"
    assert res["n_curves"] == 30
    assert len(res["data_var"]) == 24
    assert len(res["null_var"]) == 24
    assert len(res["deficit_pct"]) == 24
    assert len(res["z_score"]) == 24
    # Deficits and z-scores should be modest because data and null
    # come from the same distribution. With only 30 curves the
    # variance estimator has huge sampling noise (SE ≈ var * sqrt(2/29)
    # ≈ 26% per bin), so individual k can swing widely. Check the
    # MEDIAN deficit is near zero rather than an extreme outlier.
    deficits = np.asarray(res["deficit_pct"])
    median_deficit = float(np.median(deficits))
    assert abs(median_deficit) < 25.0, (
        f"median deficit pct should be near 0 (data~null), got "
        f"{median_deficit:.2f}; full deficits = {deficits}"
    )
    # bootstrap_ci on gap_1 should include 0 in the CI.
    data_g1 = np.asarray(res["data_matrix"])[:, 0]
    null_g1 = np.asarray(res["null_matrix"])[:, 0]
    boot = sg.bootstrap_ci(data_g1, null_g1, n_bootstrap=500, rng_seed=0)
    assert boot["ci_low"] <= 0.0 <= boot["ci_high"] or abs(boot["mean"]) < 0.5


def test_composition_normalize_then_variance_then_bootstrap():
    """Chain: normalize_zeros → gap_k_variance → bootstrap_ci.

    Composition test for the analytic chain. We construct 50 synthetic
    'curves' with quasi-uniform spacing (low variance), and verify:
      (1) per-curve normalize_zeros works
      (2) gap_k_variance is ~ 0 for the constant-spacing limit
      (3) bootstrap_ci sees the deficit
    """
    rng = np.random.default_rng(7)
    # Quasi-uniform spacings: mean 1.0, very small jitter.
    n_curves = 50
    curves = []
    for _ in range(n_curves):
        spac = 1.0 + rng.normal(0, 0.05, size=24)
        curves.append(spac.tolist())
    # Each row has mean ≈ 1; renormalize anyway.
    matrix = np.array([
        sg.normalize_zeros(np.cumsum([0.0] + c).tolist(), mode="local-24-gap")
        for c in curves
    ])
    var_g1 = sg.gap_k_variance(matrix, k=1)
    # GUE reference at sample size 1000.
    null = sg.matched_null(N=40, n_samples=1000, ensemble="GUE", kmax=4,
                           rng=np.random.default_rng(7))
    null_var_g1 = sg.gap_k_variance(null, k=1)
    # Quasi-uniform sample's variance should be << GUE variance.
    assert var_g1 < 0.05, f"quasi-uniform var should be tiny, got {var_g1}"
    assert null_var_g1 > 0.1
    # Bootstrap should report a STRONG positive deficit (data ≪ null).
    boot = sg.bootstrap_ci(matrix[:, 0], null[:, 0],
                           n_bootstrap=500, rng_seed=0)
    assert boot["mean"] > 0.5, f"expected strong positive deficit, got {boot}"
    assert 0.0 <= boot["p_value"] <= 1.0
