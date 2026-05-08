"""Substrate-Tester Fire #35 harness — Lane 8 (TriangulationPathRef
indirect frozen-ness probe via ExclusionCertificate) + Lane 12 (5th
novel object: representation of S_3).

Coordination: my fire #34 was last; no new parallel.

Lane 8: T-ST-fire33-001 P3 reports that TriangulationPathRef's
frozen-ness is NOT caught by the audit because the synthesizer can't
auto-construct it (requires nested MethodSpec). This fire probes
whether the frozen-ness is caught INDIRECTLY when TriangulationPathRef
is wrapped inside ExclusionCertificate's triangulation_history. If
mutating a ref through the parent's field still raises
FrozenInstanceError, the indirect coverage IS sufficient and
ST-fire33-001 might be downgrade-able to documentation-only.

Lane 12: 5th novel capability-gap probe — finite-group representation
(specifically S_3 with its 3 irreducible representations: trivial, sign,
2-dim standard). Avoids overlap with existing capability-gap tickets
(T024-T028 + ST-fire1-002/003 + ST-fire21-001/002).

Outputs:
  charon/diagnostics/substrate_tester_fire_35_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 8 — TriangulationPathRef indirect frozen-ness probe
# ---------------------------------------------------------------------------


def lane_8_indirect_frozen_probe() -> Dict[str, Any]:
    """Construct an ExclusionCertificate with a real TriangulationPathRef
    in triangulation_history. Then attempt to mutate the ref through the
    parent's field. If FrozenInstanceError raises, indirect coverage
    holds. If silent mutation succeeds, ST-fire33-001 holds — the audit
    needs explicit per-class coverage."""
    import dataclasses

    from sigma_kernel.exclusion_certificate import (
        Boundary, CertificateStrength, CertificateType,
        ExclusionCertificate, ExclusionClaim, RegionSpec,
        ReplayInfo, TriangulationPathRef, VerifierSet,
    )
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec

    tests: List[Dict[str, Any]] = []

    spec = MethodSpec(
        engine="sympy", strategy="factor_list",
        independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        version="1.0.0",
    )

    # Construct a real TriangulationPathRef
    ref = TriangulationPathRef(
        path_id="path_test",
        method_spec=spec,
        verdict="verified",
        timestamp=time.time(),
        summary="test ref",
    )

    # T1: directly mutating the ref raises FrozenInstanceError
    try:
        ref.path_id = "mutated"  # type: ignore
        tests.append({
            "id": "T1_direct_setattr_on_ref",
            "expected": "FrozenInstanceError",
            "actual": f"silently accepted: ref.path_id={ref.path_id!r}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "TriangulationPathRef NOT actually frozen — substrate-grade flaw",
        })
    except dataclasses.FrozenInstanceError:
        tests.append({
            "id": "T1_direct_setattr_on_ref",
            "expected": "FrozenInstanceError",
            "actual": "FrozenInstanceError raised on direct setattr",
            "verdict": "PASS",
            "note": "TriangulationPathRef IS actually frozen (just not auto-enrolled in audit)",
        })
    except (AttributeError, TypeError) as exc:
        tests.append({
            "id": "T1_direct_setattr_on_ref",
            "expected": "FrozenInstanceError",
            "actual": f"raised {type(exc).__name__}: {str(exc)[:120]}",
            "verdict": "PASS",
            "note": "frozen-equivalent rejection (older Python style)",
        })

    # T2: construct ExclusionCertificate with ref in triangulation_history
    cert_spec = MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        version="1.0.0",
    )
    cert = ExclusionCertificate(
        region_spec=RegionSpec(coordinate_chart_id="test:scope", constraints={}, bounds=None),
        exclusion_claim=ExclusionClaim(
            excluded_property="probe", result_class="test", reason="probe",
        ),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.COMPLETE,  # requires triangulation_history
        verifier_set=VerifierSet(methods=(cert_spec,)),
        replay=ReplayInfo(code_hash="x", data_hash="y", seed=0, environment_hash="z"),
        triangulation_history=(ref,),
    )

    # T3: mutating the parent's triangulation_history tuple
    try:
        cert.triangulation_history = ()  # type: ignore
        tests.append({
            "id": "T3_parent_field_mutation",
            "expected": "FrozenInstanceError",
            "actual": f"silently accepted; cert.triangulation_history={cert.triangulation_history!r}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except dataclasses.FrozenInstanceError:
        tests.append({
            "id": "T3_parent_field_mutation",
            "expected": "FrozenInstanceError",
            "actual": "FrozenInstanceError raised on parent setattr",
            "verdict": "PASS",
        })
    except (AttributeError, TypeError) as exc:
        tests.append({
            "id": "T3_parent_field_mutation",
            "expected": "FrozenInstanceError",
            "actual": f"raised {type(exc).__name__}",
            "verdict": "PASS",
            "note": "frozen-equivalent rejection",
        })

    # T4: mutating the inner ref via cert.triangulation_history[0]
    try:
        cert.triangulation_history[0].path_id = "smuggled"  # type: ignore
        tests.append({
            "id": "T4_inner_ref_mutation_through_parent",
            "expected": "FrozenInstanceError",
            "actual": f"silently accepted; ref.path_id={cert.triangulation_history[0].path_id!r}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "ref mutation via parent index NOT caught — need explicit per-class test",
        })
    except dataclasses.FrozenInstanceError:
        tests.append({
            "id": "T4_inner_ref_mutation_through_parent",
            "expected": "FrozenInstanceError",
            "actual": "FrozenInstanceError raised on inner ref via parent",
            "verdict": "PASS",
            "note": "indirect coverage HOLDS — ST-fire33-001 may be downgrade-candidate",
        })
    except (AttributeError, TypeError) as exc:
        tests.append({
            "id": "T4_inner_ref_mutation_through_parent",
            "expected": "FrozenInstanceError",
            "actual": f"raised {type(exc).__name__}: {str(exc)[:120]}",
            "verdict": "PASS",
            "note": "frozen-equivalent rejection",
        })

    return {
        "lane": "8_triangulation_path_ref_indirect_frozen_probe",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 12 — 5th novel capability-gap probe (S_3 representation)
# ---------------------------------------------------------------------------


def lane_12_s3_representation() -> Dict[str, Any]:
    """Probe: encode an irreducible representation of S_3 (symmetric
    group on 3 letters) as a substrate object. S_3 has 3 irreducibles:
    trivial (1-dim, every g→1), sign (1-dim, even→+1, odd→−1), and
    2-dim standard. The data: a group homomorphism G → GL(V) for each
    irrep."""
    encoding_attempts: List[str] = []
    encoding_works = False
    encoding_notes: List[str] = []

    # The 2-dim standard rep of S_3:
    #   (1 2)  →  [[-1, 1], [0, 1]]
    #   (1 2 3) → [[0, -1], [1, -1]]
    # Plus 6 group elements with their images.

    # CoordinateChart attempt
    encoding_attempts.append(
        "CoordinateChart: would need (group_element, matrix_image) "
        "coordinate pairs. No registered chart for "
        "rep_theory:finite_group:S_3 exists. CoordinateChart's metric "
        "is over scalar-coordinate points; matrix-valued outputs are "
        "structurally different. The natural identity is the homomorphism "
        "G → GL(V), not a point in some scalar space."
    )

    # OperatorOutputSequence (T023) attempt
    encoding_attempts.append(
        "OperatorOutputSequence (T023): could encode as "
        "operator='representation_image', index=group_element_index "
        "(0 to 5 for S_3), output=serialized_matrix_string. Stretches "
        "T023 — output_unit is not a meaningful scalar; the matrix "
        "structure (multiplicativity ρ(gh)=ρ(g)ρ(h)) is lost in the "
        "sequence shape."
    )

    # REWRITE/EQUIV attempt: equivalence of representations
    encoding_attempts.append(
        "REWRITE/EQUIV: two representations are equivalent iff there's "
        "an intertwining isomorphism. EQUIV(rep_A, rep_B, "
        "equivalence_class_id='intertwining_isomorphism', "
        "witness=intertwining_matrix) is conceptually right but the "
        "witness shape (a non-scalar matrix M satisfying M·ρ_A(g)=ρ_B(g)·M "
        "for all g) doesn't match the 3 substrate witness types "
        "(proof_ref, finite_check, equiv_chain). 'finite_check' could "
        "stretch to encode the verification of the intertwining property "
        "for all 6 group elements, but loses the structural identity "
        "(M is what makes A and B equivalent, not just that they ARE)."
    )

    # KillVector / ExclusionCertificate: N/A (not falsifier outcomes)
    encoding_attempts.append(
        "KillVector / ExclusionCertificate: N/A (representations are "
        "not falsifier outcomes nor exclusion claims)."
    )

    encoding_notes.append(
        "Group representations require: (a) a finite group object as "
        "domain; (b) a vector space (or matrix algebra over a field) "
        "as codomain; (c) the homomorphism data; (d) intertwining "
        "morphisms as the canonical equivalence relation. Substrate "
        "has no GroupObject primitive, no MatrixOverField primitive, "
        "and the EQUIV witness-types don't capture matrix-valued "
        "intertwining data."
    )
    encoding_notes.append(
        "Pattern observed: this is the FIFTH lane-12 capability-gap "
        "where the substrate has NO native primitive for a structured "
        "object class with its own equivalence relation. Cumulative: "
        "ST-fire1-002 (homotopy), ST-fire1-003 (combinatorial design), "
        "ST-fire21-001 (HOMFLY/symbolic Laurent), ST-fire21-002 "
        "(A∞-algebra), and now ST-fire35 (group representation). The "
        "common theme: 'Structured Equivalence Class' meta-primitive "
        "is the unified design candidate for the next contract-change "
        "window (per Aporia recommendation cited in the mini-window "
        "summary)."
    )

    return {
        "probe": "finite_group_representation_S3_irreducible",
        "encoded_cleanly": encoding_works,
        "encoding_attempts": encoding_attempts,
        "missing_primitives": [
            "GroupObject (finite group with multiplication table or generators)",
            "MatrixOverField (typed matrix with coefficient field metadata)",
            "GroupHomomorphism / Representation (G → GL(V) data)",
        ],
        "verdict_notes": encoding_notes,
        "related_to_existing_tickets": [
            "ST-fire1-002 (homotopy class)", "ST-fire1-003 (combinatorial design)",
            "ST-fire21-001 (HOMFLY)", "ST-fire21-002 (A∞-algebra)",
        ],
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 35,
        "lanes": [8, 12],
        "lane_8": lane_8_indirect_frozen_probe(),
        "lane_12": lane_12_s3_representation(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_35_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 8: {summary['lane_8']['verdict_counts']}")
    print(f"Lane 12: encoded={summary['lane_12']['encoded_cleanly']}, "
          f"missing_primitives={len(summary['lane_12']['missing_primitives'])}")
    return summary


if __name__ == "__main__":
    run()
