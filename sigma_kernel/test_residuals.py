"""Tests for sigma_kernel.residuals (Residual primitive + REFINE opcode).

Math-tdd skill rubric: at least 3 tests in each of authority/property/edge/
composition. The 30-residual benchmark is the load-bearing acceptance test
in the composition category — if it fails (<80% accuracy or any false-
positive `signal` on known-noise), the primitive doesn't ship.

Test-first per the math-tdd skill: this file was written before
sigma_kernel/residuals.py existed.

References cited in authority tests:
- Mercury perihelion residual: Le Verrier 1859; Einstein 1915. Magnitude
  43 arcsec/century, structured deviation from Newtonian fit.
- Random Gaussian residual: textbook null distribution; classifier must
  return `noise`.
- Calibration-anchor drift: matches the OPERA-faster-than-light pattern
  cited in the proposal §3.3 — fingerprint of known instrument drift.
- Lehmer cluster (Mossinghoff): Mahler measure 1.176... polynomial
  vs random reciprocal poly distribution.
- Ramanujan-Hardy partition asymptotic: Hardy-Ramanujan 1918, leading
  correction term in p(n).
"""
from __future__ import annotations

import json
import math

import pytest
from hypothesis import given, settings, strategies as st

from sigma_kernel.sigma_kernel import (
    Capability,
    CapabilityError,
    SigmaKernel,
    Tier,
    Verdict,
)
from sigma_kernel.residuals import (
    BudgetExceeded,
    RefinementBlocked,
    Residual,
    ResidualExtension,
    SpectralVerdict,
)


# ---------------------------------------------------------------------------
# Calibration signatures fixture — used by the drift detector.
#
# The drift detector compares a residual's failure_shape JSON against this
# dict. Keys are signature ids; values are JSON-serializable
# fingerprints. A residual whose failure_shape matches a known drift
# signature classifies as `instrument_drift`.
# ---------------------------------------------------------------------------


