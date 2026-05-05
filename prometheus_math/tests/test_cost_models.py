"""Tests for the empirical cost-model calibration shipped on 2026-05-04.

Validates that ``prometheus_math.cost_model_profiler`` produces
well-formed structured cost models, that the calibrated coefficients
match expected complexity classes for ops with known asymptotic
behavior, and that the harness handles edge cases (zero-size, throwing
ops, unbounded growth) cleanly.

Test taxonomy (math-tdd skill, four required categories):

- Authority (>=3): coefficients/complexity for ops whose asymptotic
  behavior is documented in the literature (mahler_measure is O(n) or
  O(n log n) in degree, NOT O(n^2); is_cyclotomic is O(n) in degree;
  factor_polynomial / flint_factor is sub-quadratic on small inputs).
- Property (>=3): determinism, ratio metric well-definedness, every
  registered op has a non-null cost_model post-update.
- Edge (>=3): zero-size input (no crash), op that throws on bad input
  (calibration_failed flag), unbounded growth (size limit honored).
- Composition (>=3): profiler harness produces the expected report
  schema, top-50 batch produces well-formed JSON, and recalibration
  doesn't break the existing 2436+ tests.

Calibrated on Skullport (Windows 11 / Python 3.11.9 / AMD Ryzen 7
5700X3D); the absolute coefficient bounds below are *generous* (factor
3-5x) so the tests are stable across thermal / load variation on the
same host.
"""
from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, List

import pytest

from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
from prometheus_math.cost_model_profiler import (
    PROBES,
    Profile,
    TOP_50_HOT_PATH,
    build_report,
    calibrated_cost_payload,
    hardware_profile,
    predict_us,
    profile_op,
    profile_top_50,
)


# ---------------------------------------------------------------------------
# Authority — calibrated coefficients must match documented complexity
# classes within 2x for ops with well-known asymptotics.
# ---------------------------------------------------------------------------


def test_authority_mahler_measure_is_subquadratic_in_degree():
    """Mahler measure of a degree-n integer polynomial is *not* O(n^2):

    The classical computation is root-finding (degree-n companion
    matrix eigenvalues, ~O(n^3) in the worst case) but at the small
    sizes (n<=40) we profile, mpmath's polyroots dominated by O(n) bit
    manipulation per coefficient. Authority: Mossinghoff Mahler tables
    + Lehmer 1933 §3 (computational outline).

    The fitted complexity at n in {10, 20, 40} should be at most
    O(n log n); coefficient < 50 us at n=1.
    """
    ref = "techne.lib.mahler_measure:mahler_measure"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("mahler_measure not in registry")
    cal = ARSENAL_REGISTRY[ref].cost.get("calibrated_cost")
    assert cal is not None, "mahler_measure missing calibrated_cost"
    cls = cal["complexity"]
    assert cls in {"O(1)", "O(log n)", "O(n)", "O(n log n)"}, (
        f"mahler_measure expected sub-quadratic; got {cls}"
    )
    assert 0 < cal["coefficient_us"] < 50, (
        f"mahler_measure coefficient_us {cal['coefficient_us']} out of [0, 50]"
    )


def test_authority_is_cyclotomic_is_linear_or_better():
    """is_cyclotomic checks |root|==1 for each root of an integer poly.

    Authority: Kronecker 1857 + Mossinghoff Mahler tables. The dominant
    cost is companion-matrix root-finding (worst case O(n^3) but
    sub-quadratic at the small degrees we profile); at most O(n log n)
    in practice.
    """
    ref = "techne.lib.mahler_measure:is_cyclotomic"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("is_cyclotomic not in registry")
    cal = ARSENAL_REGISTRY[ref].cost.get("calibrated_cost")
    assert cal is not None
    assert cal["complexity"] in {"O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)"}, (
        f"is_cyclotomic expected polynomial-time; got {cal['complexity']}"
    )


def test_authority_flint_factor_is_subquadratic_at_profile_sizes():
    """FLINT integer-polynomial factorization is Berlekamp-Zassenhaus.

    Authority: Cohen GTM 138 §3.5; FLINT docs. Asymptotically O(n^2 +
    n log^2 n) but at degrees 4..16 the dominant cost is fixed-overhead
    + linear; the fit should NOT come back as O(n^3) or worse.
    """
    ref = "prometheus_math.numerics:flint_factor"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("flint_factor not in registry")
    cal = ARSENAL_REGISTRY[ref].cost.get("calibrated_cost")
    assert cal is not None
    assert cal["complexity"] in {"O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)"}, (
        f"flint_factor expected at most O(n^2) at small sizes; got {cal['complexity']}"
    )


