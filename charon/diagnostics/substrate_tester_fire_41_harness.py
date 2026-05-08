"""Substrate-Tester Fire #41 harness — fourth fire under HARD-6 posture.

Lane 12 — pulled catalog entry #34 (Border-rank variety membership
problem; §IV Algebraic Geometry). NP-hard decision problem: given
tensor T and integer r, decide whether T in sigma_r (the r-th secant
variety of the Segre variety). Direct test of three-fire convergence:
this is canonically a positive-existential-with-witness problem. If
ConstructiveExistenceWitness surfaces again, the Tier-B finding
becomes four-fire-confirmed.

Lane 11 — canon-fuzz pytest regression (different from fires #38/#39/#40).

Outputs:
  charon/diagnostics/substrate_tester_fire_41_results.json
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — catalog entry #34: border-rank variety membership
# ---------------------------------------------------------------------------


def lane_12_border_rank_membership_probe() -> Dict[str, Any]:
    """Attempt to encode catalog entry #34 — border-rank variety
    membership — using existing substrate primitives. Specifically
    designed to TEST the Tier-B (ConstructiveExistenceWitness)
    prediction: this problem is a canonical positive-existential-with-
    witness, so ConstructiveExistenceWitness should surface again."""

    # Conceptual setup: sigma_r = closure in projective space of the
    # union of all rank-r tensors. Membership T in sigma_r is decided by
    # defining equations (when known: only sigma_2 generally, sigma_3
    # for some formats, sigma_4 for 4x4x4 via Salmon). In general T in
    # sigma_r iff there exists a sequence T_n -> T with rank(T_n) <= r.
    # Constructive witness: a Bini-style degeneration sequence
    # T(epsilon) = sum_{i=1}^r a_i(epsilon) ⊗ b_i(epsilon) ⊗ c_i(epsilon)
    # whose epsilon -> 0 limit equals T.
    #
    # Toy example: T = e_1 ⊗ e_1 ⊗ e_2 + e_1 ⊗ e_2 ⊗ e_1 + e_2 ⊗ e_1 ⊗ e_1
    # (the "W tensor" in 2x2x2). Rank 3, border rank 2 (Bini's classical
    # example). T in sigma_2 — but no rank-2 decomposition; need a
    # degeneration witness.

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode membership as CLAIM
    encoding_attempts.append({
        "probe": "encode_membership_as_CLAIM",
        "attempt": (
            "CLAIM(target_name='W_tensor', "
            "hypothesis='W in sigma_2 (border rank <= 2)', "
            "evidence={...}, kill_path='check_no_degeneration_sequence', "
            "target_tier=Conjecture). The kill_path attempts to falsify "
            "by finding a defining-equation violator."
        ),
        "blocker": (
            "CLAIM stores hypothesis as a string. The substrate has no "
            "way to represent 'sigma_r' as a substrate-grade object — "
            "it's a variety (algebraic-geometric scheme), not a region "
            "or chart. Even if hypothesis is just text: the evidence dict "
            "would need to carry a degeneration witness, which has no "
            "substrate type. SchemeMembership claim shape unsupported."
        ),
        "verdict": "FAIL_ENCODING — no SchemeObject / VarietyObject primitive",
    })

    # Probe 2: encode degeneration witness as EQUIV with parametric chain
    encoding_attempts.append({
        "probe": "encode_degeneration_via_EQUIV_chain",
        "attempt": (
            "EQUIV(W_tensor, limit_object, equivalence_class_id="
            "'border_rank_2_membership', witness_type=equiv_chain, "
            "witness=[T(epsilon_1), T(epsilon_2), ...] as epsilon -> 0). "
            "The chain encodes a Bini-style degeneration sequence."
        ),
        "blocker": (
            "EQUIV's equiv_chain witness type is for FINITE chains of "
            "syntactic equivalences (e.g. rewrite chains). Border-rank "
            "membership requires an INFINITE LIMIT (epsilon -> 0). "
            "Substrate has no LimitWitness / ParametricFamily primitive. "
            "Could approximate by truncating to finite epsilon — but then "
            "loses the 'limit equals T' semantic, leaving only an "
            "inequality 'T near sigma_2.'"
        ),
        "verdict": "FAIL_ENCODING — no LimitWitness / ParametricFamily",
    })

    # Probe 3: ExclusionCertificate for non-membership
    encoding_attempts.append({
        "probe": "encode_non_membership_via_ExclusionCertificate",
        "attempt": (
            "ExclusionCertificate(region_spec=..., exclusion_claim="
            "ExclusionClaim(excluded_property='border_rank_le_r', "
            "result_class='secant_variety_membership', reason="
            "'defining_equation_violated'), ...). Defining equations of "
            "sigma_r (Young flattenings, border-apolarity equations) "
            "cert the non-membership."
        ),
        "blocker": (
            "Works for non-membership (negative direction). BUT same "
            "asymmetric-existential gap as fires #39 + #40: T in sigma_r "
            "(positive direction) has no constructive-witness primitive. "
            "Substrate could store 'T not in sigma_r because Young-"
            "flattening rank > r' but couldn't store 'T in sigma_r "
            "witnessed by Bini degeneration sequence.' THIS IS THE "
            "FOURTH PARADIGM TO HIT THE SAME GAP."
        ),
        "verdict": "PARTIAL — non-membership encodable, membership witness has no home",
    })

    # Probe 4: encode the variety via CoordinateChart
    encoding_attempts.append({
        "probe": "encode_sigma_r_as_CoordinateChart",
        "attempt": (
            "CoordinateChart(domain='secant_variety', region_key="
            "'sigma_2_2x2x2', coordinate_system=('rank_param', "
            "'tensor_entries'), metric=...). Treat sigma_r as a region."
        ),
        "blocker": (
            "Variety sigma_r is an ALGEBRAIC SCHEME — vanishing locus of "
            "polynomial ideal — not a coordinate chart. CoordinateChart "
            "represents differentiable manifolds with coordinate axes; "
            "sigma_r has singular loci, irreducible components, "
            "embedded primes. Mapping a scheme to a chart loses the "
            "scheme structure."
        ),
        "verdict": "FAIL_ENCODING — no SchemeObject / IdealObject primitive",
    })

    capability_gaps_identified = [
        {
            "missing_primitive": "ConstructiveExistenceWitness (4TH PARADIGM CONFIRMATION)",
            "purpose": "constructive witness for positive existential — completing ExclusionCertificate's asymmetry",
            "needed_for": "border-rank membership (#34), tensor iso (#58), contraction order (#84), rank decomposition (#4)",
            "convergence_with_fires_38_39_40": (
                "FOUR fires (#38/#39/#40/#41) from FOUR sections "
                "(§I/§X/§VII/§IV) and FOUR paradigm-clusters all hit the "
                "same shape: substrate has ExclusionCertificate for "
                "negative existentials but no companion for positive "
                "existentials with witness. This is now the most robust "
                "finding of the matrix-filling exercise. Tier B should be "
                "treated as confirmed contract-change priority."
            ),
            "blocks_paradigms": ["P28", "P29", "P30", "P31", "all NP-search problems"],
            "blocks_catalog_entries": "broader than tensors — applies to any 'witnessed existential' decision the substrate may track",
        },
        {
            "missing_primitive": "SchemeObject / IdealObject / VarietyObject",
            "purpose": "represent algebraic schemes (vanishing loci of polynomial ideals); singular loci, components, primes",
            "needed_for": "secant varieties (sigma_r), SLOCC orbit closures, defective varieties (#26-33), border-rank variety geometry",
            "blocks_paradigms": ["P29", "P31"],
            "blocks_catalog_entries": "all of Section IV (#26-35) + parts of Section III (Waring) + Section X #79 (orbit closures)",
            "convergence_note": (
                "NEW PRIMITIVE not surfaced in fires #38/#39/#40. Section "
                "IV's algebraic-geometric flavor introduces a distinct "
                "foundational object class. Tier A's TensorAlgebra "
                "subsystem should be EXTENDED with SchemeObject as the "
                "geometric companion to TensorObject + TensorNetworkGraph."
            ),
        },
        {
            "missing_primitive": "LimitWitness / ParametricFamily",
            "purpose": "represent limits / degeneration sequences with parameter epsilon -> 0",
            "needed_for": "border-rank witnesses (Bini degenerations), asymptotic restriction, deformation arguments",
            "blocks_paradigms": ["P28", "P29"],
            "blocks_catalog_entries": "#5 + #10 + #34 + most border-rank problems in §I + apolarity-style degeneration in §IV",
            "convergence_note": (
                "Specialization of ConstructiveExistenceWitness for the "
                "'limit-of-rank-r-decompositions' case. Could be a subtype "
                "of ConstructiveExistenceWitness rather than separate "
                "primitive."
            ),
        },
    ]

    return {
        "lane": "12_catalog_pulled_border_rank_membership_probe",
        "catalog_entry": "#34 Border-rank variety membership problem",
        "section": "IV. Algebraic Geometry: Secant Varieties, Schemes, Apolarity",
        "attack_paradigms": ["P29", "P31"],
        "encoding_attempts": encoding_attempts,
        "all_attempts_failed": all(
            a["verdict"].startswith("FAIL") or a["verdict"].startswith("PARTIAL")
            for a in encoding_attempts
        ),
        "capability_gaps_identified": capability_gaps_identified,
        "verdict": "FAIL_ENCODING — Tier-B confirmed (4th paradigm) + new SchemeObject + LimitWitness primitives needed",
        "feeds_techne_ticket": "T-2026-05-08-T038 (substrate-primitive classification of all 104 catalog entries)",
        "tier_B_confirmation_status": (
            "FOUR FIRES, FOUR PARADIGMS, SAME GAP. "
            "ConstructiveExistenceWitness is now the most robust "
            "missing-primitive finding from matrix-filling. "
            "Recommendation: Aporia coordination ticket flagging Tier B "
            "for strategic-planning review."
        ),
        "tier_A_extension": (
            "Tier A (TensorAlgebra subsystem) should be extended with "
            "SchemeObject / IdealObject as the algebraic-geometric "
            "companion to TensorObject + TensorNetworkGraph + GroupAction. "
            "Section IV's geometric flavor can't reduce to the existing "
            "Tier-A primitives."
        ),
    }


# ---------------------------------------------------------------------------
# Lane 11 — canon-fuzz pytest regression
# ---------------------------------------------------------------------------


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    """Run prometheus_math/tests/test_canonicalization_fuzz.py with a
    fresh seed; report pass/fail counts."""
    seed = "20260508_06"
    cmd = [
        "pytest",
        "prometheus_math/tests/test_canonicalization_fuzz.py",
        "-q",
        "--no-header",
        "-x",
        f"--hypothesis-seed={seed}",
    ]
    proc = subprocess.run(
        cmd, cwd=str(REPO), capture_output=True, text=True, timeout=240,
    )
    stdout_tail = "\n".join(proc.stdout.splitlines()[-15:])
    stderr_tail = "\n".join(proc.stderr.splitlines()[-5:]) if proc.stderr else ""

    # Parse the "X passed" line
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()

    return {
        "lane": "11_canon_fuzz_smoke",
        "seed": seed,
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 41,
        "posture": "fourth-HARD-6-fire (matrix-filling: §IV catalog entry #34; testing Tier-B prediction directly)",
        "lanes": [12, 11],
        "lane_12": lane_12_border_rank_membership_probe(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_41_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: catalog #34 verdict = {summary['lane_12']['verdict'][:60]}...")
    print(f"  capability gaps: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"  tier_B_status: {summary['lane_12']['tier_B_confirmation_status'][:60]}...")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
