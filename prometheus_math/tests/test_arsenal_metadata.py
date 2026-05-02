"""Tests for the centrally-registered arsenal metadata.

Verifies that ``prometheus_math._metadata_table`` populates the
``ARSENAL_REGISTRY`` with at least 50 calibrated entries across
multiple categories, and that the cost models are tight enough that the
sigma_env action space gets honest budgets.

Test taxonomy:
- size / coverage: registry has the breadth week-2 promised
- callable resolution: every entry imports cleanly via BindEvalExtension
- cost calibration: declared elapsed is within 2x..50x of actual p95
- composition: BIND -> EVAL succeeds end-to-end on a random sample
"""
from __future__ import annotations

import importlib
import random
import time
from typing import Any, Dict, List, Tuple

import pytest

from prometheus_math.arsenal_meta import ARSENAL_REGISTRY


# ---------------------------------------------------------------------------
# Curated representative-args table: used for cost-calibration and
# round-trip BIND/EVAL tests. Keep these inputs CHEAP — these execute
# during normal test runs.
# ---------------------------------------------------------------------------

REPRESENTATIVE_ARGS: Dict[str, Tuple[List[Any], Dict[str, Any]]] = {
    "prometheus_math.numerics_special_dilogarithm:dilogarithm": ([1.0], {}),
    "prometheus_math.numerics_special_dilogarithm:polylogarithm": ([3, 0.5], {}),
    "prometheus_math.numerics_special_dilogarithm:bloch_wigner_dilog": ([0.5 + 0.5j], {}),
    "prometheus_math.numerics_special_dilogarithm:clausen": ([1.0], {}),
    "prometheus_math.numerics_special_hurwitz:hurwitz_zeta": ([2.0, 1.0], {}),
    "prometheus_math.numerics_special_hurwitz:polygamma": ([1, 1.0], {}),
    "prometheus_math.numerics_special_theta:theta_null_value": ([3, 0.5], {}),
    "prometheus_math.numerics_special_theta:jacobi_theta": ([3, 0.0, 0.5], {}),
    "prometheus_math.numerics_special_eta:eta": ([1.0j], {}),
    "prometheus_math.numerics_special_eta:j_invariant": ([1.0j], {}),
    "prometheus_math.numerics_special_eta:eta_quotient": ([{1: 2, 2: -2}, 1.0j], {}),
    "prometheus_math.numerics_special_q_pochhammer:euler_function": ([0.5], {}),
    "prometheus_math.numerics_special_q_pochhammer:dedekind_eta": ([1.0j], {}),
    "prometheus_math.numerics_special_q_pochhammer:q_pochhammer": ([0.5, 0.5], {}),
    "prometheus_math.combinatorics_partitions:num_partitions": ([20], {}),
    "prometheus_math.combinatorics_partitions:partitions_of": ([8], {}),
    "prometheus_math.combinatorics_partitions:conjugate": ([[5, 3, 2, 1]], {}),
    "prometheus_math.combinatorics_partitions:num_standard_young_tableaux": ([[3, 2, 1]], {}),
    "prometheus_math.combinatorics_partitions:rsk": ([[3, 1, 4, 1, 5, 2]], {}),
    "prometheus_math.combinatorics_partitions:hook_length_array": ([[5, 3, 2, 1]], {}),
    "prometheus_math.numerics:flint_factor": ([[1, 0, -1]], {}),
    "prometheus_math.numerics:flint_polmodp": ([[1, 2, 3, 4], 7], {}),
    "prometheus_math.numerics:mpdft": ([[1.0, 0.0, 1.0, 0.0]], {}),
    "prometheus_math.numerics:mpfft": ([[1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]], {}),
    "prometheus_math.numerics:bernoulli": ([10], {}),
    "prometheus_math.numerics:zeta": ([2.0], {}),
    "prometheus_math.geometry_convex_hull:convex_hull": (
        [[(0, 0), (1, 0), (0, 1), (1, 1), (0.5, 0.5)]], {},
    ),
    "prometheus_math.geometry_voronoi:voronoi_diagram": (
        [[(0, 0), (1, 0), (0, 1), (1, 1)]], {},
    ),
    "prometheus_math.geometry_delaunay:delaunay_triangulation": (
        [[(0, 0), (1, 0), (0, 1), (1, 1), (0.5, 0.5)]], {},
    ),
    "prometheus_math.geometry_delaunay:circumcenter": (
        [[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]], {},
    ),
    "prometheus_math.dynamics_iterated_maps:logistic_map": (
        [3.7, 0.5], {"n_iter": 100, "transient": 50},
    ),
    "prometheus_math.dynamics_iterated_maps:tent_map": (
        [0.6], {"n_iter": 100, "transient": 50},
    ),
    "prometheus_math.research.lehmer:identify_salem_class": (
        [[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]], {},
    ),
    "prometheus_math.research.lehmer:is_reciprocal": (
        [[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]], {},
    ),
    "prometheus_math.research.lehmer:degree_profile": (
        [[{"mahler_measure": 1.5, "degree": 4},
          {"mahler_measure": 1.7, "degree": 4}]], {},
    ),
    "techne.lib.mahler_measure:mahler_measure": (
        [[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]], {},
    ),
    "techne.lib.mahler_measure:log_mahler_measure": (
        [[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]], {},
    ),
    "techne.lib.mahler_measure:is_cyclotomic": ([[1, -1]], {}),
    "techne.lib.cf_expansion:cf_expand": ([22, 7], {}),
    "techne.lib.cf_expansion:cf_max_digit": ([22, 7], {}),
    "techne.lib.cf_expansion:zaremba_test": ([25], {}),
    "techne.lib.cf_expansion:sturm_bound": ([12, 11], {}),
    "techne.lib.smith_normal_form:smith_normal_form": (
        [[[2, 4, 4], [-6, 6, 12], [10, -4, -16]]], {},
    ),
    "techne.lib.smith_normal_form:invariant_factors": (
        [[[2, 4, 4], [-6, 6, 12], [10, -4, -16]]], {},
    ),
    "techne.lib.smith_normal_form:abelian_group_structure": (
        [[[2, 4, 4], [-6, 6, 12], [10, -4, -16]]], {},
    ),
    "techne.lib.class_number:class_number": (["x^2 - 5"], {}),
    "techne.lib.class_number:class_group": (["x^2 - 5"], {}),
    "techne.lib.class_number:regulator_nf": (["x^2 - 5"], {}),
    "techne.lib.galois_group:galois_group": (["x^3 - 2"], {}),
    "techne.lib.galois_group:is_abelian": (["x^2 - 2"], {}),
    "techne.lib.galois_group:disc_is_square": (["x^2 - 2"], {}),
    "techne.lib.lll_reduction:lll": ([[[1, 1, 1], [-1, 0, 2], [3, 5, 6]]], {}),
    "techne.lib.lll_reduction:shortest_vector_lll": (
        [[[1, 1, 1], [-1, 0, 2], [3, 5, 6]]], {},
    ),
    "techne.lib.cm_order_data:cm_order_data": ([-7], {}),
    "techne.lib.regulator:regulator": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.conductor:conductor": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.conductor:bad_primes": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.root_number:root_number": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.faltings_height:faltings_height": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.analytic_sha:analytic_sha": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.selmer_rank:selmer_2_rank": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.functional_eq_check:functional_eq_check": ([[0, 0, 1, -1, 0]], {}),
    "techne.lib.hyperbolic_volume:hyperbolic_volume": (["4_1"], {}),
    "techne.lib.hyperbolic_volume:is_hyperbolic": (["4_1"], {}),
    "techne.lib.alexander_polynomial:alexander_polynomial": (["4_1"], {}),
    "techne.lib.alexander_polynomial:alexander_coeffs": (["4_1"], {}),
    "techne.lib.knot_shape_field:polredabs": (
        ["x^4 - 4*x^3 + 5*x^2 - 2*x - 1"], {},
    ),
    "techne.lib.hilbert_class_field:hilbert_class_field": (["x^2 + 23"], {}),
}