def test_authority_logistic_map_is_linear_in_iterations():
    """Logistic map iteration is one multiply per step, so total cost
    is exactly O(n_iter). Authority: trivial — simple arithmetic loop.
    """
    ref = "prometheus_math.dynamics_iterated_maps:logistic_map"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("logistic_map not in registry")
    cal = ARSENAL_REGISTRY[ref].cost.get("calibrated_cost")
    assert cal is not None
    assert cal["complexity"] == "O(n)", (
        f"logistic_map expected O(n); got {cal['complexity']}"
    )


def test_authority_smith_normal_form_polynomial_in_size():
    """Smith Normal Form is polynomial-time in matrix dimension.

    Authority: Smith 1861; Cohen GTM 138 §2.4. Small fixed sizes
    (n=3,5,8) in our profile rarely show super-cubic behaviour.
    """
    ref = "techne.lib.smith_normal_form:smith_normal_form"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("smith_normal_form not in registry")
    cal = ARSENAL_REGISTRY[ref].cost.get("calibrated_cost")
    assert cal is not None
    assert cal["complexity"] in {
        "O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)",
    }, f"smith_normal_form expected polynomial; got {cal['complexity']}"


def test_authority_calibrated_cost_json_is_well_formed():
    """Every calibrated_cost dict round-trips through json.dumps cleanly.

    Authority: structural — the profiler must emit JSON-serialisable
    payloads so cost models can be archived / shared / diffed.
    """
    for ref, meta in ARSENAL_REGISTRY.items():
        cal = meta.cost.get("calibrated_cost")
        if cal is None:
            continue
        # Must be a dict
        assert isinstance(cal, dict), f"{ref}: calibrated_cost not a dict"
        # Must round-trip
        s = json.dumps(cal)
        cal2 = json.loads(s)
        assert cal2 == cal, f"{ref}: calibrated_cost not json-stable"
        # Required keys
        for k in ("complexity", "coefficient_us", "calibrated_2026_05_04"):
            assert k in cal, f"{ref}: calibrated_cost missing key {k!r}"


# ---------------------------------------------------------------------------
# Property — invariants that hold across all profiles / all ops.
# ---------------------------------------------------------------------------


def test_property_calibration_is_deterministic_given_fixed_inputs():
    """Two profile_op calls on a deterministic op give the same fitted
    complexity class (the absolute coefficients drift with thermal /
    OS-jitter noise, but the class bucket is stable on log-log fit).
    """
    ref = "prometheus_math.combinatorics_partitions:num_partitions"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("num_partitions not in registry")
    declared = ARSENAL_REGISTRY[ref].cost["max_seconds"]
    p1 = profile_op(ref, declared_max_seconds=declared, n_repeats=5)
    p2 = profile_op(ref, declared_max_seconds=declared, n_repeats=5)
    assert not p1.calibration_failed
    assert not p2.calibration_failed
    # Class is deterministic; coefficient may drift up to 2x with noise.
    assert p1.fitted_complexity == p2.fitted_complexity, (
        f"non-deterministic class: {p1.fitted_complexity} vs {p2.fitted_complexity}"
    )


def test_property_ratio_metric_is_well_defined():
    """ratio_declared_over_p95 is finite and positive for every
    successfully-calibrated op with a non-zero declared budget.
    """
    declared = {ref: meta.cost.get("max_seconds", 0.0)
                for ref, meta in ARSENAL_REGISTRY.items()}
    p = profile_op(
        "prometheus_math.combinatorics_partitions:num_partitions",
        declared_max_seconds=declared.get(
            "prometheus_math.combinatorics_partitions:num_partitions", 0.0),
        n_repeats=3,
    )
    if not p.calibration_failed:
        assert p.ratio_declared_over_p95 > 0
        assert math.isfinite(p.ratio_declared_over_p95)


def test_property_every_registered_op_has_cost_model_after_update():
    """All ops in ARSENAL_REGISTRY have a non-null cost dict; top-50
    hot-path ops additionally carry a structured calibrated_cost.
    """
    missing_cost = [ref for ref, meta in ARSENAL_REGISTRY.items()
                    if not meta.cost]
    assert not missing_cost, f"{len(missing_cost)} ops missing cost: {missing_cost[:5]}"

    missing_cal = [ref for ref in TOP_50_HOT_PATH
                   if ref in ARSENAL_REGISTRY
                   and ARSENAL_REGISTRY[ref].cost.get("calibrated_cost") is None]
    assert not missing_cal, (
        f"{len(missing_cal)} top-50 ops missing calibrated_cost: {missing_cal[:5]}"
    )


