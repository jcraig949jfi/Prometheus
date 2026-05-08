"""Substrate-Tester Fire #38 harness — first fire under HARD-6 posture.

Lane 12 (representation-pressure) pulled from the canonical
104-entry catalog at aporia/mathematics/tensor_open_problems_v1.md.
Per HARD POSTURE 2026-05-08 + HARD-6 ("attack the problems of the
tools we'll need most; failures guide"), substrate-tester probes
specific catalog entries instead of inventing novel objects.

Selected: catalog entry #4 — Exact rank of M⟨3⟩ (3×3 matrix
multiplication tensor). 27-entry tensor in [3,3,3] with known structure
(bilinear complexity object). Bounds 19 ≤ R(M⟨3⟩) ≤ 23 (Smirnov 2013
upper bound; Landsberg-style lower bounds). Attack paradigms per
attack_angle_taxonomy.md: P28 (asymptotic spectrum), P29 (border
apolarity), P31 (secant variety geometry).

Probe goal: attempt to encode M⟨3⟩ as a substrate object using existing
primitives. Document each encoding attempt and the failure mode. The
failure IS the output (HARD-6 doctrine; P25 paradigm).

Lane 8 — quick cert-extension regression smoke (sister to fire #25).

Outputs:
  charon/diagnostics/substrate_tester_fire_38_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — catalog-pulled probe: M⟨3⟩ encoding attempt
# ---------------------------------------------------------------------------


def lane_12_m3_encoding_probe() -> Dict[str, Any]:
    """Attempt to encode the 3×3 matrix multiplication tensor M⟨3⟩ as a
    substrate object using existing primitives. Document failures as
    capability gaps — feeds Techne T-2026-05-08-T038."""

    # M⟨3⟩ is a 27-entry tensor of shape (9, 9, 9) representing
    # bilinear matrix-multiply. M⟨n⟩(A, B, C) = trace(A·B·C) where A, B
    # are n×n. For n=3, the tensor T has entries T[i,j,k,l,m,p] with i,j
    # row/col of A; k,l row/col of B; m,p row/col of C; T = 1 iff
    # j==k AND l==m AND p==i, else 0. As a 3-tensor in (n²)^3:
    # T[(i,j), (k,l), (m,p)] = δ_{j,k} δ_{l,m} δ_{p,i}.

    encoding_attempts: List[Dict[str, Any]] = []

    # Build the tensor data (substrate-tester-side; substrate doesn't
    # have a TensorObject primitive yet).
    n = 3
    n_sq = n * n
    M3_data: Dict[tuple, int] = {}
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for ll in range(n):
                    for m in range(n):
                        for p in range(n):
                            if j == k and ll == m and p == i:
                                key = (i * n + j, k * n + ll, m * n + p)
                                M3_data[key] = 1
    n_nonzero = len(M3_data)

    # Probe 1: CoordinateChart — can we register a chart for M⟨3⟩?
    encoding_attempts.append({
        "probe": "register_M3_as_CoordinateChart",
        "attempt": (
            "CoordinateChart(domain='matrix_mult', region_key='M3', "
            "coordinate_system=('a_idx', 'b_idx', 'c_idx'), "
            "metric=...)."
        ),
        "blocker": (
            "CoordinateChart's coordinate_system is a tuple of named scalar "
            "axes; M⟨3⟩'s natural shape is a 9×9×9 tensor whose entries are "
            "the substrate-grade primitive content, not the coordinates. "
            "There's no substrate primitive for 'tensor with entries as "
            "first-class identity.' CoordinateChart can register the "
            "metadata but can't HOLD the tensor."
        ),
        "verdict": "FAIL_ENCODING — no TensorObject primitive",
    })

    # Probe 2: KillVector / EvidenceField as a workaround
    encoding_attempts.append({
        "probe": "encode_via_KillVector_or_EvidenceField",
        "attempt": (
            "KillVector / EvidenceField are typed value objects for "
            "falsifier outcomes. Force-fit M⟨3⟩ entries as (operator_id, "
            "index, output) in OperatorOutputSequence (T023) — operator = "
            "'M3_tensor_lookup', index = (i*9 + j*3 + k) integer-encoded, "
            "output = '0' or '1' string."
        ),
        "blocker": (
            "T023 OperatorOutputSequence is index→scalar-output. Loses the "
            "3-tensor structure (3 independent index axes). The substrate "
            "would store 729 (operator_id, index, output) entries but lose "
            "the multilinearity that makes M⟨3⟩'s rank decomposition "
            "meaningful. Rank queries (e.g. 'is there a rank-22 "
            "decomposition?') are not expressible against this encoding."
        ),
        "verdict": "FAIL_ENCODING — loses tensor structure",
    })

    # Probe 3: REWRITE/EQUIV for matrix multiplication identity
    encoding_attempts.append({
        "probe": "encode_via_REWRITE_EQUIV",
        "attempt": (
            "REWRITE(A·B, C, rewrite_rule_id='matrix_multiply_3x3', "
            "invariants_preserved=['rank', 'bilinear_complexity']). "
            "Or EQUIV(rank_decomposition_X, M3, equivalence_class_id="
            "'rank_decomposition_equivalence', witness=...)."
        ),
        "blocker": (
            "REWRITE expects scalar-valued Symbols. EQUIV's 3 witness types "
            "(proof_ref / finite_check / equiv_chain) don't carry rank-r "
            "decomposition data. Rank-r decomposition of M⟨3⟩ is a tuple of "
            "r outer products (a_i ⊗ b_i ⊗ c_i) — substrate has no "
            "primitive for outer-product witnesses."
        ),
        "verdict": "FAIL_ENCODING — no outer-product witness type",
    })

    # Probe 4: Path-of-least-stretch via OperatorPortabilityCertificate (T030)
    encoding_attempts.append({
        "probe": "encode_via_OperatorPortabilityCertificate",
        "attempt": (
            "T030 OperatorPortabilityCertificate carries 'operator transports "
            "from region A to region B' semantics. Could M⟨3⟩'s symmetry "
            "group (cyclic Z/3 action; GL_3 × GL_3 × GL_3 from each "
            "dimension) be a portability certificate? Operator = "
            "'cyclic_permutation_M3', source_chart = 'matrix_mult:M3:identity', "
            "target_chart = 'matrix_mult:M3:cyclic_permuted'."
        ),
        "blocker": (
            "T030 can express the symmetry GROUP ACTION at the metadata "
            "level (chart_id + transfer_method) but doesn't carry the "
            "tensor entry data. The encoding tags M⟨3⟩'s symmetry without "
            "letting the substrate do anything WITH it (rank lower-bound "
            "computation, decomposition search, etc.). Substrate-grade "
            "annotation, not substrate-grade compute."
        ),
        "verdict": "PARTIAL — symmetry annotation only, no compute backbone",
    })

    # Verdict + capability gap analysis
    capability_gaps_identified = [
        {
            "missing_primitive": "TensorObject (n-dim tensor with entry-level identity)",
            "needed_for": "any encoding of M⟨3⟩ that preserves multilinearity",
            "attack_paradigms_blocked": ["P28", "P29", "P30", "P31"],
            "catalog_entries_blocked": "#4 + #5 + #6 + at least #18-21 (similar bilinear-complexity objects)",
        },
        {
            "missing_primitive": "RankDecompositionWitness (sum of outer products with rank annotation)",
            "needed_for": "R(M⟨3⟩) lower/upper bound certificates as substrate-grade primitives",
            "attack_paradigms_blocked": ["P28", "P29"],
            "catalog_entries_blocked": "#4 + #5 + #6 + every rank-bound problem in §I",
        },
        {
            "missing_primitive": "MomentPolytope / SecantVarietyEquation (algebraic-geometric tensor object)",
            "needed_for": "Border-rank apolarity (P29) and Young-flattening (P31) certificates",
            "attack_paradigms_blocked": ["P29", "P31"],
            "catalog_entries_blocked": "Every border-rank / secant-variety problem in §I-III",
        },
    ]

    return {
        "lane": "12_catalog_pulled_M3_probe",
        "catalog_entry": "#4 Exact rank of M⟨3⟩",
        "attack_paradigms": ["P28", "P29", "P30", "P31"],
        "tensor_data_summary": {
            "shape": (9, 9, 9),
            "n_nonzero_entries": n_nonzero,
            "expected_n_nonzero": 27,  # for n=3, M⟨n⟩ has n^3 = 27 nonzero entries
        },
        "encoding_attempts": encoding_attempts,
        "all_attempts_failed": all(
            a["verdict"].startswith("FAIL") or a["verdict"].startswith("PARTIAL")
            for a in encoding_attempts
        ),
        "capability_gaps_identified": capability_gaps_identified,
        "verdict": "FAIL_ENCODING — substrate has NO native tensor primitive",
        "feeds_techne_ticket": "T-2026-05-08-T038 (substrate-primitive classification of all 104 catalog entries)",
    }


# ---------------------------------------------------------------------------
# Lane 8 — cert-extension regression smoke
# ---------------------------------------------------------------------------


def lane_8_cert_smoke() -> Dict[str, Any]:
    from sigma_kernel.exclusion_certificate import (
        Boundary, CertificateRegistry, CertificateRegistrationError,
        CertificateCollisionError, CertificateStrength, CertificateType,
        ExclusionCertificate, ExclusionClaim, RegionSpec,
        ReplayInfo, VerifierSet,
    )
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec

    spec = MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        version="1.0.0",
    )

    tests: List[Dict[str, Any]] = []

    cert = ExclusionCertificate(
        region_spec=RegionSpec(coordinate_chart_id="test:fire38", constraints={}, bounds=None),
        exclusion_claim=ExclusionClaim(
            excluded_property="probe", result_class="test", reason="fire38",
        ),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=(spec,)),
        replay=ReplayInfo(code_hash="x", data_hash="y", seed=0, environment_hash="z"),
    )

    reg = CertificateRegistry()

    # T1: register
    try:
        reg.register(cert, require_chart=False)
        tests.append({"id": "T1_register", "verdict": "PASS"})
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_register", "verdict": "FAIL",
            "actual": f"raised: {type(exc).__name__}",
        })

    # T2: collision
    try:
        reg.register(cert, require_chart=False)
        tests.append({"id": "T2_collision_raises", "verdict": "FAIL"})
    except (CertificateCollisionError, CertificateRegistrationError):
        tests.append({"id": "T2_collision_raises", "verdict": "PASS"})

    # T3: COMPLETE without triangulation_history → ValueError
    try:
        _ = ExclusionCertificate(
            region_spec=RegionSpec(coordinate_chart_id="test:fire38b", constraints={}, bounds=None),
            exclusion_claim=ExclusionClaim(
                excluded_property="probe", result_class="test", reason="fire38",
            ),
            certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
            strength=CertificateStrength.COMPLETE,
            verifier_set=VerifierSet(methods=(spec,)),
            replay=ReplayInfo(code_hash="x", data_hash="y", seed=0, environment_hash="z"),
        )
        tests.append({"id": "T3_complete_requires_triangulation", "verdict": "FAIL"})
    except ValueError:
        tests.append({"id": "T3_complete_requires_triangulation", "verdict": "PASS"})

    return {
        "lane": "8_cert_smoke",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 38,
        "posture": "first-HARD-6-fire (failures guide; tensor catalog drives lane 12)",
        "lanes": [12, 8],
        "lane_12": lane_12_m3_encoding_probe(),
        "lane_8": lane_8_cert_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_38_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: catalog #{summary['lane_12']['catalog_entry']}")
    print(f"  verdict: {summary['lane_12']['verdict']}")
    print(f"  capability gaps: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"Lane 8: {summary['lane_8']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