CALIBRATION_SIGNATURES = {
    # OPERA-style: anchor recovery rate dropped from 100% to 99.13%
    "PATTERN_ANCHOR_RECOVERY_DRIFT": {
        "kind": "anchor_recovery_drift",
        "anchor_recovery_rate": {"min": 0.95, "max": 0.999},
    },
    # Prime-decile gravitational overfit (battery history fingerprint)
    "PATTERN_PRIME_GRAVITATIONAL_OVERFIT": {
        "kind": "prime_decile_bias",
        "decile_correlation": {"min": 0.5},
    },
    # Conductor-decile-correlated null breakdown
    "PATTERN_CONDUCTOR_CONFOUND": {
        "kind": "conductor_decile_correlation",
        "conductor_correlation": {"min": 0.5},
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel():
    return SigmaKernel(":memory:")


_SENTINEL = object()


def _make_ext(calibration=_SENTINEL):
    k = _make_kernel()
    if calibration is _SENTINEL:
        calibration = CALIBRATION_SIGNATURES
    return k, ResidualExtension(
        k, calibration_signatures=calibration
    )


def _bootstrap_parent_claim(k, hypothesis="parent hypothesis"):
    """Produce a parent claim with a CLEAR verdict, so REFINE has something
    to chain off of."""
    claim = k.CLAIM(
        target_name="test_target",
        hypothesis=hypothesis,
        evidence={"dataset_hash": "a" * 64},
        kill_path="test_kill_path",
        target_tier=Tier.Conjecture,
    )
    return claim


# Pre-built fixture residual subsets used across categories.

MERCURY_FAILURE_SHAPE = {
    "kind": "structured_deviation",
    "magnitude_arcsec_per_century": 43,
    "subset": "perihelion_advance",
    "variety_signature": "elliptic_orbit_residual",
    "coeff_variance": 1.7,  # > heuristic threshold
}

LEHMER_FAILURE_SHAPE = {
    "kind": "polynomial_residual",
    "subset": "lehmer_cluster",
    "variety_signature": "reciprocal_minimal_poly",
    "coeff_variance": 0.85,  # > heuristic threshold (0.5)
    "mahler_measure": 1.17628,
}

GAUSSIAN_NOISE_SHAPE = {
    "kind": "gaussian_noise",
    "subset": "random_normal",
    "coeff_variance": 0.0,  # uniform / zero structure
    "n_samples": 10,
}

OPERA_DRIFT_SHAPE = {
    "kind": "anchor_recovery_drift",
    "anchor_recovery_rate": 0.9913,
    "anchors_checked": 5,
}


# ---------------------------------------------------------------------------
# AUTHORITY TESTS  (≥3)
# ---------------------------------------------------------------------------


def test_authority_mercury_perihelion_classifies_as_signal():
    """Mercury's perihelion residual classifies as signal (variety_fingerprint
    subclass).

    Reference: Le Verrier 1859 measured the 43-arcsec/century anomalous
    advance in Mercury's perihelion as a structured deviation from the
    Newtonian fit; Einstein 1915 GR explained it. The substrate must
    classify residuals of this shape as 'signal' to allow REFINE.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="test_newtonian_fit",
        magnitude=0.0087,
        surviving_subset={"items": ["mercury_perihelion"], "n": 1},
        failure_shape=MERCURY_FAILURE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "signal"


def test_authority_random_gaussian_residual_classifies_as_noise():
    """Random Gaussian residual on a small sample classifies as noise.

    Reference: textbook null distribution. The substrate must NOT
    promote uniform-distributed residuals to 'signal'. False positives
    on noise drive infinite-rescue (proposal §5).
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="test_null",
        magnitude=0.05,
        surviving_subset={"items": [0.1, -0.2, 0.05], "n": 3},
        failure_shape=GAUSSIAN_NOISE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "noise"


def test_authority_opera_drift_classifies_as_instrument_drift():
    """OPERA-style anchor-recovery drift residual classifies as
    instrument_drift.

    Reference: OPERA faster-than-light neutrinos (loose fiber-optic
    cable). Cited in the proposal §3.3. Pattern: anchor recovery rate
    drops below 100% across the calibration set — diagnostic of
    instrument fault, not of the original hypothesis. The substrate must
    auto-spawn META_CLAIM in this case.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="test_anchor_recovery",
        magnitude=0.0087,
        surviving_subset={"items": ["anchor_5"], "n": 1},
        failure_shape=OPERA_DRIFT_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "instrument_drift"


def test_authority_refine_lehmer_cluster_halves_budget():
    """REFINE on a Lehmer-cluster (signal-class) residual produces a
    refined claim with cost_budget exactly half the parent's.

    Reference: Mossinghoff Mahler measures (Lehmer 1933 candidate
    M=1.17628). The cost-budget compounding rule from proposal §3.1
    states: max_seconds *= 2 per REFINE depth, equivalently
    cost_budget_remaining halves at each refinement. (The remaining
    budget represents how much of the parent's budget hasn't been
    spent yet on the deeper inquiry.)
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    cap = k.mint_capability("RefineCap")
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="test_mahler",
        magnitude=0.05,
        surviving_subset={"items": ["lehmer_cluster_M1.176"], "n": 1},
        failure_shape=LEHMER_FAILURE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "signal"
    refined = ext.REFINE(parent, res, cap=cap)
    assert math.isclose(
        refined.cost_budget_remaining, 5.0, rel_tol=1e-9
    ), f"expected 5.0, got {refined.cost_budget_remaining}"


def test_authority_cost_budget_exhaustion_at_depth_7():
    """Cost-budget exhaustion at depth=7 with default budget=10s raises
    BudgetExceeded.

    Reference: proposal §3.1 — by depth 7 you're spending 128x the
    original budget (or equivalently, remaining is 10 / 2^7 ≈ 0.078).
    The economic cliff fires at the depth where budget falls below the
    minimum useful per-eval threshold (default 0.1 s).
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    current = parent
    current_budget = 10.0
    raised = False
    for depth in range(20):
        # build a signal-class residual against current
        res = ext.record_residual(
            parent_claim_id=current.id,
            test_id=f"depth_{depth}",
            magnitude=0.05,
            surviving_subset={"items": [f"d{depth}"], "n": 1},
            failure_shape=LEHMER_FAILURE_SHAPE,
            instrument_id="F1_F20_battery",
            cost_budget=current_budget,
        )
        cap = k.mint_capability("RefineCap")
        try:
            current = ext.REFINE(current, res, cap=cap)
            current_budget = current.cost_budget_remaining
        except BudgetExceeded:
            raised = True
            assert depth >= 6, (
                f"BudgetExceeded raised too early at depth={depth}"
            )
            break
    assert raised, "BudgetExceeded was never raised; the rule didn't fire"


# ---------------------------------------------------------------------------
# PROPERTY TESTS  (≥3)  — Hypothesis-driven invariants
# ---------------------------------------------------------------------------


@given(magnitude=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
@settings(max_examples=20, deadline=None)
def test_property_classification_is_deterministic(magnitude):
    """Same input residual produces the same classification.

    Property: classification is a pure function of (failure_shape,
    surviving_subset, calibration_signatures). No randomness, no clock
    dependence.
    """
    k1, ext1 = _make_ext()
    k2, ext2 = _make_ext()
    parent1 = _bootstrap_parent_claim(k1)
    parent2 = _bootstrap_parent_claim(k2)
    shape = dict(LEHMER_FAILURE_SHAPE)
    r1 = ext1.record_residual(
        parent_claim_id=parent1.id,
        test_id="t",
        magnitude=magnitude,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape=shape,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    r2 = ext2.record_residual(
        parent_claim_id=parent2.id,
        test_id="t",
        magnitude=magnitude,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape=shape,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert r1.classification == r2.classification


@given(depth=st.integers(min_value=1, max_value=4))
@settings(max_examples=4, deadline=None)
def test_property_cost_budget_strictly_decreases_along_chain(depth):
    """cost_budget_remaining strictly decreases along a refinement chain;
    geometric ratio ~ 1/2 per step.

    Property: refinement chains converge geometrically.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    current = parent
    current_budget = 10.0
    budgets = [current_budget]
    for d in range(depth):
        res = ext.record_residual(
            parent_claim_id=current.id,
            test_id=f"d{d}",
            magnitude=0.05,
            surviving_subset={"items": [f"d{d}"], "n": 1},
            failure_shape=LEHMER_FAILURE_SHAPE,
            instrument_id="F1_F20_battery",
            cost_budget=current_budget,
        )
        cap = k.mint_capability("RefineCap")
        current = ext.REFINE(current, res, cap=cap)
        current_budget = current.cost_budget_remaining
        budgets.append(current_budget)
    # Strictly decreasing.
    for i in range(len(budgets) - 1):
        assert budgets[i + 1] < budgets[i]
    # Geometric ratio close to 1/2.
    if len(budgets) >= 2:
        ratio = budgets[-1] / budgets[0]
        expected = 0.5 ** depth
        assert math.isclose(ratio, expected, rel_tol=1e-9)


@given(
    magnitude=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
@settings(max_examples=10, deadline=None)
def test_property_classification_in_valid_set(magnitude):
    """residual.classification ∈ {signal, noise, instrument_drift,
    unclassified} for all valid inputs.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t",
        magnitude=magnitude,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape={"kind": "arbitrary", "coeff_variance": 0.3},
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification in {
        "signal", "noise", "instrument_drift", "unclassified"
    }


def test_property_refine_on_non_signal_raises():
    """REFINE on a residual whose classification is not 'signal' raises
    RefinementBlocked.

    Property: discipline is mechanical, not advisory. noise / drift /
    unclassified residuals cannot mint refined claims.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    # Noise-class residual.
    res_noise = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t1",
        magnitude=0.05,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape=GAUSSIAN_NOISE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    cap = k.mint_capability("RefineCap")
    with pytest.raises(RefinementBlocked):
        ext.REFINE(parent, res_noise, cap=cap)
    # Drift-class residual.
    res_drift = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t2",
        magnitude=0.05,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape=OPERA_DRIFT_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    cap2 = k.mint_capability("RefineCap")
    with pytest.raises(RefinementBlocked):
        ext.REFINE(parent, res_drift, cap=cap2)


def test_property_refinement_chain_length_equals_depth_plus_one():
    """refinement_chain returns a chain of length depth + 1 — i.e., it
    walks back from the leaf claim to the root, inclusive on both ends.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    current = parent
    current_budget = 10.0
    target_depth = 3
    for d in range(target_depth):
        res = ext.record_residual(
            parent_claim_id=current.id,
            test_id=f"d{d}",
            magnitude=0.05,
            surviving_subset={"items": [f"d{d}"], "n": 1},
            failure_shape=LEHMER_FAILURE_SHAPE,
            instrument_id="F1_F20_battery",
            cost_budget=current_budget,
        )
        cap = k.mint_capability("RefineCap")
        current = ext.REFINE(current, res, cap=cap)
        current_budget = current.cost_budget_remaining
    chain = ext.refinement_chain(current.id)
    assert len(chain) == target_depth + 1


# ---------------------------------------------------------------------------
# EDGE TESTS  (≥3)
# ---------------------------------------------------------------------------


def test_edge_empty_surviving_subset_short_circuits_to_noise():
    """Empty surviving subset → classification short-circuits to noise.

    The proposal §4.6 names this edge: an empty residual is by
    definition uniform (zero items, no structure to detect).
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t",
        magnitude=0.0,
        surviving_subset={"items": [], "n": 0},
        failure_shape={"kind": "vacuous"},
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "noise"
    assert res.magnitude == 0.0


def test_edge_magnitude_out_of_range_raises():
    """Magnitude < 0 or > 1 raises ValueError."""
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    with pytest.raises(ValueError):
        ext.record_residual(
            parent_claim_id=parent.id,
            test_id="t",
            magnitude=-0.5,
            surviving_subset={"items": ["x"], "n": 1},
            failure_shape={"kind": "arbitrary"},
            instrument_id="F1_F20_battery",
            cost_budget=10.0,
        )
    with pytest.raises(ValueError):
        ext.record_residual(
            parent_claim_id=parent.id,
            test_id="t",
            magnitude=1.5,
            surviving_subset={"items": ["x"], "n": 1},
            failure_shape={"kind": "arbitrary"},
            instrument_id="F1_F20_battery",
            cost_budget=10.0,
        )


def test_edge_refine_without_capability_raises():
    """REFINE without a capability raises CapabilityError."""
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t",
        magnitude=0.05,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape=LEHMER_FAILURE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    with pytest.raises(CapabilityError):
        ext.REFINE(parent, res, cap=None)


def test_edge_refine_with_consumed_capability_raises():
    """REFINE with already-consumed capability raises CapabilityError."""
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t",
        magnitude=0.05,
        surviving_subset={"items": ["x"], "n": 1},
        failure_shape=LEHMER_FAILURE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    cap = k.mint_capability("RefineCap")
    ext.REFINE(parent, res, cap=cap)
    # Re-using the same cap_id token raises (linearity check via DB).
    res2 = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t2",
        magnitude=0.05,
        surviving_subset={"items": ["y"], "n": 1},
        failure_shape=LEHMER_FAILURE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    with pytest.raises(CapabilityError):
        ext.REFINE(parent, res2, cap=cap)


def test_edge_refinement_at_depth_20_raises_budget_exceeded():
    """Refinement at depth=20 raises BudgetExceeded long before hitting
    the depth limit (well below the 0.1s minimum-useful threshold).
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    current = parent
    current_budget = 10.0
    # By depth 7 budget is 0.078 s, below 0.1 s minimum-useful → raises.
    raised = False
    for depth in range(20):
        res = ext.record_residual(
            parent_claim_id=current.id,
            test_id=f"d{depth}",
            magnitude=0.05,
            surviving_subset={"items": [f"d{depth}"], "n": 1},
            failure_shape=LEHMER_FAILURE_SHAPE,
            instrument_id="F1_F20_battery",
            cost_budget=current_budget,
        )
        cap = k.mint_capability("RefineCap")
        try:
            current = ext.REFINE(current, res, cap=cap)
            current_budget = current.cost_budget_remaining
        except BudgetExceeded:
            raised = True
            break
    assert raised


def test_edge_drift_detector_with_no_calibration_signatures():
    """Drift detector with no calibration signatures loaded returns
    'unclassified' for residuals that look like drift but cannot be
    matched.

    The MVP semantics: if nothing in the four-subclass canonicalizer
    fires AND the calibration_signatures dict is empty, fall through to
    'unclassified' (NOT 'noise', because we don't know yet).
    """
    k, ext = _make_ext(calibration={})  # empty calibration map
    parent = _bootstrap_parent_claim(k)
    # Use a shape that wouldn't fire any canonicalizer (zero variance,
    # no variety_signature, no ideal_signature).
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t",
        magnitude=0.5,
        surviving_subset={"items": ["item"], "n": 1},
        failure_shape={"kind": "anchor_recovery_drift",
                       "anchor_recovery_rate": 0.95},
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    # With empty calibration map, drift detection skips → unclassified
    # or noise (NOT classified as instrument_drift).
    assert res.classification != "instrument_drift"


# ---------------------------------------------------------------------------
# COMPOSITION TESTS  (≥3)
# ---------------------------------------------------------------------------


def test_composition_full_pipeline_claim_to_residual_to_refined_claim():
    """End-to-end: bootstrap a CLAIM → simulate FALSIFY producing a
    residual → record_residual auto-classifies signal → REFINE → child
    claim is intact.

    Composition: chains the v0.1 kernel's CLAIM op with the new
    record_residual + REFINE ops.
    """
    k, ext = _make_ext()
    parent = k.CLAIM(
        target_name="lehmer_test",
        hypothesis="Mahler measure < threshold",
        evidence={"dataset_hash": "b" * 64},
        kill_path="kill_path_lehmer",
    )
    # Simulate FALSIFY producing a non-uniform residual.
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="lehmer_battery",
        magnitude=0.0087,
        surviving_subset={"items": ["lehmer_M1.176"], "n": 1},
        failure_shape=LEHMER_FAILURE_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "signal"
    # REFINE produces a child claim.
    cap = k.mint_capability("RefineCap")
    refined = ext.REFINE(parent, res, cap=cap)
    assert refined.target_name == parent.target_name
    assert refined.refinement_depth == 1
    # Refined claim's hypothesis includes provenance back to parent.
    assert parent.id in refined.parent_claim_id_or_root
    # The refined claim is a real Claim — it can be FALSIFY-ed (skip
    # actually running the oracle in the unit test; just verify it has
    # the structural fields).
    assert refined.hypothesis  # non-empty


def test_composition_30_residual_benchmark_load_bearing():
    """LOAD-BEARING ACCEPTANCE TEST.

    The 30-residual benchmark is the day-4 acceptance criterion from
    proposal §7. Required:
      - >=80% overall classifier accuracy
      - ZERO false-positive `signal` calls on known-noise residuals

    If this test fails, the primitive does not ship. Per proposal §5
    classifier-kill: the primitive's value depends on the classifier
    being able to separate signal from noise on a curated benchmark.
    """
    from sigma_kernel.residual_benchmark import (
        BENCHMARK_ENTRIES,
        run_benchmark,
    )
    k, ext = _make_ext()
    result = run_benchmark(ext, k, BENCHMARK_ENTRIES)
    # Hard gate 1: overall accuracy >= 80%.
    assert result["accuracy"] >= 0.80, (
        f"Benchmark accuracy {result['accuracy']:.3f} < 0.80; primitive does "
        f"not ship per proposal §5 classifier-kill discipline. "
        f"Per-class precision/recall: {result['per_class']}"
    )
    # Hard gate 2: zero false-positive `signal` on known-noise.
    fp_signal = result["false_positive_signal_count"]
    assert fp_signal == 0, (
        f"Got {fp_signal} false-positive `signal` calls on known-noise "
        f"residuals; this drives infinite-rescue and the primitive does "
        f"not ship per proposal §5. Mis-classified noise items: "
        f"{result['false_positive_signal_items']}"
    )


def test_composition_refinement_chain_provenance_walks_to_root():
    """TRACE on a leaf refined claim walks back through the chain via
    the residuals table to the root.

    Composition: chains REFINE with the kernel's TRACE-style provenance
    walk (here we use refinement_chain since refined claims aren't
    Symbols proper).
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k, hypothesis="root hypothesis")
    current = parent
    current_budget = 10.0
    chain_ids = [parent.id]
    for d in range(3):
        res = ext.record_residual(
            parent_claim_id=current.id,
            test_id=f"step{d}",
            magnitude=0.05,
            surviving_subset={"items": [f"step{d}"], "n": 1},
            failure_shape=LEHMER_FAILURE_SHAPE,
            instrument_id="F1_F20_battery",
            cost_budget=current_budget,
        )
        cap = k.mint_capability("RefineCap")
        current = ext.REFINE(current, res, cap=cap)
        current_budget = current.cost_budget_remaining
        chain_ids.append(current.id)
    # refinement_chain should walk back through the residuals table.
    walked = ext.refinement_chain(current.id)
    walked_ids = [c.id for c, _ in walked]
    assert walked_ids[0] == parent.id  # root first
    assert walked_ids[-1] == current.id  # leaf last
    assert walked_ids == chain_ids


def test_composition_cost_budget_conservation_along_chain():
    """Cost-budget conservation: total budget consumed across a depth-N
    chain equals cost_0 * (1 - 0.5^N) to within tolerance.

    Composition: chains record_residual + REFINE and verifies the
    declared geometric law.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    current = parent
    cost_0 = 10.0
    current_budget = cost_0
    N = 4
    for d in range(N):
        res = ext.record_residual(
            parent_claim_id=current.id,
            test_id=f"d{d}",
            magnitude=0.05,
            surviving_subset={"items": [f"d{d}"], "n": 1},
            failure_shape=LEHMER_FAILURE_SHAPE,
            instrument_id="F1_F20_battery",
            cost_budget=current_budget,
        )
        cap = k.mint_capability("RefineCap")
        current = ext.REFINE(current, res, cap=cap)
        current_budget = current.cost_budget_remaining
    # Remaining budget at depth N: cost_0 * 0.5^N.
    expected_remaining = cost_0 * (0.5 ** N)
    assert math.isclose(current_budget, expected_remaining, rel_tol=1e-9)
    # Total consumed: cost_0 * (1 - 0.5^N).
    consumed = cost_0 - current_budget
    expected_consumed = cost_0 * (1 - 0.5 ** N)
    assert math.isclose(consumed, expected_consumed, rel_tol=1e-9)


def test_composition_meta_claim_auto_spawned_on_drift():
    """When a residual classifies as instrument_drift, record_meta_claim
    auto-spawns a CLAIM targeting the battery itself (not the original
    hypothesis).

    Composition: chains record_residual (classifies drift) with
    record_meta_claim (mints a battery-target claim). Per proposal
    §3.3, this is the Penzias-Wilson move made systematic.
    """
    k, ext = _make_ext()
    parent = _bootstrap_parent_claim(k)
    res = ext.record_residual(
        parent_claim_id=parent.id,
        test_id="t",
        magnitude=0.0087,
        surviving_subset={"items": ["anchor_5"], "n": 1},
        failure_shape=OPERA_DRIFT_SHAPE,
        instrument_id="F1_F20_battery",
        cost_budget=10.0,
    )
    assert res.classification == "instrument_drift"
    cap = k.mint_capability("RefineCap")
    meta = ext.record_meta_claim(
        target_battery_id="F1_F20_battery",
        evidence_residuals=[res],
        hypothesis="battery integrity compromised by anchor recovery drift",
        cap=cap,
    )
    assert meta.target_name == "F1_F20_battery"
    # The meta-claim's evidence should mention the drift residual.
    assert res.id in meta.evidence