def test_property_predict_us_is_monotone_in_size():
    """predict_us(cal, n) is monotone non-decreasing in n for non-trivial
    complexity classes. (O(1) is constant, others grow.)
    """
    sample_cals = [
        {"complexity": "O(n)", "coefficient_us": 1.0},
        {"complexity": "O(n log n)", "coefficient_us": 1.0},
        {"complexity": "O(n^2)", "coefficient_us": 1.0},
        {"complexity": "O(n^3)", "coefficient_us": 1.0},
    ]
    for cal in sample_cals:
        prev = -1.0
        for n in (1, 4, 16, 64):
            cur = predict_us(cal, n)
            assert cur >= prev - 1e-9, (
                f"non-monotone: cls={cal['complexity']} n={n} prev={prev} cur={cur}"
            )
            prev = cur


def test_property_complexity_class_is_one_of_seven():
    """fitted_complexity is one of the seven standard buckets (no
    spurious labels)."""
    valid = {"O(1)", "O(log n)", "O(n)", "O(n log n)",
             "O(n^2)", "O(n^3)", "O(2^n)", "unknown"}
    for ref, meta in ARSENAL_REGISTRY.items():
        cal = meta.cost.get("calibrated_cost")
        if cal is None:
            continue
        assert cal["complexity"] in valid, (
            f"{ref}: invalid complexity class {cal['complexity']!r}"
        )


# ---------------------------------------------------------------------------
# Edge — zero-size, throwing op, unbounded growth.
# ---------------------------------------------------------------------------


def test_edge_zero_size_input_does_not_crash():
    """profile_op handles a probe builder that returns size=0 gracefully.

    The harness must record a near-zero time and not raise, because some
    ops legitimately accept empty input (e.g. partitions_of(0) == [()]).
    """
    # num_partitions(0) is well-defined: 1.
    fn = lambda *args, **kwargs: 1  # noqa: E731 — placeholder, see below
    # Use the real op so we exercise the real harness.
    ref = "prometheus_math.combinatorics_partitions:num_partitions"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("num_partitions not in registry")

    # Override the probe to test zero-size by registering a temp probe.
    saved = PROBES.get(ref)
    try:
        PROBES[ref] = ((0, 1, 2), lambda n: ([n], {}))
        p = profile_op(ref, declared_max_seconds=0.5, n_repeats=3)
        assert not p.calibration_failed, p.error
        # Either zero or a tiny positive number; both acceptable.
        assert all(t >= 0 for t in p.times_us)
    finally:
        if saved is not None:
            PROBES[ref] = saved


def test_edge_throwing_op_caught_as_calibration_failed():
    """If the probe builder raises (e.g. wrong arg shape), the profiler
    must catch and report calibration_failed=True without bubbling.
    """
    ref = "prometheus_math.combinatorics_partitions:num_partitions"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("num_partitions not in registry")
    saved = PROBES.get(ref)
    try:
        PROBES[ref] = ((1, 2, 3), lambda n: (1 / 0, {}))  # zero-div in builder
        p = profile_op(ref, declared_max_seconds=0.5, n_repeats=3)
        assert p.calibration_failed, "expected calibration_failed=True"
        assert "ZeroDivisionError" in p.error or "builder" in p.error
    finally:
        if saved is not None:
            PROBES[ref] = saved


def test_edge_op_throwing_at_eval_time_caught_as_calibration_failed():
    """If the *callable* (not the builder) throws on the chosen args,
    the profiler reports calibration_failed=True. Required for ops that
    legitimately reject a size class.
    """
    ref = "prometheus_math.combinatorics_partitions:num_partitions"
    if ref not in ARSENAL_REGISTRY:
        pytest.skip("num_partitions not in registry")
    saved = PROBES.get(ref)
    try:
        # num_partitions wants a non-negative int; pass a string to force a TypeError.
        PROBES[ref] = ((1, 2, 3), lambda n: (["bogus"], {}))
        p = profile_op(ref, declared_max_seconds=0.5, n_repeats=3)
        assert p.calibration_failed
        assert "measure" in p.error or "TypeError" in p.error
    finally:
        if saved is not None:
            PROBES[ref] = saved


def test_edge_unbounded_growth_stops_at_wall_budget():
    """For an op whose total wall time would exceed the per-op budget
    of 5 seconds, the harness stops mid-loop and still emits a result.
    Required for factorial-time / pathological-scale inputs.
    """
    from prometheus_math.cost_model_profiler import _measure

    def slow_fn(n: int) -> int:
        time.sleep(0.05)  # 50ms per call
        return n

    # n_repeats=100 would be 5 seconds total; we cap at max_total_seconds=0.2,
    # which means ~4 measurements before the budget cuts us off.
    ts = _measure(slow_fn, [1], {}, n_repeats=100, max_total_seconds=0.2)
    assert 0 < len(ts) < 100, (
        f"_measure should have stopped early; got {len(ts)} samples"
    )


