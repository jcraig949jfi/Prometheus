"""Substrate-Tester Fire #21 harness — Lane 12 (representation-pressure
with NOVEL objects) + Lane 6 (undecidable-canonicalization regression).

Coordination: parallel fire #20 (commit 0f399394) covered Lane 5 deg-10
±5 (PASS, 0 tickets, hit-rate scaling pattern documented). My fire = #21.
P0 ticket T-ST-fire17-001 still OPEN — Techne hasn't shipped fix;
deferred re-probe.

Lane 12 novel-object selection: avoid duplicating existing tickets
ST-fire1-002 (homotopy class) and ST-fire1-003 (Fano plane / combinatorial
design); also avoid T024-T028 design set (tropical curve, p-adic
L-function, Galois cohomology, large-cardinal consistency, motivic
period). Picks two genuinely uncovered object classes:
  - Knot invariant (HOMFLY polynomial) — classical, concrete, well-defined
  - A∞-algebra (concrete: dg-algebra of singular cochains) — homotopy-
    coherent algebraic structure with arity-graded operations

Lane 6: regression check that decidability-flag discipline still holds
across the contract-change window + post-restart fires.

Outputs:
  charon/diagnostics/substrate_tester_fire_21_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — representation-pressure with NOVEL objects
# ---------------------------------------------------------------------------


def lane_12_homfly_polynomial() -> Dict[str, Any]:
    """Probe: encode the HOMFLY polynomial of a specific knot (the trefoil,
    3_1 in Rolfsen notation) as a substrate object."""
    encoding_attempts: List[str] = []
    encoding_works = False
    encoding_notes: List[str] = []

    # Probe target: trefoil knot 3_1's HOMFLY polynomial
    # P(3_1)(a, z) = -a^4 + a^2*z^2 + 2*a^2 (Rolfsen sign)
    # Two-variable Laurent polynomial in a (variable from skein relation)
    # and z = q - q^{-1} (Conway-style).

    # CoordinateChart attempt
    encoding_attempts.append(
        "CoordinateChart: would need (a, z) Laurent-polynomial coordinates with "
        "a metric over the polynomial ring. No registered chart for "
        "knot_invariants:HOMFLY exists. CoordinateChart's metric is over "
        "scalar-coordinate points, not polynomial-ring elements."
    )

    # KillVector attempt
    encoding_attempts.append(
        "KillVector: N/A (not a falsifier outcome)."
    )

    # OperatorOutputSequence (T023) attempt
    encoding_attempts.append(
        "OperatorOutputSequence (T023): partial — could encode the "
        "(a, z) -> P(a, z) as an output sequence indexed by (a, z) lattice "
        "points. But the natural identity is a SYMBOLIC LAURENT POLYNOMIAL, "
        "not a sequence of evaluated values. The sequence loses the symbolic "
        "structure that makes HOMFLY recognizable up to isotopy."
    )

    # ExclusionCertificate attempt
    encoding_attempts.append(
        "ExclusionCertificate: N/A (not an exclusion claim)."
    )

    # REWRITE/EQUIV attempt: skein relation as a REWRITE
    encoding_attempts.append(
        "REWRITE: skein relation a*P(L_+) - a^{-1}*P(L_-) = z*P(L_0) is "
        "structurally a rewrite rule from one knot's HOMFLY to its neighbors'. "
        "Could be encoded as REWRITE Symbol from L_+ to L_- via "
        "rewrite_rule_id='homfly_skein_relation'. BUT: substrate's REWRITE "
        "primitive expects scalar-valued Symbols, not polynomials in a, z."
    )

    # Verdict
    encoding_notes.append(
        "Knot HOMFLY polynomials are SYMBOLIC objects in a 2-variable "
        "Laurent polynomial ring. The substrate has no native primitive for "
        "symbolic-polynomial-valued objects with structural recognition (skein "
        "equivalence, isotopy invariance). T023 OperatorOutputSequence captures "
        "evaluations but loses symbolic identity."
    )

    return {
        "probe": "knot_invariant_HOMFLY_polynomial_trefoil_3_1",
        "encoded_cleanly": encoding_works,
        "encoding_attempts": encoding_attempts,
        "missing_primitive": (
            "SymbolicLaurentPolynomial primitive that natively carries "
            "(variable_set: tuple[str, ...], laurent_terms: dict[tuple[int, ...], "
            "Coefficient]) with skein-equivalence + isotopy-invariance "
            "registered as canonicalization protocols."
        ),
        "verdict_notes": encoding_notes,
    }


def lane_12_a_infinity_algebra() -> Dict[str, Any]:
    """Probe: encode the dg-algebra of singular cochains C*(S^2; Z) on the
    2-sphere as a substrate object (concrete A∞-algebra)."""
    encoding_attempts: List[str] = []
    encoding_works = False
    encoding_notes: List[str] = []

    # Probe target: dg-algebra C*(S^2; Z). Has cohomology Z[u]/(u^2) with deg(u)=2.
    # As an A∞-algebra: m_2 (cup product) is the only nonzero higher operation
    # because S^2 is formal. So this is effectively a CDGA, but registering
    # higher m_n=0 is part of the A∞ structure.

    # CoordinateChart attempt
    encoding_attempts.append(
        "CoordinateChart: A∞-algebra has graded vector space + tower of "
        "operations m_n: A^{⊗n} -> A. No registered chart captures this; "
        "CoordinateChart's coordinate_system is a tuple of scalar axes, "
        "not a graded vector space + operad action."
    )

    # KillVector attempt
    encoding_attempts.append(
        "KillVector: N/A (not a falsifier outcome)."
    )

    # OperatorOutputSequence (T023) attempt
    encoding_attempts.append(
        "OperatorOutputSequence (T023): could encode each m_n as a "
        "separate sequence (operator_id='m_n', index=n-tuple of basis elements). "
        "But: requires registering INFINITE many operator_ids (m_2, m_3, m_4, ...) "
        "because A∞ has unbounded arity. Substrate has no notion of "
        "arity-graded operator family."
    )

    # REWRITE/EQUIV attempt
    encoding_attempts.append(
        "REWRITE/EQUIV: A∞-morphisms include higher coherences (the L∞ "
        "structure). REWRITE only captures binary src->tgt; cannot express "
        "the arity-graded family of (f_1, f_2, f_3, ...) maps that "
        "constitute an A∞-morphism."
    )

    encoding_notes.append(
        "A∞-algebras require an ARITY-GRADED OPERATION FAMILY primitive. "
        "Substrate has no such primitive. Related to the homotopy-class "
        "capability gap from fire #7 (ST-fire1-002) — both want "
        "higher-categorical structure."
    )

    return {
        "probe": "A_infinity_algebra_singular_cochains_S2",
        "encoded_cleanly": encoding_works,
        "encoding_attempts": encoding_attempts,
        "missing_primitive": (
            "ArityGradedOperationFamily primitive: a registered tower of "
            "operations indexed by arity n with type-checked composition + "
            "Stasheff associativity coherence relations. Likely a substantial "
            "contract-change."
        ),
        "verdict_notes": encoding_notes,
        "related_to_existing_ticket": "ST-fire1-002 (homotopy class) — both want higher-categorical structure",
    }


def lane_12_novel_objects() -> Dict[str, Any]:
    homfly = lane_12_homfly_polynomial()
    a_inf = lane_12_a_infinity_algebra()
    n_gaps = sum(1 for r in (homfly, a_inf) if not r["encoded_cleanly"])
    return {
        "lane": "12_representation_pressure_novel_objects",
        "n_probes": 2,
        "n_capability_gaps": n_gaps,
        "probes": [homfly, a_inf],
    }


# ---------------------------------------------------------------------------
# Lane 6 — undecidable-canonicalization regression
# ---------------------------------------------------------------------------


def lane_6_regression() -> Dict[str, Any]:
    from sigma_kernel.coordinate_chart import (
        CanonicalizationProtocol,
        VALID_DECIDABILITY,
        all_charts,
    )
    import sigma_kernel.coordinate_charts  # noqa: F401

    tests: List[Dict[str, Any]] = []

    # T1: VALID_DECIDABILITY tuple unchanged
    expected = {"decidable", "undecidable", "conditional"}
    actual = set(VALID_DECIDABILITY)
    if actual == expected:
        tests.append({
            "id": "T1_valid_decidability_unchanged",
            "expected": str(sorted(expected)),
            "actual": str(sorted(actual)),
            "verdict": "PASS",
        })
    else:
        tests.append({
            "id": "T1_valid_decidability_unchanged",
            "expected": str(sorted(expected)),
            "actual": str(sorted(actual)),
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "VALID_DECIDABILITY contract changed since fire #11 baseline",
        })

    # T2: invalid decidability_status raises
    try:
        _ = CanonicalizationProtocol(
            impl="bogus_fire21",
            decidability_status="not_a_valid_status",
            choice_dependencies=(),
            version="1.0.0",
        )
        tests.append({
            "id": "T2_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": "silently constructed",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
    except ValueError as exc:
        tests.append({
            "id": "T2_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": f"ValueError: {str(exc)[:140]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T2_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": f"raised wrong type: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T3: undecidable construction succeeds
    try:
        proto = CanonicalizationProtocol(
            impl="word_problem_for_finitely_presented_groups",
            decidability_status="undecidable",
            choice_dependencies=("normal_form_choice",),
            version="1.0.0",
        )
        tests.append({
            "id": "T3_undecidable_construction",
            "expected": "construction succeeds",
            "actual": f"impl={proto.impl!r}, decidability={proto.decidability_status!r}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_undecidable_construction",
            "expected": "construction succeeds",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T4: registered Lehmer chart is decidable
    try:
        charts = all_charts()
        lehmer = next((c for c in charts if c.domain == "lehmer"), None)
        if lehmer is None:
            tests.append({
                "id": "T4_lehmer_chart_decidable",
                "expected": "Lehmer chart present",
                "actual": "no Lehmer chart in registry",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        elif lehmer.canonicalization.decidability_status == "decidable":
            tests.append({
                "id": "T4_lehmer_chart_decidable",
                "expected": "decidable",
                "actual": (
                    f"impl={lehmer.canonicalization.impl!r}, "
                    f"decidability={lehmer.canonicalization.decidability_status!r}"
                ),
                "verdict": "PASS",
            })
        else:
            tests.append({
                "id": "T4_lehmer_chart_decidable",
                "expected": "decidable",
                "actual": f"decidability_status={lehmer.canonicalization.decidability_status!r}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_lehmer_chart_decidable",
            "expected": "Lehmer chart accessible",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    return {
        "lane": "6_undecidable_canonicalization_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 21,
        "lanes": [12, 6],
        "lane_12": lane_12_novel_objects(),
        "lane_6": lane_6_regression(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_21_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: {summary['lane_12']['n_capability_gaps']}/2 capability gaps")
    print(f"Lane 6: {summary['lane_6']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
