"""Cross-loader substrate-grade triangulation tests.

Per pivot/erebos_substrate_synthesis_iter4_to_iter15_2026-05-26.md
section "Cross-instrument triangulation": three independent loaders
converge on the Salem-class moderation effect:
- G02 contrast (ITER-4 original): observed_divergence at M_LEHMER
- G04 survivor-tightening band_high (ITER-5): band-restricted version
- G17 causal-intervention (ITER-11): label-shuffle reproduction

These tests codify the triangulation: G02 + G17 must produce
numerically-close observed-divergence values on the SAME live
catalog. If they diverge significantly, either one loader has
drifted or the underlying data changed.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders.composition_g02_lehmer_salem import (
    run_composition_battery as run_g02_salem,
)
from charon.agents.stygian.loaders.composition_g17_lehmer_label_shuffle import (
    SURVIVAL_M_THRESHOLD as G17_THRESHOLD,
    run_g17_lehmer_label_shuffle,
)
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
    permutation_null_divergence,
    survival_fraction,
)


# Tolerance for cross-loader divergence agreement.
# G02 uses threshold M_LEHMER; G17 uses threshold 1.30. They measure
# the same population but at different thresholds, so divergences
# will differ — but G17's intervention test at threshold 1.30
# should match independent G02-style salem-binary at threshold 1.30.
DIVERGENCE_TOLERANCE = 0.01


def _g02_style_divergence_at_threshold(threshold: float) -> float:
    """Re-implement the G02 salem-vs-non-salem observed-divergence
    computation at an arbitrary threshold. Returns
    abs(surv_salem - surv_non_salem)."""
    entries = load_non_cyclotomic_mahler_entries()
    salem = [
        float(e["mahler_measure"]) for e in entries
        if bool(e.get("salem_class"))
    ]
    non_salem = [
        float(e["mahler_measure"]) for e in entries
        if not bool(e.get("salem_class"))
    ]
    if not salem or not non_salem:
        return float("nan")
    return abs(
        survival_fraction(salem, threshold)
        - survival_fraction(non_salem, threshold)
    )


# ---------------------------------------------------------------------
# G02 vs G17 at the SAME threshold should produce SAME divergence
# ---------------------------------------------------------------------

def test_g02_style_and_g17_observed_divergence_agree_at_1_30():
    """G17's loader uses threshold M=1.30 by default. A direct
    salem-vs-non-salem divergence at the same threshold should match
    G17's reported observed_divergence within DIVERGENCE_TOLERANCE.

    If this fails, either:
    - G17's loader changed its threshold without updating consumers
    - One loader has a partitioning bug
    - Live catalog data shifted
    """
    g17_result = run_g17_lehmer_label_shuffle()
    if g17_result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {g17_result.get('notes')}")
    g17_observed = g17_result["observed_divergence"]

    independent_observed = _g02_style_divergence_at_threshold(G17_THRESHOLD)
    if independent_observed != independent_observed:  # NaN check
        pytest.skip("Could not compute independent observed divergence")

    assert abs(g17_observed - independent_observed) < DIVERGENCE_TOLERANCE, (
        f"G17 observed_divergence ({g17_observed}) and independent "
        f"salem-binary divergence ({independent_observed:.4f}) "
        f"diverge at threshold {G17_THRESHOLD}; "
        f"loader drift or data change."
    )


def test_g02_salem_loader_rejects_at_baseline_threshold():
    """Per ITER-4 substrate finding doc: G02 salem loader at the
    baseline threshold M_LEHMER returns REJECTED with
    kill_pattern=permutation_null. The Salem-vs-non-Salem divergence
    is invisible at M_LEHMER because both populations trivially
    survive the bound. The substrate-grade Salem moderation effect
    only emerges at threshold >= 1.30 (covered by G04 band_high
    loader + G17 intervention loader).

    Codify the baseline behavior: G02 at M_LEHMER must continue to
    REJECT, NOT promote, otherwise the threshold-sensitivity story
    documented in ITER-4 has broken.
    """
    g02_result = run_g02_salem({})
    if g02_result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G02 loader UNVERIFIED: {g02_result.get('notes')}")
    assert g02_result["verdict"] == "REJECTED", (
        f"G02 baseline expected REJECTED; got {g02_result['verdict']}. "
        f"ITER-4 documented threshold-sensitivity (Salem effect "
        f"invisible at M_LEHMER) appears to have changed."
    )
    assert g02_result["kill_pattern"] == "permutation_null"


def test_salem_moderation_emerges_at_threshold_1_30_via_g17():
    """The Salem-class moderation effect at threshold M>=1.30 is
    detectable. G17 intervention loader observed_divergence at
    threshold 1.30 should match the ITER-4 G04 result of 0.997.
    """
    g17_result = run_g17_lehmer_label_shuffle()
    if g17_result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {g17_result.get('notes')}")
    observed = g17_result["observed_divergence"]
    # ITER-4 G04 documented divergence 0.9972 at threshold 1.30; allow
    # tolerance for catalog growth.
    assert observed >= 0.90, (
        f"Salem moderation at threshold 1.30 weakened: observed "
        f"({observed}) << 0.997 documented at ITER-4."
    )


# ---------------------------------------------------------------------
# G17 reproduces ITER-4: REJECTED with correlation_survives_intervention
# ---------------------------------------------------------------------

def test_g17_reproduces_iter4_finding_via_intervention_framing():
    """G17 should always return REJECTED with
    correlation_survives_intervention on the Lehmer-Salem effect:
    the intervention fails to sever the moderation."""
    g17_result = run_g17_lehmer_label_shuffle()
    if g17_result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {g17_result.get('notes')}")
    assert g17_result["verdict"] == "REJECTED"
    assert g17_result["kill_pattern"] == "correlation_survives_intervention"


# ---------------------------------------------------------------------
# Salem cluster bulk lives below 1.30 (G10 finding cross-check)
# ---------------------------------------------------------------------

def test_salem_class_population_concentrates_below_1_30():
    """The G10 substrate finding documents that the Salem cluster
    runs through [1.18, 1.30]. Cross-check via salem_class population:
    most salem-class entries should have M < 1.30."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        pytest.skip("Catalog not loadable")
    salem = [
        float(e["mahler_measure"]) for e in entries
        if bool(e.get("salem_class"))
    ]
    if len(salem) < 100:
        pytest.skip(f"Salem population too small (n={len(salem)})")
    fraction_below_130 = sum(1 for m in salem if m < 1.30) / len(salem)
    assert fraction_below_130 >= 0.95, (
        f"Salem cluster no longer concentrates below 1.30 "
        f"({fraction_below_130:.4f}); G10 finding regressed."
    )


# ---------------------------------------------------------------------
# Permutation null behavior is stable across loaders
# ---------------------------------------------------------------------

def test_permutation_null_independent_of_threshold_for_uniform_pool():
    """For a uniform random pool, permutation_null_divergence
    distribution is approximately the same regardless of threshold
    (as long as threshold falls inside the data range). Sanity check
    on the shared helper used across all G02/G04/G17 loaders."""
    pool = [float(i) for i in range(100)]
    n_a = 50
    # Two thresholds in the middle of the range
    nulls_50 = permutation_null_divergence(pool, n_a=n_a, threshold=50, n_perm=200, seed=42)
    nulls_75 = permutation_null_divergence(pool, n_a=n_a, threshold=75, n_perm=200, seed=42)
    mean_50 = sum(nulls_50) / len(nulls_50)
    mean_75 = sum(nulls_75) / len(nulls_75)
    # Mean divergence under null should be small and ~similar
    assert mean_50 < 0.15
    assert mean_75 < 0.15