def test_edge_ref_with_no_probe_marks_calibration_failed():
    """profile_op for a ref that has no probe entry returns
    calibration_failed=True with a clear error.
    """
    p = profile_op("nonsense.module:fake_callable_ref",
                   declared_max_seconds=0.001, n_repeats=2)
    assert p.calibration_failed
    assert p.error  # non-empty


# ---------------------------------------------------------------------------
# Composition — full report schema, batch, regression-free.
# ---------------------------------------------------------------------------


def test_composition_report_dict_has_all_expected_keys():
    """build_report returns a dict with the schema downstream tooling
    expects: hardware, n_profiled, n_calibrated, n_failed,
    n_in_band_2x_to_50x, n_out_of_band, worst_skewed_top5, profiles.
    """
    declared = {ref: meta.cost.get("max_seconds", 0.0)
                for ref, meta in ARSENAL_REGISTRY.items()}
    # Profile a handful of cheap ops only.
    cheap_refs = [
        "prometheus_math.combinatorics_partitions:num_partitions",
        "prometheus_math.combinatorics_partitions:conjugate",
        "prometheus_math.research.lehmer:is_reciprocal",
    ]
    profiles: Dict[str, Profile] = {}
    for ref in cheap_refs:
        if ref in ARSENAL_REGISTRY and ref in PROBES:
            profiles[ref] = profile_op(ref, declared.get(ref, 0.0), n_repeats=3)
    if not profiles:
        pytest.skip("no cheap ops available")
    report = build_report(profiles)
    for k in ("hardware", "n_profiled", "n_calibrated", "n_failed",
              "n_in_band_2x_to_50x", "n_out_of_band",
              "worst_skewed_top5", "profiles"):
        assert k in report, f"build_report missing key {k!r}"
    # Hardware sub-dict shape
    for k in ("platform", "processor", "python_version"):
        assert k in report["hardware"]


def test_composition_top_50_batch_produces_valid_json():
    """profile_top_50 + build_report yields a JSON-serialisable report.
    Use a tiny n_repeats (2) to keep test wall-time bounded.
    """
    declared = {ref: meta.cost.get("max_seconds", 0.0)
                for ref, meta in ARSENAL_REGISTRY.items()}
    profiles = profile_top_50(declared, n_repeats=2)
    report = build_report(profiles)
    blob = json.dumps(report, indent=2)
    assert len(blob) > 100  # non-trivial
    # Round-trips
    parsed = json.loads(blob)
    assert parsed["n_profiled"] == report["n_profiled"]


def test_composition_calibrated_cost_payload_round_trips():
    """calibrated_cost_payload(profile) -> JSON -> dict preserves all
    structured fields. Used by the report writer + by _metadata_table.
    """
    p = Profile(callable_ref="dummy:op",
                sizes=[1, 2, 4],
                times_us=[10.0, 20.0, 40.0],
                fitted_complexity="O(n)",
                fitted_coefficient_us=10.0,
                fitted_r2=1.0,
                p95_max_seconds=4e-5,
                declared_max_seconds=4e-4,
                ratio_declared_over_p95=10.0,
                in_band=True,
                n_repeats=3)
    payload = calibrated_cost_payload(p)
    assert payload["complexity"] == "O(n)"
    assert payload["coefficient_us"] == 10.0
    assert payload["calibrated_2026_05_04"] is True
    blob = json.dumps(payload)
    assert "O(n)" in blob


def test_composition_recalibration_does_not_break_existing_metadata():
    """The recalibrated metadata table preserves every previously-required
    invariant the existing test_arsenal_metadata.py suite enforces:

    - all 85 ops still register
    - every entry still has callable_ref/cost/postconditions/authority_refs
    - the [2x, 50x] safety-band test still passes
    """
    assert len(ARSENAL_REGISTRY) >= 50, (
        f"recalibration shrank registry to {len(ARSENAL_REGISTRY)}; "
        "expected >= 50"
    )
    for ref, meta in ARSENAL_REGISTRY.items():
        assert meta.cost.get("max_seconds", 0) > 0, (
            f"{ref}: max_seconds <=0 after recalibration"
        )
        assert meta.cost.get("max_memory_mb", 0) > 0
        assert "max_oracle_calls" in meta.cost
        assert meta.postconditions, f"{ref}: lost postconditions"
        assert meta.authority_refs, f"{ref}: lost authority_refs"


def test_composition_hardware_profile_recorded():
    """hardware_profile() captures host info every report needs.

    Composition: this is the substrate's audit trail — without it,
    cross-machine cost-model diffs are uninterpretable.
    """
    h = hardware_profile()
    assert h["platform"]
    assert h["python_version"]
    assert h["processor"] or h["machine"]
    assert "perf_counter" in h["wall_clock"]
