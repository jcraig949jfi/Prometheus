"""Synthetic-control tests for catalog_profile.

Per Erebos v3 Phase 0 ITER-22. Validates data-driven threshold
calibration on the Mahler catalog (real data) and primitive
correctness via synthetic inputs.
"""
from __future__ import annotations

import pickle
import pytest

from prometheus_math.databases._catalog_profile import (
    CatalogProfile,
    UnknownDomainError,
    _bootstrap_ci,
    _median_pairwise_gap,
    _percentiles,
    _silverman_bandwidth,
    bootstrap_ci_for,
    catalog_profile,
    clear_runtime_cache,
    epsilon_band_for,
    known_domains,
    percentile_threshold_for,
)


# ---------------------------------------------------------------------
# Primitive correctness
# ---------------------------------------------------------------------

def test_median_pairwise_gap_uniform_sequence():
    """Uniform 0, 1, 2, ..., 9 has all gaps = 1; median = 1."""
    assert _median_pairwise_gap([float(i) for i in range(10)]) == 1.0


def test_median_pairwise_gap_handles_unsorted():
    """Input order doesn't matter; sort internally."""
    assert _median_pairwise_gap([5.0, 1.0, 3.0, 2.0, 4.0]) == 1.0


def test_median_pairwise_gap_too_few_values():
    assert _median_pairwise_gap([1.5]) == 0.0
    assert _median_pairwise_gap([]) == 0.0


def test_percentiles_uniform_distribution():
    """0..99 uniform; p50 = 49.5 (linear interpolation)."""
    pcts = _percentiles([float(i) for i in range(100)])
    assert abs(pcts["p50"] - 49.5) < 1e-9
    assert abs(pcts["p25"] - 24.75) < 1e-9
    assert abs(pcts["p95"] - 94.05) < 1e-9


def test_percentiles_empty_returns_zeros():
    pcts = _percentiles([])
    assert pcts == {"p05": 0.0, "p25": 0.0, "p50": 0.0,
                    "p75": 0.0, "p95": 0.0, "p99": 0.0}


def test_silverman_bandwidth_positive_for_real_data():
    """h > 0 for n >= 2 with nonzero variance."""
    bw = _silverman_bandwidth([1.0, 2.0, 3.0, 4.0, 5.0])
    assert bw > 0


def test_silverman_bandwidth_fallback_for_singleton():
    """h = 0.1 fallback for n < 2."""
    assert _silverman_bandwidth([5.0]) == 0.1
    assert _silverman_bandwidth([]) == 0.1


def test_silverman_bandwidth_fallback_for_zero_variance():
    """h = 0.1 when stdev is 0."""
    assert _silverman_bandwidth([3.0, 3.0, 3.0, 3.0]) == 0.1


def test_bootstrap_ci_returns_intervals_with_lo_lt_hi():
    """100 random samples; CIs should be ordered (lo <= hi)."""
    import random
    rng = random.Random(0)
    values = [rng.gauss(5.0, 1.0) for _ in range(100)]
    ci = _bootstrap_ci(values, n_boot=50, seed=42)
    for param, (lo, hi) in ci.items():
        assert lo <= hi, f"CI for {param}: lo={lo}, hi={hi}"


def test_bootstrap_ci_too_few_values_returns_empty():
    assert _bootstrap_ci([1.0, 2.0], n_boot=10) == {}


# ---------------------------------------------------------------------
# Live Mahler-domain profile
# ---------------------------------------------------------------------

def test_catalog_profile_mahler_returns_valid_profile():
    clear_runtime_cache()
    profile = catalog_profile("mahler")
    assert profile.domain == "mahler"
    assert profile.n_entries > 1000
    assert profile.primary_axis_field == "mahler_measure"
    assert profile.median_pairwise_gap > 0
    assert profile.p05 < profile.p50 < profile.p95
    assert profile.kde_bandwidth > 0


