"""Tests for sigma_kernel.triangulation_protocol — P6 Tier 2 (substrate v2.3 §6.3).

Coverage:

  * MethodClass + TriangulationVerdict enum membership invariants.
  * INDEPENDENCE_TO_METHOD_CLASS registry covers the 12 non-UNKNOWN
    IndependenceClass values + UNKNOWN defaults to EXPLORATORY.
  * TriangulationPath construction, ``is_proof_bearing``, ``can_certify``
    (clustering CANNOT certify hard rule).
  * TriangulationProtocol.evaluate full upgrade-rule decision tree:
    INCONCLUSIVE_WAITING / CONTRADICTED / REJECTED /
    INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE / UPGRADED_TO_LOCAL_LEMMA.
  * Lehmer prototype case (Day 5 sprint): 4 paths, sympy is the
    proof-bearing primary, mpmath + catalog provide independent replays,
    clustering nominates but cannot certify → UPGRADED.
  * can_upgrade fast-path matches evaluate() result.
"""
from __future__ import annotations

import time

import pytest

from sigma_kernel.method_spec import IndependenceClass, MethodSpec
from sigma_kernel.triangulation_protocol import (
    INDEPENDENCE_TO_METHOD_CLASS,
    MethodClass,
    TriangulationPath,
    TriangulationProtocol,
    TriangulationResult,
    TriangulationVerdict,
    method_class_for_independence_class,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _make_path(
    path_id: str,
    independence_class: IndependenceClass,
    verdict: str = "verified",
    *,
    method_class: MethodClass = None,
    engine: str = "engine",
    strategy: str = "direct",
    runtime_ms: int = 100,
    rationale: str = "ok",
) -> TriangulationPath:
    """Construct a TriangulationPath with sensible defaults for testing."""
    spec = MethodSpec(
        engine=engine,
        strategy=strategy,
        independence_class=independence_class,
    )
    if method_class is None:
        method_class = method_class_for_independence_class(independence_class)
    return TriangulationPath(
        path_id=path_id,
        method_spec=spec,
        method_class=method_class,
        verdict=verdict,
        runtime_ms=runtime_ms,
        rationale=rationale,
        timestamp=time.time(),
    )


# ===========================================================================
# MethodClass enum
# ===========================================================================


def test_method_class_enum_has_5_values():
    """v2.3 §6.3 P6 specifies exactly 5 method classes."""
    assert len(MethodClass) == 5
    assert {m.value for m in MethodClass} == {
        "proof_bearing",
        "numerical",
        "catalog",
        "robustness",
        "exploratory",
    }


def test_method_class_is_string_compatible():
    """str-mixin → enum members compare equal to underlying string."""
    assert MethodClass.PROOF_BEARING == "proof_bearing"
    assert MethodClass.EXPLORATORY == "exploratory"


# ===========================================================================
# TriangulationVerdict enum
# ===========================================================================


def test_triangulation_verdict_enum_has_5_values():
    """v2.3 §6.3 P6 produces five terminal verdicts."""
    assert len(TriangulationVerdict) == 5
    assert {v.value for v in TriangulationVerdict} == {
        "inconclusive_waiting",
        "inconclusive_insufficient_independence",
        "upgraded_to_local_lemma",
        "contradicted",
        "rejected",
    }


# ===========================================================================
# INDEPENDENCE_TO_METHOD_CLASS registry + lookup helper
# ===========================================================================


def test_independence_to_method_class_covers_all_classified_independence_classes():
    """All 13 IndependenceClass values minus UNKNOWN must be classified.

    UNKNOWN deliberately has no entry — the lookup helper falls through
    to EXPLORATORY (conservative default; cannot certify).
    """
    classified = set(INDEPENDENCE_TO_METHOD_CLASS.keys())
    expected = {ic.value for ic in IndependenceClass} - {"unknown"}
    assert classified == expected
    # Exactly 12 classified entries; UNKNOWN deliberately absent.
    assert len(INDEPENDENCE_TO_METHOD_CLASS) == 12
    assert "unknown" not in INDEPENDENCE_TO_METHOD_CLASS


def test_method_class_for_unknown_independence_class_is_exploratory():
    """Conservative default: an unknown IC cannot be silently certifying."""
    assert method_class_for_independence_class("unknown") == MethodClass.EXPLORATORY
    assert method_class_for_independence_class(IndependenceClass.UNKNOWN) == MethodClass.EXPLORATORY


def test_method_class_for_arbitrary_unregistered_string_is_exploratory():
    """Unregistered IC strings also fall through to EXPLORATORY (safe default)."""
    assert method_class_for_independence_class("future_quantum_oracle") == MethodClass.EXPLORATORY
    assert method_class_for_independence_class("") == MethodClass.EXPLORATORY


def test_method_class_lookup_for_proof_bearing():
    assert method_class_for_independence_class(
        IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION
    ) == MethodClass.PROOF_BEARING


def test_method_class_lookup_for_numerical():
    for ic in (
        IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
        IndependenceClass.PARI_NUMBER_FIELD,
        IndependenceClass.SAGE_ELLIPTIC_CURVE,
        IndependenceClass.NUMPY_LINEAR_ALGEBRA,
    ):
        assert method_class_for_independence_class(ic) == MethodClass.NUMERICAL


def test_method_class_lookup_for_catalog():
    for ic in (
        IndependenceClass.MAHLER_LOOKUP_CATALOG,
        IndependenceClass.LMFDB_CATALOG,
        IndependenceClass.OEIS_CATALOG,
        IndependenceClass.LITERATURE_CROSS_CHECK,
    ):
        assert method_class_for_independence_class(ic) == MethodClass.CATALOG


def test_method_class_lookup_for_robustness_and_exploratory():
    assert method_class_for_independence_class(
        IndependenceClass.PERTURBATION_ROBUSTNESS
    ) == MethodClass.ROBUSTNESS
    assert method_class_for_independence_class(
        IndependenceClass.CLUSTERING_BOUNDARY
    ) == MethodClass.EXPLORATORY


# ===========================================================================
# TriangulationPath construction + properties
# ===========================================================================


def test_triangulation_path_construction():
    p = _make_path("path-1", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION)
    assert p.path_id == "path-1"
    assert p.method_class == MethodClass.PROOF_BEARING
    assert p.verdict == "verified"
    assert p.runtime_ms == 100
    assert p.method_spec.independence_class == IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION


def test_triangulation_path_is_frozen():
    """Path objects are immutable so ledger rows can't be silently mutated."""
    p = _make_path("p", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION)
    with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError or similar
        p.verdict = "contradicted"  # type: ignore[misc]


def test_path_is_proof_bearing_for_proof_bearing_class():
    p = _make_path("p", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION)
    assert p.is_proof_bearing is True
    assert p.can_certify is True


def test_path_is_proof_bearing_for_numerical_class_is_false():
    """Numerical paths are NOT proof-bearing (precision replication only)."""
    p = _make_path("p", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION)
    assert p.is_proof_bearing is False
    assert p.can_certify is True  # numerical can certify (just not primarily)


def test_path_can_certify_for_exploratory_is_false():
    """Clustering CANNOT certify per substrate v2.3 §6.3 hard rule."""
    p = _make_path("p", IndependenceClass.CLUSTERING_BOUNDARY)
    assert p.is_proof_bearing is False
    assert p.can_certify is False


# ===========================================================================
# TriangulationProtocol.evaluate — decision tree
# ===========================================================================


def test_evaluate_with_zero_paths_returns_inconclusive_waiting():
    proto = TriangulationProtocol()
    result = proto.evaluate([])
    assert result.verdict == TriangulationVerdict.INCONCLUSIVE_WAITING
    assert result.upgrade_eligible is False


def test_evaluate_with_two_paths_returns_inconclusive_waiting():
    proto = TriangulationProtocol()
    paths = [
        _make_path("p1", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("p2", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.INCONCLUSIVE_WAITING
    assert result.upgrade_eligible is False
    assert "≥3" in result.summary or "3" in result.summary


def test_evaluate_three_verified_with_proof_bearing_and_independent_replay_upgrades():
    """Canonical happy path: proof-bearing primary + 2 independent replays."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),  # proof-bearing
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),  # numerical
        _make_path("mahler", IndependenceClass.MAHLER_LOOKUP_CATALOG),  # catalog
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA
    assert result.upgrade_eligible is True
    assert len(result.paths_run) == 3
    assert IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION in result.independence_classes_covered
    assert MethodClass.PROOF_BEARING in result.method_classes_covered
    assert MethodClass.NUMERICAL in result.method_classes_covered
    assert MethodClass.CATALOG in result.method_classes_covered


def test_evaluate_only_exploratory_paths_returns_REJECTED():
    """Canonical hard-rule test: clustering CANNOT certify alone."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("c1", IndependenceClass.CLUSTERING_BOUNDARY, engine="engine_a"),
        _make_path("c2", IndependenceClass.CLUSTERING_BOUNDARY, engine="engine_b"),
        _make_path("c3", IndependenceClass.CLUSTERING_BOUNDARY, engine="engine_c"),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.REJECTED
    assert result.upgrade_eligible is False
    assert "cannot certify" in result.summary.lower() or "exploratory" in result.summary.lower()


def test_evaluate_no_proof_bearing_only_numerical_returns_REJECTED():
    """Three numerical paths is precision replication, not triangulation."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("n1", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("n2", IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING),
        _make_path("n3", IndependenceClass.NUMPY_LINEAR_ALGEBRA),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.REJECTED
    assert result.upgrade_eligible is False


def test_evaluate_three_same_independence_class_returns_INSUFFICIENT_INDEPENDENCE():
    """Three numerical paths sharing the same IC: precision replication only."""
    proto = TriangulationProtocol()
    # Force one of them to be PROOF_BEARING via override so we exercise the
    # independence-check branch (not the proof-bearing-missing branch).
    paths = [
        _make_path(
            "p1",
            IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
            method_class=MethodClass.PROOF_BEARING,
        ),
        _make_path("p2", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("p3", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE
    assert result.upgrade_eligible is False


def test_evaluate_one_path_contradicted_returns_CONTRADICTED():
    """Any contradiction is a substrate finding; supersedes other rules."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        _make_path(
            "mpmath",
            IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
            "verified",
        ),
        _make_path("catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG, "contradicted"),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.CONTRADICTED
    assert result.upgrade_eligible is False
    assert "contradict" in result.summary.lower()


def test_evaluate_contradiction_supersedes_proof_bearing_success():
    """Even if proof-bearing path verified, a contradicting path wins."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),
        _make_path("catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG, "contradicted"),
        _make_path("oeis", IndependenceClass.OEIS_CATALOG, "verified"),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.CONTRADICTED


def test_evaluate_inconclusive_paths_treated_as_neither_verified_nor_contradicted():
    """Three inconclusive paths → no proof-bearing-verified → REJECTED."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("p1", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "inconclusive"),
        _make_path("p2", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "inconclusive"),
        _make_path("p3", IndependenceClass.MAHLER_LOOKUP_CATALOG, "inconclusive"),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.REJECTED
    assert result.upgrade_eligible is False


def test_evaluate_proof_bearing_plus_robustness_replay_upgrades():
    """Robustness paths are valid independent replays (not just numerical/catalog)."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("perturb", IndependenceClass.PERTURBATION_ROBUSTNESS),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA
    assert MethodClass.ROBUSTNESS in result.method_classes_covered


def test_evaluate_upgrade_independence_classes_covered_correct():
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("mahler", IndependenceClass.MAHLER_LOOKUP_CATALOG),
    ]
    result = proto.evaluate(paths)
    assert result.independence_classes_covered == frozenset({
        IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        IndependenceClass.MAHLER_LOOKUP_CATALOG,
    })


# ===========================================================================
# can_upgrade — fast-path predicate
# ===========================================================================


def test_can_upgrade_true_only_for_upgrade_path():
    proto = TriangulationProtocol()
    upgrade_paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("mahler", IndependenceClass.MAHLER_LOOKUP_CATALOG),
    ]
    assert proto.can_upgrade(upgrade_paths) is True


def test_can_upgrade_false_for_under_three_paths():
    proto = TriangulationProtocol()
    assert proto.can_upgrade([]) is False
    assert proto.can_upgrade([
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
    ]) is False


def test_can_upgrade_false_for_only_exploratory():
    proto = TriangulationProtocol()
    paths = [
        _make_path("c1", IndependenceClass.CLUSTERING_BOUNDARY, engine="a"),
        _make_path("c2", IndependenceClass.CLUSTERING_BOUNDARY, engine="b"),
        _make_path("c3", IndependenceClass.CLUSTERING_BOUNDARY, engine="c"),
    ]
    assert proto.can_upgrade(paths) is False


def test_can_upgrade_false_for_contradiction():
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),
        _make_path("catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG, "contradicted"),
    ]
    assert proto.can_upgrade(paths) is False


# ===========================================================================
# Lehmer prototype (Day 5 sprint case)
# ===========================================================================


def test_lehmer_prototype_four_paths_upgrades():
    """Day 5 Lehmer brute-force INCONCLUSIVE → H5_CONFIRMED-local-lemma case.

    Four paths:
      A: mpmath_factor_first  (numerical)        verified
      B: sympy symbolic       (proof-bearing)    verified
      C: mahler catalog       (catalog)          verified
      D: clustering_boundary  (exploratory)      verified — nominates only

    sympy is the proof-bearing primary; mpmath + catalog provide
    independent replays. clustering nominates boundary structure but
    cannot certify on its own.
    """
    proto = TriangulationProtocol()
    paths = [
        _make_path("path_a_mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("path_b_sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("path_c_catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG),
        _make_path("path_d_clustering", IndependenceClass.CLUSTERING_BOUNDARY),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA
    assert result.upgrade_eligible is True
    # All four method classes represented in the coverage record.
    assert result.method_classes_covered >= {
        MethodClass.PROOF_BEARING,
        MethodClass.NUMERICAL,
        MethodClass.CATALOG,
        MethodClass.EXPLORATORY,
    }


def test_lehmer_prototype_without_sympy_returns_REJECTED():
    """Same Lehmer paths minus the proof-bearing sympy → cannot certify."""
    proto = TriangulationProtocol()
    paths = [
        _make_path("path_a_mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("path_c_catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG),
        _make_path("path_d_clustering", IndependenceClass.CLUSTERING_BOUNDARY),
    ]
    result = proto.evaluate(paths)
    assert result.verdict == TriangulationVerdict.REJECTED


# ===========================================================================
# Result immutability + summary content
# ===========================================================================


def test_triangulation_result_is_frozen():
    proto = TriangulationProtocol()
    result = proto.evaluate([])
    with pytest.raises((AttributeError, Exception)):
        result.verdict = TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA  # type: ignore[misc]


def test_upgrade_summary_mentions_proof_bearing_and_replay_count():
    proto = TriangulationProtocol()
    paths = [
        _make_path("sympy", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        _make_path("mpmath", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        _make_path("catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG),
    ]
    result = proto.evaluate(paths)
    s = result.summary.lower()
    assert "proof-bearing" in s
    assert "independent replay" in s or "replay" in s
