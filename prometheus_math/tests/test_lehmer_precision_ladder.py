"""Tests for prometheus_math.lehmer_precision_ladder.

Math-tdd skill rubric: ≥3 tests in each of authority / property / edge /
composition. The driver builds a precision-vs-strategy convergence curve
over the 17 brute-force band entries; the tests pin down (1) literature
anchor values, (2) shape invariants of the curve, (3) graceful
degradation on edge inputs, (4) end-to-end pipeline well-formedness.

Reference data
--------------
* Lehmer's polynomial (deg 10, ascending [1,1,0,-1,-1,-1,-1,-1,0,1,1])
  has M = 1.17628081825991... (Lehmer, 1933). Direct mpmath.polyroots
  on the unfactored polynomial converges at every dps >= 30 — the
  unfactored polynomial has only simple roots, so Durand-Kerner is
  well-conditioned.
* Phi_15 = x^8 - x^7 + x^5 - x^4 + x^3 - x + 1 is cyclotomic with
  M = 1 exactly. Both strategies converge at every reasonable dps.
* The convergence-vs-dps curve is monotone: a strategy that has
  converged at some dps stays converged at higher dps on the same
  poly + same maxsteps (sympy.factor_list and mpmath.polyroots are
  deterministic, and the only knobs in the driver are dps and the
  fixed maxsteps).
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from prometheus_math.lehmer_precision_ladder import (
    DEFAULT_DIRECT_MAXSTEPS,
    DEFAULT_DPS_LADDER,
    PRECISION_REGIME_DIVERGENT,
    PRECISION_REGIME_FACTOR_FIRST_ONLY,
    PRECISION_REGIME_HIGH,
    PRECISION_REGIME_LOW,
    PRECISION_REGIME_MID,
    aggregate_convergence_curve,
    classify_precision_regime,
    compute_M_direct,
    compute_M_factor_first,
    evaluate_entry_on_ladder,
    run_precision_ladder,
)


LEHMER_M = 1.17628081825991759324
PROMETHEUS_MATH_DIR = Path(__file__).resolve().parents[1]
BRUTE_FORCE_JSON = PROMETHEUS_MATH_DIR / "_lehmer_brute_force_results.json"


# ---------------------------------------------------------------------------
# Authority — paper-anchored facts
# ---------------------------------------------------------------------------

def test_authority_lehmer_polynomial_direct_converges_all_ladder_dps():
    """Lehmer's deg-10 polynomial has only simple roots; direct mpmath
    polyroots converges at every dps >= 30 in the standard ladder.

    Reference: Lehmer (1933), "Factorization of certain cyclotomic
    functions"; M = 1.1762808182599... .
    """
    asc = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # Lehmer ascending
    for dps in (30, 40, 60):
        res = compute_M_direct(asc, dps=dps, maxsteps=DEFAULT_DIRECT_MAXSTEPS)
        assert res["converged"], (
            f"Lehmer at dps={dps} failed to converge directly: "
            f"status={res['status']}, error={res['error']}"
        )
        assert math.isfinite(res["M"]), f"non-finite M at dps={dps}"
        assert abs(res["M"] - LEHMER_M) < 1e-10, (
            f"M(Lehmer) at dps={dps} = {res['M']!r}, expected ~{LEHMER_M}"
        )


def test_authority_phi15_cyclotomic_M_one_both_strategies():
    """Phi_15 has all roots on the unit circle; M = 1 exactly. Both
    strategies should converge to M = 1 at every ladder dps.

    Reference: standard cyclotomic-polynomial table; Lang, *Algebra* Ch. VI.
    """
    asc = [1, -1, 0, 1, -1, 1, 0, -1, 1]
    for dps in (30, 60, 100):
        d = compute_M_direct(asc, dps=dps)
        f = compute_M_factor_first(asc, dps=dps)
        assert d["converged"], (
            f"Phi_15 direct at dps={dps}: status={d['status']}"
        )
        assert f["converged"], (
            f"Phi_15 factor-first at dps={dps}: status={f['status']}"
        )
        assert abs(d["M"] - 1.0) < 1e-10
        assert abs(f["M"] - 1.0) < 1e-10


def test_authority_ladder_is_monotone_no_regression():
    """The convergence curve is monotone: once a (poly, strategy) pair
    converges at dps=k, it must also converge at dps=k' > k. This is
    the "more precision doesn't break already-converged" sanity.

    Anchored on Lehmer's polynomial (direct strategy converges at
    every ladder point) and Phi_15 (both strategies converge at every
    point) — i.e. the property holds vacuously for these but the
    SHAPE of the test (no regression at higher dps) is the invariant.
    """
    asc_lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    asc_phi15 = [1, -1, 0, 1, -1, 1, 0, -1, 1]
    for asc in (asc_lehmer, asc_phi15):
        seen_converged = False
        for dps in DEFAULT_DPS_LADDER:
            res = compute_M_direct(asc, dps=dps)
            if seen_converged:
                assert res["converged"], (
                    f"asc={asc}: regression — converged at lower dps "
                    f"but not at dps={dps}"
                )
            if res["converged"]:
                seen_converged = True


# ---------------------------------------------------------------------------
# Property — universal invariants
# ---------------------------------------------------------------------------

def test_property_determinism_same_input_same_output():
    """sympy and mpmath are deterministic; running compute_M_factor_first
    twice on the same input must produce the same M (status fields aside;
    only M and converged are mathematically determined).
    """
    asc = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # Lehmer
    r1 = compute_M_factor_first(asc, dps=60)
    r2 = compute_M_factor_first(asc, dps=60)
    assert r1["converged"] == r2["converged"]
    assert r1["M"] == r2["M"]


def test_property_min_dps_is_nonneg_integer_or_none():
    """Per-entry min_dps for either strategy must be either a positive
    integer drawn from the ladder, or None (never converged). It cannot
    be negative, zero, or fractional.
    """
    # Run on a pair of entries: Phi_15 (converges at every dps) and one
    # of the brute-force-failed entries (only factor-first converges).
    fake_phi15_entry = {
        "half_coeffs": [],
        "coeffs_ascending": [1, -1, 0, 1, -1, 1, 0, -1, 1],
        "M_numpy": 1.0,
        "M_mpmath": 1.0,
    }
    fake_failed_entry = {
        "half_coeffs": [1, -4, 5, 0, -5, 4, -1, 0],
        "coeffs_ascending": [
            1, -4, 5, 0, -5, 4, -1, 0, -1, 4, -5, 0, 5, -4, 1
        ][::-1],
        "M_numpy": 1.0031432230024813,
        "M_mpmath": float("nan"),
    }
    for entry in (fake_phi15_entry, fake_failed_entry):
        result = evaluate_entry_on_ladder(
            entry, dps_ladder=(30, 60), direct_maxsteps=200
        )
        for key in ("direct_min_dps_converged",
                    "factor_first_min_dps_converged"):
            v = result[key]
            assert v is None or (isinstance(v, int) and v > 0), (
                f"{key}={v!r} not a positive int or None"
            )


def test_property_convergence_rate_nondecreasing_in_dps():
    """For any single strategy, the count of entries converged is
    non-decreasing as dps increases. This is the curve-shape invariant
    that motivates the whole exercise.

    Implementation note: the brute-force JSON's 17 entries each
    converge for factor-first at dps>=30 and never for direct, so both
    counts are constant (17 and 0) — but the invariant we check is the
    monotone shape, which holds vacuously and is still the right
    property to assert.
    """
    if not BRUTE_FORCE_JSON.exists():
        pytest.skip("brute-force results JSON not present")
    # Synthesize a small per-entry results stub by re-using a single
    # brute-force entry; this exercises aggregate_convergence_curve
    # without rerunning the heavy ladder.
    single_eval = evaluate_entry_on_ladder(
        {
            "half_coeffs": [1, -4, 5, 0, -5, 4, -1, 0],
            "coeffs_ascending": [
                1, -4, 5, 0, -5, 4, -1, 0, -1, 4, -5, 0, 5, -4, 1
            ][::-1],
            "M_numpy": 1.0031432230024813,
            "M_mpmath": float("nan"),
        },
        dps_ladder=(30, 60, 100),
        direct_maxsteps=200,
    )
    agg = aggregate_convergence_curve([single_eval], dps_ladder=(30, 60, 100))
    for strategy in ("direct", "factor_first"):
        counts = agg["by_strategy"][strategy]["convergence_count_by_dps"]
        prev = -1
        for d in sorted(counts.keys()):
            assert counts[d] >= prev, (
                f"non-monotone {strategy} curve: "
                f"counts={counts}, prev={prev}, dps={d}"
            )
            prev = counts[d]


# ---------------------------------------------------------------------------
# Edge — degenerate / extreme inputs
# ---------------------------------------------------------------------------

def test_edge_zero_budget_ladder_is_empty():
    """A ladder with no dps points produces a per-entry result with
    no measurements and both min_dps fields = None. The driver must
    not crash on an empty ladder.
    """
    entry = {
        "half_coeffs": [],
        "coeffs_ascending": [1, -1, 0, 1, -1, 1, 0, -1, 1],  # Phi_15
        "M_numpy": 1.0,
        "M_mpmath": 1.0,
    }
    res = evaluate_entry_on_ladder(entry, dps_ladder=(), direct_maxsteps=200)
    assert res["measurements"] == []
    assert res["direct_min_dps_converged"] is None
    assert res["factor_first_min_dps_converged"] is None
    # When neither strategy has run at any dps, regime collapses to
    # DIVERGENT (both min_dps None). This is the documented behaviour.
    assert res["regime"] == PRECISION_REGIME_DIVERGENT


def test_edge_very_low_dps_handled_gracefully():
    """A dps far below the canonical ladder (e.g. dps=10) must not
    crash. The result may be converged or not, but the schema must hold.

    On Phi_15 (cyclotomic, simple structure) factor-first should still
    converge at dps=10; the test is robust to either outcome on direct.
    """
    asc = [1, -1, 0, 1, -1, 1, 0, -1, 1]
    f = compute_M_factor_first(asc, dps=10)
    assert "converged" in f
    assert "wall_time_ms" in f
    assert "M" in f
    # Phi_15 at dps=10: factor-first uses sympy.Poly.nroots(n=10), well
    # within sympy's capabilities; should converge.
    assert f["converged"], (
        f"Phi_15 at dps=10 factor-first failed: status={f['status']}"
    )
    # Direct at dps=10 may or may not converge, but the call must
    # return a well-formed dict either way.
    d = compute_M_direct(asc, dps=10)
    assert "converged" in d
    assert isinstance(d["converged"], bool)


def test_edge_degenerate_polynomial_handled():
    """A constant polynomial (degree 0) has no roots; the strategies
    must return a well-formed result without crashing — converged=False
    and a degenerate-status flag.
    """
    asc_const = [3]  # P(x) = 3 (degree 0)
    d = compute_M_direct(asc_const, dps=30)
    f = compute_M_factor_first(asc_const, dps=30)
    # Direct: degenerate/no_convergence is fine; the contract is "no
    # crash, return a dict, M is non-finite, converged=False".
    assert d["converged"] is False
    assert not math.isfinite(d["M"])
    # Factor-first: high_precision_M_via_factor returns
    # status=factor_failed for deg < 1.
    assert f["converged"] is False


# ---------------------------------------------------------------------------
# Composition — full pipeline end-to-end
# ---------------------------------------------------------------------------

def test_composition_run_precision_ladder_produces_well_formed_json(tmp_path):
    """The end-to-end pipeline writes a JSON document with the schema
    documented in the module docstring. All required top-level keys
    are present and the per-entry list has the correct length.

    Uses a small ladder (dps={30, 60}) and the real brute-force JSON.
    """
    if not BRUTE_FORCE_JSON.exists():
        pytest.skip("brute-force results JSON not present")
    out = tmp_path / "ladder.json"
    res = run_precision_ladder(
        brute_force_results_path=BRUTE_FORCE_JSON,
        output_path=out,
        dps_ladder=(30, 60),
        direct_maxsteps=200,
        progress=False,
    )
    # In-memory shape.
    for key in (
        "subspace", "source_brute_force_results", "dps_ladder",
        "direct_maxsteps", "n_entries", "aggregate", "per_entry_results",
        "wall_time_seconds",
    ):
        assert key in res, f"missing top-level key: {key}"
    assert res["dps_ladder"] == [30, 60]
    assert res["n_entries"] == 17
    assert len(res["per_entry_results"]) == 17

    # Disk shape.
    with out.open("r", encoding="utf-8") as fh:
        on_disk = json.load(fh)
    assert on_disk["n_entries"] == res["n_entries"]
    assert on_disk["dps_ladder"] == res["dps_ladder"]
    assert len(on_disk["per_entry_results"]) == 17


def test_composition_per_entry_regime_consistent_with_min_dps():
    """For every per-entry record, the ``regime`` label must be
    consistent with the recorded ``direct_min_dps_converged`` and
    ``factor_first_min_dps_converged`` via classify_precision_regime.
    """
    if not BRUTE_FORCE_JSON.exists():
        pytest.skip("brute-force results JSON not present")
    res = run_precision_ladder(
        brute_force_results_path=BRUTE_FORCE_JSON,
        output_path=None,
        dps_ladder=(30, 60),
        direct_maxsteps=200,
        progress=False,
    )
    for r in res["per_entry_results"]:
        expected_regime = classify_precision_regime(
            direct_min_dps=r["direct_min_dps_converged"],
            factor_first_min_dps=r["factor_first_min_dps_converged"],
            ladder=res["dps_ladder"],
        )
        assert r["regime"] == expected_regime, (
            f"regime mismatch for half={r['half_coeffs']}: "
            f"recorded={r['regime']!r} vs expected={expected_regime!r}"
        )
        # Sanity: every regime label must be one of the documented set.
        assert r["regime"] in (
            PRECISION_REGIME_LOW,
            PRECISION_REGIME_MID,
            PRECISION_REGIME_HIGH,
            PRECISION_REGIME_FACTOR_FIRST_ONLY,
            PRECISION_REGIME_DIVERGENT,
        )


def test_composition_aggregate_stats_well_formed():
    """The aggregate dict produced by aggregate_convergence_curve must
    be internally self-consistent: counts in convergence_count_by_dps
    are between 0 and n_entries, regime_counts sum to n_entries, and
    classification_counts sum to n_entries.
    """
    if not BRUTE_FORCE_JSON.exists():
        pytest.skip("brute-force results JSON not present")
    res = run_precision_ladder(
        brute_force_results_path=BRUTE_FORCE_JSON,
        output_path=None,
        dps_ladder=(30, 60),
        direct_maxsteps=200,
        progress=False,
    )
    n = res["n_entries"]
    agg = res["aggregate"]
    assert agg["n_entries"] == n
    for strategy in ("direct", "factor_first"):
        counts = agg["by_strategy"][strategy]["convergence_count_by_dps"]
        rates = agg["by_strategy"][strategy]["convergence_rate_by_dps"]
        for d, c in counts.items():
            assert 0 <= c <= n, (
                f"{strategy} dps={d}: count={c} out of [0,{n}]"
            )
            # rate = count / n.
            r = rates[d]
            assert abs(r - (c / n if n > 0 else 0.0)) < 1e-12
    assert sum(agg["regime_counts"].values()) == n
    assert sum(agg["classification_counts"].values()) == n


def test_composition_classify_precision_regime_unit_table():
    """Direct unit-table for classify_precision_regime: every documented
    (direct_min_dps, factor_first_min_dps) pattern maps to the right
    regime. Locks down the bucket boundaries.
    """
    cases = [
        # Direct converges at dps=30 → LOW.
        ((30, 30), PRECISION_REGIME_LOW),
        # Direct converges at dps=40 → MID.
        ((40, 40), PRECISION_REGIME_MID),
        ((50, 50), PRECISION_REGIME_MID),
        # Direct converges at dps=60 or above → HIGH.
        ((60, 30), PRECISION_REGIME_HIGH),
        ((80, 30), PRECISION_REGIME_HIGH),
        ((100, 100), PRECISION_REGIME_HIGH),
        # Direct never converges, factor-first does → FACTOR_FIRST_ONLY.
        ((None, 30), PRECISION_REGIME_FACTOR_FIRST_ONLY),
        ((None, 100), PRECISION_REGIME_FACTOR_FIRST_ONLY),
        # Neither converges → DIVERGENT.
        ((None, None), PRECISION_REGIME_DIVERGENT),
    ]
    for (d_min, f_min), expected in cases:
        got = classify_precision_regime(
            direct_min_dps=d_min,
            factor_first_min_dps=f_min,
        )
        assert got == expected, (
            f"({d_min}, {f_min}) → {got!r}, expected {expected!r}"
        )