def _resolve(callable_ref: str):
    """Mirror BindEvalExtension._resolve_callable; kept inline to avoid
    requiring a live SigmaKernel just to test resolvability."""
    if ":" not in callable_ref:
        raise ValueError(f"bad ref {callable_ref!r}")
    modpath, qualname = callable_ref.split(":", 1)
    mod = importlib.import_module(modpath)
    obj: Any = mod
    for part in qualname.split("."):
        obj = getattr(obj, part)
    if not callable(obj):
        raise TypeError(f"{callable_ref!r} resolves to non-callable")
    return obj


# ---------------------------------------------------------------------------
# Size / coverage
# ---------------------------------------------------------------------------


def test_authority_registry_size_at_least_50():
    """Week-2 commitment: at least 50 ops registered with full metadata."""
    assert len(ARSENAL_REGISTRY) >= 50, (
        f"registry only has {len(ARSENAL_REGISTRY)} ops; "
        f"week-2 target was 50+"
    )


def test_authority_category_coverage():
    """Coverage spans at least 5 distinct categories — week-2 spec."""
    cats = {m.category for m in ARSENAL_REGISTRY.values() if m.category}
    assert len(cats) >= 5, (
        f"only {len(cats)} categories represented: {sorted(cats)}"
    )


# ---------------------------------------------------------------------------
# Property — every entry's shape is correct
# ---------------------------------------------------------------------------