def test_catalog_profile_cache_hits_on_second_call():
    clear_runtime_cache()
    p1 = catalog_profile("mahler")
    p2 = catalog_profile("mahler")
    # Same object identity from runtime cache
    assert p1 is p2


def test_catalog_profile_refresh_recomputes():
    clear_runtime_cache()
    p1 = catalog_profile("mahler")
    p2 = catalog_profile("mahler", refresh=True)
    # Different objects, same values
    assert p1 is not p2
    assert p1.n_entries == p2.n_entries


def test_catalog_profile_pickles_to_disk():
    clear_runtime_cache()
    from prometheus_math.databases._catalog_profile import _cache_path_for
    cache_path = _cache_path_for("mahler")
    if cache_path.exists():
        cache_path.unlink()
    catalog_profile("mahler", refresh=True)
    assert cache_path.exists()
    with cache_path.open("rb") as f:
        loaded = pickle.load(f)
    assert isinstance(loaded, CatalogProfile)
    assert loaded.domain == "mahler"


def test_epsilon_band_for_mahler_is_positive():
    eps = epsilon_band_for("mahler", multiplier=1.0)
    assert eps > 0
    # Sanity: should be < 0.1 (typical Mahler-catalog gap)
    assert eps < 0.1


def test_epsilon_band_for_mahler_scales_with_multiplier():
    eps1 = epsilon_band_for("mahler", multiplier=1.0)
    eps2 = epsilon_band_for("mahler", multiplier=2.5)
    assert abs(eps2 / eps1 - 2.5) < 1e-9


def test_percentile_threshold_for_known_values():
    """Mossinghoff has Lehmer at p05-ish (smallest entries cluster
    near M_LEHMER); p95 should sit in the Salem-cluster upper region."""
    p05 = percentile_threshold_for("mahler", 0.05)
    p50 = percentile_threshold_for("mahler", 0.50)
    p95 = percentile_threshold_for("mahler", 0.95)
    assert 1.17 < p05 < 1.30   # near Lehmer band
    assert p05 < p50 < p95


def test_percentile_threshold_for_invalid_p_raises():
    with pytest.raises(ValueError, match="0.05, 0.25"):
        percentile_threshold_for("mahler", 0.42)


def test_bootstrap_ci_for_mean_is_ordered():
    lo, hi = bootstrap_ci_for("mahler", "mean")
    assert lo <= hi


def test_bootstrap_ci_for_unknown_parameter_raises():
    with pytest.raises(ValueError, match="not in"):
        bootstrap_ci_for("mahler", "nonexistent_param")


# ---------------------------------------------------------------------
# Unknown / stub domains
# ---------------------------------------------------------------------

def test_unknown_domain_raises():
    with pytest.raises(UnknownDomainError):
        catalog_profile("nonexistent_domain_xyz")


def test_bsd_stub_raises_not_yet_installed():
    """BSD slot is reserved but accessor not yet installed."""
    with pytest.raises(UnknownDomainError, match="Phase 1"):
        catalog_profile("bsd", refresh=True)


def test_known_domains_includes_mahler_and_stubs():
    domains = known_domains()
    assert "mahler" in domains
    assert "bsd" in domains
    assert "oeis" in domains
    assert "number_field" in domains


# ---------------------------------------------------------------------
# Density KDE callable
# ---------------------------------------------------------------------

def test_density_kde_callable_returns_finite():
    profile = catalog_profile("mahler")
    val = profile.density_kde(1.20)
    assert val >= 0
    assert val != float("inf")


def test_density_kde_higher_near_salem_cluster():
    """KDE peak should be near the dense Salem cluster (M ~ 1.25-1.28)."""
    profile = catalog_profile("mahler")
    d_low = profile.density_kde(1.20)
    d_peak = profile.density_kde(1.27)
    d_high = profile.density_kde(1.60)
    # Peak is higher than tails
    assert d_peak > d_high
