"""
Substrate-Tester Fire #4 — Lane 3 (correlated-triangulation) + Lane 6 (undecidable-canonicalization)

Lane 3: TriangulationProtocol independence-enforcement. 5 cases:
  - 3 verified proof-bearing paths, 2 sharing independence_class -> must NOT upgrade
  - 3 paths, none proof-bearing -> REJECTED
  - 3 paths, all distinct, >=1 proof-bearing, all verified -> UPGRADED (positive control)
  - 2 paths -> INCONCLUSIVE_WAITING
  - 1 contradicted path -> CONTRADICTED

Lane 6: CanonicalizationProtocol decidability-flag enforcement. 4 cases:
  - decidability_status='undecidable' accepts
  - decidability_status='maybe' (invalid) raises
  - undecidable canonicalize() with no impl raises NotImplementedError
  - registered Lehmer chart has decidability_status set

Author: substrate-tester (Charon-aligned), fire #4, 2026-05-06
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 3 — correlated-triangulation
# ---------------------------------------------------------------------------


def lane_3_correlated_triangulation() -> dict:
    """5 cases against TriangulationProtocol.evaluate."""
    from sigma_kernel.triangulation_protocol import (
        TriangulationProtocol,
        TriangulationPath,
        TriangulationVerdict,
        MethodClass,
        method_class_for_independence_class,
    )
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec

    proto = TriangulationProtocol()

    def make_path(path_id: str, ic: IndependenceClass, verdict: str) -> TriangulationPath:
        ms = MethodSpec(
            engine="test",
            strategy="probe",
            version="1.0.0",
            independence_class=ic,
        )
        mc = method_class_for_independence_class(ic.value)
        return TriangulationPath(
            path_id=path_id,
            method_spec=ms,
            method_class=mc,
            verdict=verdict,
            runtime_ms=0,
            rationale=f"test path {path_id}",
            timestamp=0.0,
        )

    tests = []

    # Test 1: 3 verified proof-bearing paths, 2 sharing independence_class
    # -> MUST NOT upgrade.
    paths_t1 = [
        make_path("p1_mpmath_factor_a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),
        make_path("p2_mpmath_factor_b", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),  # SAME class
        make_path("p3_sympy_symbolic", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
    ]
    res_t1 = proto.evaluate(paths_t1)
    # The expectation: substrate must NOT upgrade because primary-replay
    # independence is not satisfied (p1 and p2 share class). Either:
    #   - INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE if the protocol picks p1 or p2 as primary
    #     and finds p3 as the only different-class path (which would be sufficient)
    #   - OR it correctly upgrades because p1/p3 ARE different classes
    # Reading the upgrade rule: it picks proof_bearing_verified[0] as primary, finds
    # ANY verified path with different independence_class. So with [p1, p2, p3]:
    #   primary = p1; independent_replays = [p3] (p2 same class as p1 fails diff filter)
    # → UPGRADES. The independence rule is "primary needs ≥1 different-class verified peer."
    #
    # So the actual lane-3 critical-bug test must construct a case where ALL non-primary
    # verified paths share the primary's class. Reset Test 1 to that.
    # (Will keep this test as observation; rewriting Test 1 below.)
    tests.append({
        "id": "T1_three_proof_bearing_2_shared_class",
        "expected": "Verdict depends on whether ANY independent-class peer exists",
        "actual": f"verdict={res_t1.verdict.name}, summary={res_t1.summary[:100]}",
        "verdict": "OBSERVATION",
        "severity": None,
        "note": (
            "Read of upgrade rule: 'independent replay' = different-class than "
            "primary-proof-bearing. With 3 paths and only 2 sharing class, the third "
            "path provides the required independence -> UPGRADE is correct."
        ),
    })

    # Test 1b: 3 verified paths, ALL sharing the same PROOF_BEARING
    # independence_class. Only SYMPY_SYMBOLIC_FACTORIZATION maps to
    # PROOF_BEARING in the registered map; using it here means primary
    # IS proof-bearing-verified, so the substrate must NOT short-circuit
    # to REJECTED — it must reach the independence rule and return
    # INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE because no path has a
    # different IC.
    paths_t1b = [
        make_path("p1_sympy_a", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        make_path("p2_sympy_b", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        make_path("p3_sympy_c", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
    ]
    res_t1b = proto.evaluate(paths_t1b)
    if res_t1b.verdict == TriangulationVerdict.INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE:
        tests.append({
            "id": "T1b_three_verified_all_same_class",
            "expected": "INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE (no independent replay)",
            "actual": f"verdict={res_t1b.verdict.name}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T1b_three_verified_all_same_class",
            "expected": "INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE",
            "actual": f"verdict={res_t1b.verdict.name}, summary={res_t1b.summary[:120]}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "substrate accepted correlated paths as triangulation",
        })

    # Test 2: 3 paths verified but NONE proof-bearing (clustering only)
    paths_t2 = [
        make_path("p1_clu_a", IndependenceClass.CLUSTERING_BOUNDARY, "verified"),
        make_path("p2_clu_b", IndependenceClass.CLUSTERING_BOUNDARY, "verified"),
        make_path("p3_perturb", IndependenceClass.PERTURBATION_ROBUSTNESS, "verified"),
    ]
    res_t2 = proto.evaluate(paths_t2)
    if res_t2.verdict == TriangulationVerdict.REJECTED:
        tests.append({
            "id": "T2_no_proof_bearing_paths",
            "expected": "REJECTED (clustering/exploratory cannot certify alone)",
            "actual": f"verdict={res_t2.verdict.name}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T2_no_proof_bearing_paths",
            "expected": "REJECTED",
            "actual": f"verdict={res_t2.verdict.name}, summary={res_t2.summary[:120]}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    # Test 3: positive control. 3 verified paths, ≥1 proof-bearing, all distinct.
    paths_t3 = [
        make_path("p1_proof", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        make_path("p2_replay", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),
        make_path("p3_catalog", IndependenceClass.MAHLER_LOOKUP_CATALOG, "verified"),
    ]
    res_t3 = proto.evaluate(paths_t3)
    if res_t3.verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA:
        tests.append({
            "id": "T3_positive_control_upgrade",
            "expected": "UPGRADED_TO_LOCAL_LEMMA",
            "actual": f"verdict={res_t3.verdict.name}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T3_positive_control_upgrade",
            "expected": "UPGRADED_TO_LOCAL_LEMMA",
            "actual": f"verdict={res_t3.verdict.name}, summary={res_t3.summary[:120]}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "substrate refuses to upgrade legitimate triangulation",
        })

    # Test 4: only 2 paths
    paths_t4 = [
        make_path("p1", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        make_path("p2", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),
    ]
    res_t4 = proto.evaluate(paths_t4)
    if res_t4.verdict == TriangulationVerdict.INCONCLUSIVE_WAITING:
        tests.append({
            "id": "T4_only_two_paths",
            "expected": "INCONCLUSIVE_WAITING",
            "actual": f"verdict={res_t4.verdict.name}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T4_only_two_paths",
            "expected": "INCONCLUSIVE_WAITING",
            "actual": f"verdict={res_t4.verdict.name}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # Test 5: a contradicted path
    paths_t5 = [
        make_path("p1", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION, "verified"),
        make_path("p2", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION, "verified"),
        make_path("p3_contradicted", IndependenceClass.MAHLER_LOOKUP_CATALOG, "contradicted"),
    ]
    res_t5 = proto.evaluate(paths_t5)
    if res_t5.verdict == TriangulationVerdict.CONTRADICTED:
        tests.append({
            "id": "T5_one_contradicted",
            "expected": "CONTRADICTED (substrate finding logged)",
            "actual": f"verdict={res_t5.verdict.name}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T5_one_contradicted",
            "expected": "CONTRADICTED",
            "actual": f"verdict={res_t5.verdict.name}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "contradiction must short-circuit; substrate ignored it",
        })

    verdict_counts = Counter(t["verdict"] for t in tests)
    return {
        "lane": "3_correlated_triangulation",
        "n_tests": len(tests),
        "verdict_counts": dict(verdict_counts),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 6 — undecidable-canonicalization
# ---------------------------------------------------------------------------


def lane_6_undecidable_canonicalization() -> dict:
    """4 tests on CanonicalizationProtocol's decidability flag."""
    from sigma_kernel.coordinate_chart import (
        CanonicalizationProtocol,
        CoordinateChart,
        get_chart,
    )
    from sigma_kernel import coordinate_charts  # registers default charts

    tests = []

    # Test 1: undecidable canonicalization protocol can be constructed
    # (substrate must accept the flag for documented-undecidable cases)
    try:
        cp_undec = CanonicalizationProtocol(
            impl="novikov_word_problem",
            decidability_status="undecidable",
            choice_dependencies=("relator_set",),
            version="1.0.0",
            canonicalize=None,  # registry-only; no impl bound
        )
        tests.append({
            "id": "T1_construct_undecidable_protocol",
            "expected": "CanonicalizationProtocol constructed; decidability_status=='undecidable'",
            "actual": f"impl={cp_undec.impl}, decidability_status={cp_undec.decidability_status}",
            "verdict": "PASS" if cp_undec.decidability_status == "undecidable" else "FAIL",
            "severity": None if cp_undec.decidability_status == "undecidable" else "P0-blocker",
        })
    except Exception as exc:
        tests.append({
            "id": "T1_construct_undecidable_protocol",
            "expected": "CanonicalizationProtocol(decidability_status='undecidable') accepted",
            "actual": f"raised {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "substrate refuses to record undecidability",
        })

    # Test 2: invalid decidability_status raises
    try:
        bad = CanonicalizationProtocol(
            impl="x",
            decidability_status="maybe",  # type: ignore -- ill-formed
            choice_dependencies=(),
            version="1.0.0",
        )
        tests.append({
            "id": "T2_invalid_decidability_status",
            "expected": "ValueError raised",
            "actual": "silently accepted invalid status",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except ValueError as exc:
        tests.append({
            "id": "T2_invalid_decidability_status",
            "expected": "ValueError raised",
            "actual": f"ValueError: {str(exc)[:100]}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        tests.append({
            "id": "T2_invalid_decidability_status",
            "expected": "ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # Test 3: undecidable canonicalize() without impl raises NotImplementedError
    try:
        cp = CanonicalizationProtocol(
            impl="drozd_wild_quiver",
            decidability_status="undecidable",
            choice_dependencies=(),
            version="1.0.0",
            canonicalize=None,
        )
        result = cp.apply({"some": "input"})
        tests.append({
            "id": "T3_apply_undecidable_no_impl",
            "expected": "NotImplementedError raised",
            "actual": f"silently produced {result!r}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except NotImplementedError as exc:
        tests.append({
            "id": "T3_apply_undecidable_no_impl",
            "expected": "NotImplementedError raised",
            "actual": f"NotImplementedError: {str(exc)[:120]}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        tests.append({
            "id": "T3_apply_undecidable_no_impl",
            "expected": "NotImplementedError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # Test 4: registered Lehmer chart's canonicalization has decidability_status set
    try:
        lehmer_chart = get_chart("lehmer:deg14:pm5:palindromic")
        if lehmer_chart is None:
            tests.append({
                "id": "T4_lehmer_chart_decidability",
                "expected": "Lehmer chart registered with decidability_status",
                "actual": "chart not in registry",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
        else:
            cp = lehmer_chart.canonicalization
            ds = cp.decidability_status
            tests.append({
                "id": "T4_lehmer_chart_decidability",
                "expected": "decidability_status set (decidable / undecidable / conditional)",
                "actual": f"impl={cp.impl}, decidability_status={ds}",
                "verdict": "PASS" if ds in ("decidable", "undecidable", "conditional") else "FAIL",
                "severity": None,
            })
    except Exception as exc:
        tests.append({
            "id": "T4_lehmer_chart_decidability",
            "expected": "lehmer chart accessible with decidability_status",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })

    verdict_counts = Counter(t["verdict"] for t in tests)
    return {
        "lane": "6_undecidable_canonicalization",
        "n_tests": len(tests),
        "verdict_counts": dict(verdict_counts),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #4 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 3: correlated-triangulation ---")
    lane3 = lane_3_correlated_triangulation()
    print(f"Tests: {lane3['n_tests']}, verdicts: {lane3['verdict_counts']}")
    for t in lane3["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 6: undecidable-canonicalization ---")
    lane6 = lane_6_undecidable_canonicalization()
    print(f"Tests: {lane6['n_tests']}, verdicts: {lane6['verdict_counts']}")
    for t in lane6["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_4_2026_05_06",
        "lanes": ["3_correlated_triangulation", "6_undecidable_canonicalization"],
        "lane_3": lane3,
        "lane_6": lane6,
    }
    out_path = out_dir / "substrate_tester_fire_4_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