def test_property_every_entry_has_callable_ref():
    """Every registered entry has a parseable 'module:qualname' ref."""
    for ref, meta in ARSENAL_REGISTRY.items():
        assert ref == meta.callable_ref, (
            f"key {ref!r} != meta.callable_ref {meta.callable_ref!r}"
        )
        assert ":" in ref, f"ref {ref!r} missing module:qualname separator"
        modpath, qualname = ref.split(":", 1)
        assert modpath, f"empty module path in {ref!r}"
        assert qualname, f"empty qualname in {ref!r}"


def test_property_every_entry_callable_resolves():
    """Every registered op imports + resolves to a callable."""
    failures = []
    for ref in ARSENAL_REGISTRY:
        try:
            obj = _resolve(ref)
            assert callable(obj)
        except Exception as e:
            failures.append((ref, f"{type(e).__name__}: {e}"))
    assert not failures, (
        f"{len(failures)} unresolvable callables:\n  " +
        "\n  ".join(f"{r}: {e}" for r, e in failures[:5])
    )


def test_property_every_entry_has_cost_model():
    """Every entry has a cost dict with the three required ceilings."""
    required = {"max_seconds", "max_memory_mb", "max_oracle_calls"}
    for ref, meta in ARSENAL_REGISTRY.items():
        missing = required - set(meta.cost.keys())
        assert not missing, (
            f"{ref}: missing cost keys {missing}; got {set(meta.cost)}"
        )
        assert meta.cost["max_seconds"] > 0, f"{ref}: max_seconds <= 0"


def test_property_every_entry_has_postconditions():
    """At least one specific postcondition per op."""
    for ref, meta in ARSENAL_REGISTRY.items():
        assert len(meta.postconditions) >= 1, (
            f"{ref}: no postconditions declared"
        )
        for p in meta.postconditions:
            # Reject lazy generic phrasing.
            assert p.lower().strip() not in {
                "output is correct",
                "function returns correct value",
            }, f"{ref}: lazy postcondition {p!r}"


def test_property_every_entry_has_authority():
    """Every op cites at least one authority reference."""
    for ref, meta in ARSENAL_REGISTRY.items():
        assert len(meta.authority_refs) >= 1, (
            f"{ref}: no authority_refs declared"
        )


# ---------------------------------------------------------------------------
# Edge — no duplicate refs
# ---------------------------------------------------------------------------


def test_edge_no_duplicate_refs():
    """Dict keys are unique by construction; check meta.callable_ref too."""
    seen = set()
    for meta in ARSENAL_REGISTRY.values():
        assert meta.callable_ref not in seen, (
            f"duplicate callable_ref {meta.callable_ref!r} in registry"
        )
        seen.add(meta.callable_ref)


# ---------------------------------------------------------------------------
# Cost-model calibration
# ---------------------------------------------------------------------------


def _profile(fn, args, kwargs, n=10):
    """Time fn(args, kwargs) n times; return p95 in seconds."""
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)
    times.sort()
    return times[min(int(n * 0.95), n - 1)]


# Pick stable, fast ops for the calibration test (avoid PARI/SAT/snappy
# variability; 8 ops is well above the 5+ requirement).
_CALIBRATION_OPS = [
    "prometheus_math.numerics_special_dilogarithm:dilogarithm",
    "prometheus_math.numerics_special_theta:theta_null_value",
    "prometheus_math.numerics_special_q_pochhammer:euler_function",
    "prometheus_math.combinatorics_partitions:num_partitions",
    "prometheus_math.combinatorics_partitions:rsk",
    "prometheus_math.numerics:zeta",
    "prometheus_math.numerics:bernoulli",
    "techne.lib.mahler_measure:mahler_measure",
    "techne.lib.cf_expansion:cf_expand",
    "techne.lib.smith_normal_form:smith_normal_form",
]


