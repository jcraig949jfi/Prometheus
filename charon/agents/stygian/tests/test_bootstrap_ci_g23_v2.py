"""Tests for bootstrap CI primitive + G23 v2 loader.

Per Erebos v3 Phase 1A ITER-33. Validates nonparametric bootstrap
CI on synthetic mean / slope / ratio statistics + the G23 retrofit
on live Mossinghoff per-degree minima data.
"""
from __future__ import annotations

import math
import statistics

import pytest

from charon.agents.stygian.loaders._bootstrap_ci import (
    BootstrapCIResult,
    bootstrap_ci,
)


# ---------------------------------------------------------------------
# Bootstrap CI primitive
# ---------------------------------------------------------------------

def test_bootstrap_ci_empty_sample_safe():
    """Empty / single-element input returns degenerate result, no crash."""
    r = bootstrap_ci([], lambda d: 0.0)
    assert isinstance(r, BootstrapCIResult)
    assert r.statistic_observed is None
    assert r.ci_lower is None

    r = bootstrap_ci([1.0], lambda d: float(d[0]))
    assert r.ci_lower is None


def test_bootstrap_ci_mean_covers_true_mean():
    """Bootstrap CI of the mean covers the population mean."""
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    r = bootstrap_ci(
        data,
        lambda d: sum(d) / len(d),
        n_resamples=500,
        confidence_level=0.95,
        seed=42,
    )
    true_mean = 5.5
    assert r.ci_lower <= true_mean <= r.ci_upper
    assert abs(r.statistic_observed - true_mean) < 1e-9


def test_bootstrap_ci_reproducible_with_seed():
    """Same seed -> identical bootstrap distribution."""
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    r1 = bootstrap_ci(data, lambda d: sum(d) / len(d), n_resamples=200, seed=99)
    r2 = bootstrap_ci(data, lambda d: sum(d) / len(d), n_resamples=200, seed=99)
    assert r1.statistic_distribution == r2.statistic_distribution
    assert r1.ci_lower == r2.ci_lower
    assert r1.ci_upper == r2.ci_upper


def test_bootstrap_ci_seed_changes_change_distribution():
    """Different seeds -> different bootstrap samples."""
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    r1 = bootstrap_ci(data, lambda d: sum(d) / len(d), n_resamples=200, seed=1)
    r2 = bootstrap_ci(data, lambda d: sum(d) / len(d), n_resamples=200, seed=2)
    assert r1.statistic_distribution != r2.statistic_distribution


def test_bootstrap_ci_filters_none_resamples():
    """statistic_fn returning None on a resample is silently dropped."""
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Always-None statistic -> result has no CI but no crash
    r = bootstrap_ci(data, lambda d: None, n_resamples=100, seed=1)
    assert r.statistic_observed is None
    assert r.ci_lower is None


def test_bootstrap_ci_covers_and_fraction_methods():
    """Covers / fraction_above / fraction_below report correctly."""
    data = list(range(100))
    r = bootstrap_ci(
        data, lambda d: sum(d) / len(d),
        n_resamples=500, seed=7,
    )
    # True mean ~ 49.5; CI should cover it
    assert r.covers(49.5)
    # CI shouldn't cover absurd values
    assert not r.covers(0.0)
    assert not r.covers(100.0)
    # Fractions should sum to ~1 (excluding == threshold)
    p_above = r.fraction_above(49.5)
    p_below = r.fraction_below(49.5)
    assert 0.0 <= p_above <= 1.0
    assert 0.0 <= p_below <= 1.0


def test_bootstrap_ci_narrow_ci_for_low_variance():
    """Low-variance data -> narrow CI; high-variance -> wide CI."""
    low_var = [5.0] * 20 + [5.01] * 20
    high_var = list(range(40))
    r_low = bootstrap_ci(low_var, lambda d: sum(d) / len(d), n_resamples=500, seed=3)
    r_high = bootstrap_ci(high_var, lambda d: sum(d) / len(d), n_resamples=500, seed=3)
    low_width = r_low.ci_upper - r_low.ci_lower
    high_width = r_high.ci_upper - r_high.ci_lower
    assert low_width < high_width


def test_bootstrap_ci_slope_on_linear_data():
    """OLS slope on perfectly linear data -> CI tight around true slope."""
    points = [(float(i), 2.0 * i + 1.0) for i in range(1, 21)]

    def slope_stat(pts):
        n = len(pts)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        if den == 0:
            return None
        return num / den

    r = bootstrap_ci(points, slope_stat, n_resamples=500, seed=11)
    # Slope is exactly 2.0; CI very tight
    assert abs(r.statistic_observed - 2.0) < 1e-6
    assert r.ci_lower <= 2.0 <= r.ci_upper


# ---------------------------------------------------------------------
# G23 v2 loader: routing
# ---------------------------------------------------------------------

def test_g23_v2_applicable_routes_on_bootstrap_marker():
    from charon.agents.stygian.loaders.composition_g23_lehmer_degree_decay_bootstrap import (
        G23LehmerDegreeDecayBootstrapLoader,
    )
    loader = G23LehmerDegreeDecayBootstrapLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g23_asymptotic_limit",
        "erebos_composed_id": "EREBOS-G23-bootstrap_lehmer_test",
    }) is True


def test_g23_v2_does_not_steal_v1_emissions():
    """v1 (hard-tolerance) G23 emissions continue routing to the
    original loader."""
    from charon.agents.stygian.loaders.composition_g23_lehmer_degree_decay_bootstrap import (
        G23LehmerDegreeDecayBootstrapLoader,
    )
    loader = G23LehmerDegreeDecayBootstrapLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g23_asymptotic_limit",
        "erebos_composed_id": "EREBOS-G23-lehmer_BL-C-001-degree",
    }) is False


def test_g23_v2_rejects_non_g23_plugin():
    from charon.agents.stygian.loaders.composition_g23_lehmer_degree_decay_bootstrap import (
        G23LehmerDegreeDecayBootstrapLoader,
    )
    loader = G23LehmerDegreeDecayBootstrapLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g10_boundary",
        "erebos_composed_id": "EREBOS-G10-bootstrap_test",
    }) is False


# ---------------------------------------------------------------------
# Live Mossinghoff smoke
# ---------------------------------------------------------------------

def test_g23_v2_live_returns_ci_band_with_seam_fields():
    """Live loader returns CI bounds + bootstrap fractions for the
    seam (graded confidence)."""
    from charon.agents.stygian.loaders.composition_g23_lehmer_degree_decay_bootstrap import (
        run_g23_lehmer_degree_decay_bootstrap,
    )
    result = run_g23_lehmer_degree_decay_bootstrap()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"Live Mossinghoff catalog not available: "
                    f"{result.get('notes')}")
    # CI bounds present
    assert result["slope_ci_lower"] is not None
    assert result["slope_ci_upper"] is not None
    assert result["slope_ci_lower"] <= result["slope_ci_upper"]
    # Observed slope inside its own CI (sanity check)
    assert result["slope_ci_lower"] - 1e-9 <= result["slope_observed"]
    assert result["slope_observed"] <= result["slope_ci_upper"] + 1e-9
    # Verdict in canonical set
    assert result["verdict"] in (
        "PROMOTED", "REJECTED", "UNCERTAIN", "UNVERIFIED"
    )
    # Bootstrap counts present
    assert result["n_bootstrap_resamples"] > 0
    assert result["bootstrap_seed"] == 17
    # Fractions in [0, 1]
    assert 0.0 <= result["fraction_above_no_decay_bound"] <= 1.0
    assert 0.0 <= result["fraction_below_faster_bound"] <= 1.0
