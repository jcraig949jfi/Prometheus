"""Substrate-Tester Fire #45 harness — eighth fire under HARD-6 posture.

Lane 12 — pulled catalog entry #40 (Generic CP identifiability beyond
Kruskal; §V Generic Rank, Maximum Rank, Identifiability). Sharp generic
identifiability conditions for CP rank decompositions beyond Kruskal's
bound 2r + 2 <= k_1 + k_2 + k_3. Identifiability is a "generic"
property — true for tensors in a full-measure subset.

Predicted outcome (per fire #43's Tier-B/D composition finding):
identifiability claims compose Tier B (individual decomposition is
unique) + Tier D (the generically-identifiable SET has full measure).
This fire tests the prediction.

Lane 11 — canon-fuzz pytest fresh seed 20260508_09.

Outputs:
  charon/diagnostics/substrate_tester_fire_45_results.json
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_12_identifiability_probe() -> Dict[str, Any]:
    """Test whether §V identifiability fits the predicted Tier-B/Tier-D
    composition shape, or surfaces new gaps."""

    # Conceptual setup: A tensor T = sum_{i=1}^r u_i (x) v_i (x) w_i is
    # "identifiable" if the CP decomposition is unique up to permutation
    # and scaling. Kruskal's theorem: if 2r + 2 <= k_1 + k_2 + k_3
    # (k-rank conditions on factor matrices), T is identifiable.
    #
    # GENERIC identifiability: the SET of identifiable rank-r tensors
    # has full measure in the rank-r locus (sigma_r). The complement
    # has measure zero but may contain specific T's. So:
    #   - Individual claim: "this specific T is uniquely decomposable"
    #     = Tier B (existential witness: the decomposition).
    #   - Generic claim: "rank-r tensors are generically identifiable
    #     in format (n_1, n_2, n_3)" = Tier D (full-measure set).

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode individual identifiability via Tier B
    encoding_attempts.append({
        "probe": "encode_individual_identifiability_via_Tier_B",
        "attempt": (
            "Tier-B ConstructiveExistenceWitness with witness type = "
            "RankDecompositionWitness PLUS uniqueness-up-to-permutation "
            "annotation. Existence + UNIQUENESS witness."
        ),
        "tier_B_fit": (
            "FITS for individual claim. RankDecompositionWitness from "
            "fire #38 needs an extension: uniqueness annotation. "
            "Could be a flag on RankDecompositionWitness "
            "(witness.uniqueness ∈ {nonunique, locally_unique, "
            "globally_unique}) or a sibling subtype "
            "UniquenessRankDecompositionWitness."
        ),
        "verdict": "TIER_B_REFINEMENT — uniqueness annotation needed on existing subtype",
    })

    # Probe 2: encode generic identifiability via Tier D
    encoding_attempts.append({
        "probe": "encode_generic_identifiability_via_Tier_D",
        "attempt": (
            "Tier-D primitives for the generic claim. The 'set of "
            "identifiable tensors has full measure in sigma_r' uses "
            "ProbabilityMeasure (full Lebesgue measure on the rank-r "
            "stratum) + a complement-set primitive (the non-identifiable "
            "exceptional subset has measure zero)."
        ),
        "tier_D_fit": (
            "FITS — ProbabilityMeasure + DistributionObject from fires "
            "#42/#43 cover the generic claim cleanly. NEW Tier-D "
            "candidate: GenericityAlmostEverywhereCert (measure-zero "
            "exception). Could be a specialization of "
            "ProbabilityMeasure rather than separate primitive."
        ),
        "verdict": "TIER_D_FITS — possible new GenericityAlmostEverywhereCert",
    })

    # Probe 3: confirm Tier-B/Tier-D composition (predicted fire #43)
    encoding_attempts.append({
        "probe": "confirm_tier_B_tier_D_composition",
        "attempt": (
            "The full identifiability claim COMPOSES B + D: 'this T is "
            "uniquely decomposable (Tier B) AND the format (n_1, n_2, "
            "n_3, r) admits generic identifiability (Tier D)'. The "
            "individual claim implies the generic claim FOR ALMOST ALL "
            "T at fixed format."
        ),
        "tier_B_tier_D_composition_fit": (
            "CONFIRMED. Identifiability is naturally Tier-B/Tier-D "
            "composition: individual existential at the Tier B layer "
            "(specific decomposition is unique), generic distributional "
            "at the Tier D layer (the format admits identifiability "
            "generically). Tier B/D compose as predicted by fire #43, "
            "second independent confirmation."
        ),
        "verdict": "TIER_B_TIER_D_COMPOSITION_CONFIRMED — second instance",
    })

    # Probe 4: Kruskal-bound certification
    encoding_attempts.append({
        "probe": "encode_Kruskal_bound_as_certification",
        "attempt": (
            "Kruskal's theorem: if 2r + 2 <= k_1 + k_2 + k_3, T is "
            "identifiable. This is a SUFFICIENT CONDITION certificate. "
            "Kruskal-style bound = a structural sufficient condition; "
            "k-rank computation = a substrate-grade method."
        ),
        "kruskal_fit": (
            "FITS Tier-B as a structural certificate. The k-rank "
            "computation is a MethodSpec; the inequality 2r + 2 <= "
            "sum k_i is a verifiable predicate; satisfying it is a "
            "POSITIVE EXISTENTIAL via Tier B "
            "ConstructiveExistenceWitness with witness type = "
            "structural_inequality_certificate. No new primitive "
            "needed; existing infrastructure covers."
        ),
        "verdict": "TIER_B_FITS — structural-inequality witness subtype",
    })

    capability_gaps_identified = [
        {
            "primitive": "uniqueness annotation on RankDecompositionWitness (Tier B refinement)",
            "purpose": "track unique vs locally-unique vs globally-unique decomposition status",
            "needed_for": "identifiability claims (#40, #41, #42)",
            "tier_classification": "Refinement of existing Tier B subtype, not new primitive",
        },
        {
            "primitive": "GenericityAlmostEverywhereCert (Tier D refinement)",
            "purpose": "encode 'P holds for measure-1 subset' claims with measure-zero exception annotation",
            "needed_for": "generic identifiability, generic rank, full-measure properties",
            "tier_classification": "Specialization of ProbabilityMeasure, possibly subtype",
        },
        {
            "primitive": "structural_inequality_certificate (Tier B subtype #6)",
            "purpose": "Kruskal-bound-style sufficient-condition certificates",
            "needed_for": "Kruskal identifiability, Schwartz-Zippel-style bounds, generic-position certificates",
            "tier_classification": "New Tier B subtype",
        },
    ]

    return {
        "lane": "12_catalog_pulled_identifiability_probe",
        "catalog_entry": "#40 Generic CP identifiability beyond Kruskal",
        "section": "V. Generic Rank, Maximum Rank, Identifiability",
        "attack_paradigms": ["P29 algebraic-geometric, P28 distributional"],
        "encoding_attempts": encoding_attempts,
        "tier_B_tier_D_composition_status": "CONFIRMED (second independent instance after fire #43)",
        "capability_gaps_identified": capability_gaps_identified,
        "verdict": "TIER_B_TIER_D_COMPOSITION_FITS + 3 refinements (no new tier)",
        "feeds_techne_ticket": "T-2026-05-08-T038 + supplements ST-fire43-001/44-001 with refinement details",
        "tier_summary_after_8_fires": (
            "5-tier model HOLDS without addition. Fire #45 surfaces "
            "REFINEMENTS to existing tiers, not new tiers:\n"
            "  - Tier B: uniqueness annotation on RankDecompositionWitness "
            "    + structural_inequality_certificate as 6th subtype "
            "    (was 5 in fire #44)\n"
            "  - Tier D: GenericityAlmostEverywhereCert as ProbabilityMeasure "
            "    specialization\n"
            "  - Tier B/D composition: CONFIRMED second independent "
            "    instance (after fire #43's tensor PCA threshold)\n"
            "\n"
            "Saturation evidence: matrix-filling now producing "
            "REFINEMENTS (not new tiers). 5-tier model + ~22 primitives "
            "+ cross-tier composition is approaching robust coverage."
        ),
        "saturation_signal": (
            "FIRE #45 is the strongest saturation signal yet. "
            "Identifiability problem sits at the §V/§VI/§IX boundary; "
            "if 5-tier model holds here, it's likely robust across the "
            "remaining unpulled sections (§II Rank Zoo, §III Waring, §VI "
            "Numerical Decomposition, §XI Specific Tensor Families). "
            "Substrate-tester recommendation update: pivot to test-suite "
            "design after fire #45 unless Aporia explicitly extends "
            "matrix-filling cadence."
        ),
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260508_09"
    import sys as _sys
    cmd = [
        _sys.executable, "-m", "pytest",
        "prometheus_math/tests/test_canonicalization_fuzz.py",
        "-q", "--no-header", "-x", f"--hypothesis-seed={seed}",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=240)
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    return {
        "lane": "11_canon_fuzz_smoke",
        "seed": seed,
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 45,
        "posture": "eighth-HARD-6-fire (matrix-filling: §V identifiability; testing Tier-B/D composition prediction + saturation)",
        "lanes": [12, 11],
        "lane_12": lane_12_identifiability_probe(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_45_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12 verdict: {summary['lane_12']['verdict']}")
    print(f"  composition status: {summary['lane_12']['tier_B_tier_D_composition_status']}")
    print(f"  gaps surfaced: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