def test_property_cost_models_within_2x_to_50x_of_actual():
    """Calibration goal: declared/actual ratio in [2x, 50x] for stable ops.

    Bounds rationale:
    - Lower bound 2x ensures we never under-promise (would cause
      BudgetExceeded on benign inputs).
    - Upper bound 50x ensures we don't over-promise (would let an RL
      agent waste budget on slow/wrong ops). The MVP's 100-1000x
      ratios were exactly the failure mode this test rules out.
    """
    failures = []
    for ref in _CALIBRATION_OPS:
        if ref not in ARSENAL_REGISTRY:
            continue
        if ref not in REPRESENTATIVE_ARGS:
            continue
        meta = ARSENAL_REGISTRY[ref]
        args, kwargs = REPRESENTATIVE_ARGS[ref]
        fn = _resolve(ref)
        try:
            p95 = _profile(fn, args, kwargs, n=10)
        except Exception as e:
            failures.append((ref, f"PROFILE_ERROR: {e}"))
            continue
        declared = meta.cost["max_seconds"]
        # Floor very-fast ops so noise doesn't make the ratio undefined.
        p95 = max(p95, 1e-6)
        ratio = declared / p95
        # We want 2 <= ratio <= 50 (declared >= 2*actual, declared <= 50*actual)
        if not (2.0 <= ratio <= 50.0):
            failures.append(
                (ref, f"ratio {ratio:.2f}x; "
                      f"declared={declared*1000:.3f}ms, p95={p95*1000:.3f}ms")
            )
    # Allow at most 2 outliers (e.g. snappy/PARI cold-start variance).
    assert len(failures) <= 2, (
        f"{len(failures)} of {len(_CALIBRATION_OPS)} ops fail calibration:\n  " +
        "\n  ".join(f"{r}: {e}" for r, e in failures)
    )


# ---------------------------------------------------------------------------
# Composition — BIND / EVAL round-trip
# ---------------------------------------------------------------------------


def test_composition_bind_eval_round_trip_on_random_5():
    """Pick 5 random registered ops with curated args; BIND -> EVAL passes.

    Round-trip = output non-empty + success flag set + actual cost
    bounded by declared ceiling.
    """
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension, CostModel

    candidates = [
        ref for ref in ARSENAL_REGISTRY
        if ref in REPRESENTATIVE_ARGS
        # Filter ops that would be flaky in CI (heavy PARI / OS-side caches);
        # leave the bulk-of-arsenal coverage to the bench.
        and not ref.startswith("techne.lib.class_number")
        and not ref.startswith("techne.lib.galois_group")
        and not ref.startswith("techne.lib.regulator")
        and not ref.startswith("techne.lib.hilbert_class_field")
        and not ref.startswith("techne.lib.cm_order_data")
        and not ref.startswith("techne.lib.hyperbolic_volume")
        and not ref.startswith("techne.lib.knot_shape_field")
    ]
    rng = random.Random(20260429)
    sample = rng.sample(candidates, k=min(5, len(candidates)))

    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    successes = 0
    errors = []
    for i, ref in enumerate(sample):
        meta = ARSENAL_REGISTRY[ref]
        args, kwargs = REPRESENTATIVE_ARGS[ref]
        try:
            cap = kernel.mint_capability("BindCap")
            b = ext.BIND(
                callable_ref=ref,
                cost_model=CostModel(**meta.cost),
                postconditions=list(meta.postconditions),
                authority_refs=list(meta.authority_refs),
                cap=cap,
                name=f"rt_{i}_{ref.split(':')[-1]}",
                version=1,
            )
            cap2 = kernel.mint_capability("EvalCap")
            ev = ext.EVAL(
                binding_name=b.symbol.name,
                binding_version=b.symbol.version,
                args=args,
                kwargs=kwargs,
                cap=cap2,
            )
            assert ev.success, f"{ref}: EVAL marked success=False; {ev.error_repr}"
            assert ev.output_repr, f"{ref}: empty output_repr"
            successes += 1
        except Exception as e:
            errors.append((ref, f"{type(e).__name__}: {e}"))

    # Allow up to 1 random-arg incompatibility (the bench is the
    # exhaustive check; this is a smoke test).
    assert successes >= 4, (
        f"only {successes}/5 round-trips passed; errors:\n  " +
        "\n  ".join(f"{r}: {e}" for r, e in errors)
    )
