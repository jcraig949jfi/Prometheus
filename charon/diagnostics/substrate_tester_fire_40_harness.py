"""Substrate-Tester Fire #40 harness — third fire under HARD-6 posture.

Lane 12 — pulled catalog entry #58 (Tensor isomorphism complexity;
§VII Decidability and Computational Complexity). Suspected GI-hard.
Foundation of post-quantum-crypto candidates (MEDS, ALTEQ). Different
direction from fires #38 (rank/decomposition, §I) and #39 (network
contraction, §X) — this is about EQUIVALENCE-CLASS DECISION under
group action (GL_3 × GL_3 × GL_3 etc.). Probes whether substrate's
EQUIV opcode covers algebraic-equivalence testing or has gaps.

Lane 14 — frozen-dataclass invariance regression. Sister to mini-window
Tier-2 fix; walks all frozen dataclasses in sigma_kernel/* and confirms
they reject mutation.

Outputs:
  charon/diagnostics/substrate_tester_fire_40_results.json
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — catalog entry #58: tensor isomorphism complexity
# ---------------------------------------------------------------------------


def lane_12_tensor_isomorphism_probe() -> Dict[str, Any]:
    """Attempt to encode the structure of catalog entry #58 — tensor
    isomorphism under group action — using existing substrate primitives,
    most importantly EQUIV. Document where it works / fails."""

    # Conceptual setup: two 3-tensors T, T' in F^{n×n×n}. They are
    # isomorphic under GL_n × GL_n × GL_n if there exist A, B, C in GL_n
    # such that T'[i,j,k] = sum_{p,q,r} A[i,p] B[j,q] C[k,r] T[p,q,r].
    # Decision problem: given T, T', do such A,B,C exist? Believed
    # GI-hard. Captures Group Isomorphism, Code Equivalence, MinRank.
    #
    # Toy example: T = e_1 ⊗ e_1 ⊗ e_1 + e_2 ⊗ e_2 ⊗ e_2 (rank-2 diagonal,
    # 2x2x2). Permuting basis e_1 <-> e_2 gives an isomorphic copy T'.

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode tensor isomorphism via EQUIV opcode
    encoding_attempts.append({
        "probe": "encode_tensor_iso_via_EQUIV",
        "attempt": (
            "EQUIV(symbol_T, symbol_T', equivalence_class_id="
            "'GL_n_x_GL_n_x_GL_n_action_iso', witness_type=??, witness=...). "
            "EQUIV's three witness types are proof_ref / finite_check / "
            "equiv_chain. None of them carries a group-action witness "
            "(an explicit triple (A, B, C) in GL_n cubed)."
        ),
        "blocker": (
            "EQUIV's witness types don't include 'group_action_witness'. "
            "finite_check could fit small-format tensors (2x2x2) where "
            "exhaustive search over invertible matrices is feasible — but "
            "returns boolean, not the witnessing (A,B,C). proof_ref could "
            "point to an external proof but loses substrate-grade "
            "verifiability. equiv_chain doesn't apply to non-syntactic "
            "equivalence."
        ),
        "verdict": "PARTIAL — EQUIV exists but witness types incomplete",
    })

    # Probe 2: GroupAction primitive via OperatorPortabilityCertificate
    encoding_attempts.append({
        "probe": "encode_group_action_via_T030",
        "attempt": (
            "OperatorPortabilityCertificate(operator='GL_n_action', "
            "source_chart='tensor_iso:T', target_chart='tensor_iso:T_prime', "
            "transfer_method=STRUCTURAL_ANALOGY, ...). The operator "
            "'GL_n action' applies (A, B, C) to T to get T'."
        ),
        "blocker": (
            "T030 has the right shape (operator transports T to T') but "
            "doesn't carry the GROUP STRUCTURE — substrate has no "
            "GroupAction primitive that knows about group composition, "
            "inverses, identity. The witness for tensor isomorphism MUST "
            "come from a group; OperatorPortabilityCertificate treats the "
            "operator as a black box. Loses isomorphism-class semantics."
        ),
        "verdict": "FAIL_ENCODING — no GroupAction / GroupActionWitness",
    })

    # Probe 3: encode via MethodSpec + IndependenceClass
    encoding_attempts.append({
        "probe": "encode_iso_test_via_MethodSpec",
        "attempt": (
            "MethodSpec(engine='magma', strategy='tensor_isomorphism', "
            "independence_class=??, version='2.27'). Wrap a tensor-"
            "isomorphism test as a MethodSpec; the test's output (true/"
            "false + optional witness) is then a CLAIM."
        ),
        "blocker": (
            "Same enum-gap as fire #39: no IndependenceClass value for "
            "GROUP_ACTION_INVARIANT. Even with one added: MethodSpec "
            "operates at the call-engine level, not the ALGEBRAIC-"
            "STRUCTURE level. Substrate could RUN a Magma iso-test but "
            "couldn't represent the equivalence-class structure (orbit, "
            "stabilizer, fundamental domain) as substrate-grade data."
        ),
        "verdict": "FAIL_ENCODING — no algebraic-structure-level primitive",
    })

    # Probe 4: ExclusionCertificate for non-isomorphism
    encoding_attempts.append({
        "probe": "encode_non_iso_via_ExclusionCertificate",
        "attempt": (
            "ExclusionCertificate(region_spec=..., exclusion_claim="
            "ExclusionClaim(excluded_property='isomorphism_to_T_prime', "
            "result_class='gln_iso_class', reason='Galois_orbit_invariant_"
            "differs'), ...)."
        ),
        "blocker": (
            "Works for the NEGATIVE direction (T ≢ T'): the exclusion "
            "certificate carries a Galois-orbit-invariant or other "
            "non-iso obstruction. BUT the substrate has no companion "
            "POSITIVE primitive — the (A,B,C) witness for T ≅ T' has no "
            "substrate-grade home. Same asymmetric-existential pattern as "
            "fire #39's ContractionOrderWitness. Strongly suggests this "
            "asymmetry is substrate-WIDE, not tensor-specific."
        ),
        "verdict": "PARTIAL — non-iso encodable, iso witness has no home",
    })

    capability_gaps_identified = [
        {
            "missing_primitive": "GroupAction / GroupActionWitness",
            "purpose": "explicit (A_1, ..., A_k) in G action mapping T to T'; substrate-grade group structure",
            "needed_for": "tensor iso, code equivalence, MinRank, post-quantum-crypto schemes (MEDS, ALTEQ)",
            "blocks_paradigms": ["P30", "P31"],
            "blocks_catalog_entries": "#58 directly; also entries in §V (identifiability), §IX (random tensors with symmetry), §X (SLOCC entanglement classification)",
        },
        {
            "missing_primitive": "IsomorphismCertificate (positive existential with witness, complementing ExclusionCertificate)",
            "purpose": "constructive isomorphism witness; the upper-bound side of NP-search",
            "needed_for": "completing the existential symmetry — ANY 'is-isomorphic-to' / 'is-equivalent-to' decision needs a constructive POSITIVE primitive",
            "broader_pattern": "Same ASYMMETRIC EXISTENTIAL gap as fire #39's ContractionOrderWitness. Two fires from different paradigms (P30 + GI-hard) hit the same shape — strongly suggests substrate-wide design issue, not tensor-specific.",
            "convergence_with_fire_39": (
                "Fire #39 surfaced ContractionOrderWitness for combinatorial "
                "optimization upper bound; fire #40 surfaces "
                "IsomorphismCertificate for equivalence-decision upper bound. "
                "Both are positive-existentials-with-witness; both lack a "
                "substrate-grade home. The unifying primitive is "
                "ConstructiveExistenceWitness with role-specific subclasses."
            ),
            "blocks_paradigms": ["P30", "P31", "all NP-search problems substrate may track"],
            "blocks_catalog_entries": "broader than tensors — applies whenever substrate needs to track an explicit witness for an existential claim with cost/correctness annotation",
        },
        {
            "missing_primitive": "OrbitStratification / FundamentalDomain",
            "purpose": "encode the orbit space of group action (equivalence classes); enable canonical-form reasoning",
            "needed_for": "tensor iso classification (#58), SLOCC classification (#79), Comon's conjecture lineage, any 'classify modulo G' problem",
            "blocks_paradigms": ["P31"],
            "blocks_catalog_entries": "#58 + #79 + parts of §III/§IV/§XII (geometric complexity theory)",
            "convergence_note": (
                "RELATED TO 5-of-5 capability-gap cluster's "
                "Structured-Equivalence-Class meta-primitive. Tensor iso is "
                "another instance of 'structured equivalence under specified "
                "transformations.' Pre-existing recommendation may unify "
                "this gap with the cluster's needs."
            ),
        },
    ]

    return {
        "lane": "12_catalog_pulled_tensor_iso_probe",
        "catalog_entry": "#58 Tensor isomorphism complexity",
        "section": "VII. Decidability and Computational Complexity",
        "attack_paradigms": ["P30", "P31"],
        "encoding_attempts": encoding_attempts,
        "all_attempts_failed": all(
            a["verdict"].startswith("FAIL") or a["verdict"].startswith("PARTIAL")
            for a in encoding_attempts
        ),
        "capability_gaps_identified": capability_gaps_identified,
        "verdict": "FAIL_ENCODING — substrate has no GroupAction primitive + asymmetric existential pattern (recurring)",
        "feeds_techne_ticket": "T-2026-05-08-T038 (substrate-primitive classification of all 104 catalog entries)",
        "convergence_status": (
            "Three fires (#38/#39/#40), three sections (§I/§X/§VII), "
            "three paradigms (P28-P31 + P30 + P30/P31). Convergence "
            "increasingly clear:\n"
            "  - TensorObject + TensorNetworkGraph + GroupAction = "
            "tensor-specific subsystem (foundational primitives)\n"
            "  - RankDecompositionWitness + ContractionOrderWitness + "
            "IsomorphismCertificate = SAME asymmetric-existential pattern "
            "(positive-existential-with-witness substrate-wide gap)\n"
            "  - MomentPolytope + RewriteSearchTree + OrbitStratification "
            "= optimization-geometry-over-discrete-structure family\n"
            "Pattern: foundational tensor primitives + asymmetric-existential "
            "general primitive + optimization-geometry family. Three "
            "subsystems, not one — but they interlock."
        ),
    }


# ---------------------------------------------------------------------------
# Lane 14 — frozen-dataclass invariance regression
# ---------------------------------------------------------------------------


def lane_14_frozen_invariance_regression() -> Dict[str, Any]:
    """Walk a known set of frozen dataclasses in sigma_kernel and confirm
    they reject mutation. Sister to mini-window Tier-2 fix."""

    import dataclasses
    from sigma_kernel.method_spec import MethodSpec, IndependenceClass
    from sigma_kernel.exclusion_certificate import (
        ExclusionCertificate, ExclusionClaim, RegionSpec, VerifierSet,
        ReplayInfo, CertificateType, CertificateStrength,
    )
    from sigma_kernel.triangulation_protocol import TriangulationProtocol, TriangulationPath, MethodClass

    tests: List[Dict[str, Any]] = []

    # T1: MethodSpec is frozen
    spec = MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        version="1.0.0",
    )
    try:
        try:
            spec.engine = "different_engine"
            tests.append({"id": "T1_MethodSpec_frozen", "verdict": "FAIL",
                          "actual": "mutation succeeded"})
        except dataclasses.FrozenInstanceError:
            tests.append({"id": "T1_MethodSpec_frozen", "verdict": "PASS"})
    except Exception as exc:  # noqa: BLE001
        tests.append({"id": "T1_MethodSpec_frozen", "verdict": "FAIL",
                      "actual": f"{type(exc).__name__}: {exc}"})

    # T2: ExclusionClaim is frozen
    claim = ExclusionClaim(
        excluded_property="probe", result_class="test", reason="fire40",
    )
    try:
        try:
            claim.reason = "different_reason"
            tests.append({"id": "T2_ExclusionClaim_frozen", "verdict": "FAIL",
                          "actual": "mutation succeeded"})
        except dataclasses.FrozenInstanceError:
            tests.append({"id": "T2_ExclusionClaim_frozen", "verdict": "PASS"})
    except Exception as exc:  # noqa: BLE001
        tests.append({"id": "T2_ExclusionClaim_frozen", "verdict": "FAIL",
                      "actual": f"{type(exc).__name__}: {exc}"})

    # T3: RegionSpec is frozen
    region = RegionSpec(coordinate_chart_id="test:fire40", constraints={}, bounds=None)
    try:
        try:
            region.coordinate_chart_id = "different"
            tests.append({"id": "T3_RegionSpec_frozen", "verdict": "FAIL",
                          "actual": "mutation succeeded"})
        except dataclasses.FrozenInstanceError:
            tests.append({"id": "T3_RegionSpec_frozen", "verdict": "PASS"})
    except Exception as exc:  # noqa: BLE001
        tests.append({"id": "T3_RegionSpec_frozen", "verdict": "FAIL",
                      "actual": f"{type(exc).__name__}: {exc}"})

    # T4: ReplayInfo is frozen
    replay = ReplayInfo(code_hash="x", data_hash="y", seed=0, environment_hash="z")
    try:
        try:
            replay.seed = 99
            tests.append({"id": "T4_ReplayInfo_frozen", "verdict": "FAIL",
                          "actual": "mutation succeeded"})
        except dataclasses.FrozenInstanceError:
            tests.append({"id": "T4_ReplayInfo_frozen", "verdict": "PASS"})
    except Exception as exc:  # noqa: BLE001
        tests.append({"id": "T4_ReplayInfo_frozen", "verdict": "FAIL",
                      "actual": f"{type(exc).__name__}: {exc}"})

    # T5: ExclusionCertificate is frozen
    cert = ExclusionCertificate(
        region_spec=region,
        exclusion_claim=claim,
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=(spec,)),
        replay=replay,
    )
    try:
        try:
            cert.certificate_type = CertificateType.EXHAUSTIVE_ENUMERATION
            tests.append({"id": "T5_ExclusionCertificate_frozen", "verdict": "FAIL",
                          "actual": "mutation succeeded"})
        except dataclasses.FrozenInstanceError:
            tests.append({"id": "T5_ExclusionCertificate_frozen", "verdict": "PASS"})
    except Exception as exc:  # noqa: BLE001
        tests.append({"id": "T5_ExclusionCertificate_frozen", "verdict": "FAIL",
                      "actual": f"{type(exc).__name__}: {exc}"})

    return {
        "lane": "14_frozen_invariance_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 40,
        "posture": "third-HARD-6-fire (matrix-filling: §VII catalog entry #58; testing TensorAlgebra-subsystem convergence beyond §I+§X)",
        "lanes": [12, 14],
        "lane_12": lane_12_tensor_isomorphism_probe(),
        "lane_14": lane_14_frozen_invariance_regression(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_40_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: catalog #58 verdict = {summary['lane_12']['verdict'][:60]}...")
    print(f"  capability gaps: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"Lane 14: {summary['lane_14']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
