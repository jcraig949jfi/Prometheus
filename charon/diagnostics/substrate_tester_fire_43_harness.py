"""Substrate-Tester Fire #43 harness — sixth fire under HARD-6 posture.

Lane 12 — pulled catalog entry #73 (Tensor PCA computational threshold;
§IX Random Tensors and Probabilistic Problems). Direct §IX hit
to CONFIRM Tier D primitive shape (DistributionObject + StatisticalTestSpec
+ ProbabilityMeasure) from fire #42, OR surface NEW distributional
primitives. Tensor PCA has a STATISTICAL THRESHOLD (information-
theoretic recovery) and a COMPUTATIONAL THRESHOLD (poly-time AMP /
SOS-bounded recovery) — sharp characterization of the gap is open.

Lane 11 — canon-fuzz pytest fresh seed (20260508_07).

Outputs:
  charon/diagnostics/substrate_tester_fire_43_results.json
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — catalog entry #73: tensor PCA computational threshold
# ---------------------------------------------------------------------------


def lane_12_tensor_pca_threshold_probe() -> Dict[str, Any]:
    """Attempt to encode catalog entry #73 — tensor PCA statistical-
    vs-computational threshold gap — using Tier-A/B/C/D primitives
    proposed in fires #38-#42. Goal: confirm or extend Tier D shape."""

    # Conceptual setup: spiked tensor model T = lambda * v⊗d + W where
    # W has i.i.d. Gaussian entries and v is the planted signal vector
    # (||v||=1). Statistical threshold: information-theoretically
    # recoverable for lambda > c_stat * n^{(1-d/2)/2}. Computational
    # threshold: efficient algorithms (AMP, SOS) require larger lambda
    # ~ n^{(d/2-1)/4} or worse. Sharp characterization of the gap is
    # open. Two thresholds on the SAME ensemble = need to encode both
    # phases as substrate objects.

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode the spike model as Tier-D DistributionObject (proposed)
    encoding_attempts.append({
        "probe": "encode_spiked_model_as_proposed_DistributionObject",
        "attempt": (
            "Use Tier D's DistributionObject (proposed) to represent the "
            "ensemble: T = lambda * v_outer_d + W where W has i.i.d. "
            "Gaussian entries. Parameters: (n, d, lambda, signal_v)."
        ),
        "tier_D_fit": (
            "FITS — DistributionObject with parameters (n, d, lambda, v) "
            "captures the family of spiked tensors. CONFIRMS Tier D's "
            "expected shape."
        ),
        "verdict": "TIER_D_CONFIRMED — DistributionObject works for spike model",
    })

    # Probe 2: dual-threshold representation — the GAP itself
    encoding_attempts.append({
        "probe": "encode_dual_threshold_gap",
        "attempt": (
            "The OPEN problem (#73) is the gap between statistical "
            "threshold lambda_stat ~ n^{(1-d/2)/2} and computational "
            "threshold lambda_comp ~ n^{(d/2-1)/4}. Need to represent "
            "BOTH thresholds + the gap region as substrate objects."
        ),
        "tier_D_fit": (
            "PARTIAL FIT — DistributionObject can hold the ensemble "
            "PARAMETERIZATION but doesn't natively carry THRESHOLDS as "
            "first-class objects. PhaseTransitionThreshold is a "
            "candidate NEW Tier-D primitive: a triple (parameter_axis, "
            "threshold_value, regime_below, regime_above) carrying "
            "information-theoretic vs computational semantics. The GAP "
            "region between two thresholds is itself a substrate-grade "
            "object (a 'computational hardness regime')."
        ),
        "verdict": "EXTENDS_TIER_D — PhaseTransitionThreshold as additional Tier-D primitive needed",
    })

    # Probe 3: SOS lower-bound certificate — Tier B intersection?
    encoding_attempts.append({
        "probe": "encode_SOS_lower_bound_as_Tier_B",
        "attempt": (
            "SOS hierarchy lower bounds (Hopkins-Steurer-Schramm) are "
            "computational-hardness certificates: 'no degree-k SOS "
            "polynomial certifies recovery at lambda < lambda_SOS_k'. "
            "Could be a Tier B ConstructiveExistenceWitness with "
            "Witness=SOS-decomposition? OR negative existential "
            "(ExclusionCertificate)?"
        ),
        "tier_B_intersection": (
            "MIXED — SOS certificates CAN be cast as Tier-B existential: "
            "'there EXISTS a degree-k SOS polynomial certifying recovery' "
            "(positive) vs 'no such polynomial exists' (negative, "
            "ExclusionCertificate). BUT the threshold scaling is "
            "DISTRIBUTIONAL — it's about how lambda scales with n, not "
            "individual instances. Tier-B ConstructiveExistenceWitness "
            "applies AT FIXED (n, d, lambda) — but the THRESHOLD ITSELF "
            "is Tier-D. Two-tier interaction: Tier B for individual SOS "
            "certificates, Tier D for the threshold curve."
        ),
        "verdict": "TIER_B_TIER_D_INTERACTION — primitives compose cleanly",
    })

    # Probe 4: AMP / power-method as MethodSpec?
    encoding_attempts.append({
        "probe": "encode_AMP_power_method_as_MethodSpec",
        "attempt": (
            "AMP (Approximate Message Passing) and tensor power method "
            "as MethodSpec instances; their RECOVERY SUCCESS / FAILURE "
            "as evidence in CLAIMs about the spiked model."
        ),
        "tier_existing_fit": (
            "PARTIAL — MethodSpec covers the algorithm at instance level "
            "(run AMP at fixed n, d, lambda). For the THRESHOLD "
            "characterization, need to encode 'AMP succeeds for lambda > "
            "threshold_AMP, fails below' — that's a "
            "DistributionalAlgorithmGuarantee (algorithm + "
            "distributional regime + success-probability bound). "
            "Possibly a fourth Tier-D primitive: AlgorithmThresholdCert "
            "or AsymptoticSuccessGuarantee."
        ),
        "verdict": "EXTENDS_TIER_D — AlgorithmThresholdCert candidate",
    })

    capability_gaps_identified = [
        {
            "primitive": "DistributionObject (Tier D)",
            "status": "CONFIRMED via spike model encoding",
            "convergence_with_fire_42": "First independent confirmation that Tier-D's DistributionObject shape from fire #42 fits a fresh §IX problem.",
        },
        {
            "primitive": "PhaseTransitionThreshold (NEW Tier D primitive)",
            "purpose": "represent threshold values + regime semantics (statistical vs computational) on a parameter axis",
            "needed_for": "tensor PCA threshold (#73), all phase-transition problems in §IX, area-law thresholds in §X",
            "blocks_paradigms": ["P28 distributional"],
            "tier_D_extension": (
                "Expands Tier D from 3 primitives (DistributionObject, "
                "StatisticalTestSpec, ProbabilityMeasure) to 4. Threshold "
                "is a substrate-grade object distinct from individual "
                "samples — encodes the phase-transition geometry of the "
                "ensemble."
            ),
        },
        {
            "primitive": "AlgorithmThresholdCert / AsymptoticSuccessGuarantee (NEW Tier D / cross-tier)",
            "purpose": "encode '<algorithm> succeeds with probability >= p for parameter > threshold' contracts",
            "needed_for": "AMP, tensor power method, SOS hierarchy guarantees, all asymptotic algorithm-success claims",
            "tier_interaction": (
                "Lives at Tier D / MethodSpec interface. MethodSpec "
                "alone is per-instance; AlgorithmThresholdCert is "
                "asymptotic / distributional. Could be MethodSpec + "
                "PhaseTransitionThreshold composed, OR a distinct "
                "primitive."
            ),
        },
    ]

    tier_B_tier_D_interaction = {
        "finding": (
            "Tier B (ConstructiveExistenceWitness) and Tier D "
            "(distributional primitives) COMPOSE rather than overlap. "
            "Individual SOS certificates at fixed (n, d, lambda) are "
            "Tier-B (positive existential with witness); the threshold "
            "curve they trace as (n, d, lambda) varies is Tier-D "
            "(distributional)."
        ),
        "implication": (
            "Substrate primitives interlock cleanly across tiers. "
            "Fire #43 finding: Tier D's DistributionObject + "
            "PhaseTransitionThreshold + AlgorithmThresholdCert give "
            "Tier-B's ConstructiveExistenceWitness a distributional "
            "context. Together they cover both individual and asymptotic "
            "claims about random ensembles."
        ),
    }

    return {
        "lane": "12_catalog_pulled_tensor_pca_threshold_probe",
        "catalog_entry": "#73 Tensor PCA computational threshold",
        "section": "IX. Random Tensors and Probabilistic Problems",
        "attack_paradigms": ["P28 distributional"],
        "encoding_attempts": encoding_attempts,
        "tier_D_status": "CONFIRMED + EXTENDED (3 → 5 primitives)",
        "capability_gaps_identified": capability_gaps_identified,
        "tier_B_tier_D_interaction": tier_B_tier_D_interaction,
        "verdict": "TIER_D_CONFIRMED + EXTENDED — DistributionObject fits; PhaseTransitionThreshold + AlgorithmThresholdCert added",
        "feeds_techne_ticket": "T-2026-05-08-T038 + supplements ST-fire42-001 with extended Tier D scope",
        "tier_summary_after_6_fires": (
            "Tier A (TensorAlgebra subsystem): TensorObject + "
            "TensorNetworkGraph + GroupAction + SchemeObject\n"
            "\n"
            "Tier B (ConstructiveExistenceWitness — QUALIFIED to "
            "decision-problems-with-individual-witness): "
            "RankDecompositionWitness + ContractionOrderWitness + "
            "IsomorphismCertificate + LimitWitness/BorderRankWitness + "
            "[SOS certificates at fixed parameters per fire #43]\n"
            "\n"
            "Tier C (discrete-optimization geometry): MomentPolytope + "
            "RewriteSearchTree + OrbitStratification\n"
            "\n"
            "Tier D (distributional / population-level — EXTENDED in "
            "fire #43 from 3 to 5 primitives): DistributionObject + "
            "StatisticalTestSpec + ProbabilityMeasure + "
            "PhaseTransitionThreshold + AlgorithmThresholdCert\n"
            "\n"
            "Six fires, four tiers, ~16 substrate primitives proposed. "
            "Tier B/D INTERACTION (composes cleanly) is fire #43's "
            "additional finding."
        ),
    }


# ---------------------------------------------------------------------------
# Lane 11 — canon-fuzz pytest fresh seed
# ---------------------------------------------------------------------------


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260508_07"
    import sys as _sys
    cmd = [
        _sys.executable, "-m", "pytest",
        "prometheus_math/tests/test_canonicalization_fuzz.py",
        "-q", "--no-header", "-x", f"--hypothesis-seed={seed}",
    ]
    proc = subprocess.run(
        cmd, cwd=str(REPO), capture_output=True, text=True, timeout=240,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    return {
        "lane": "11_canon_fuzz_smoke",
        "seed": seed,
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-10:]),
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 43,
        "posture": "sixth-HARD-6-fire (matrix-filling: §IX catalog entry #73; Tier D shape confirmation + extension)",
        "lanes": [12, 11],
        "lane_12": lane_12_tensor_pca_threshold_probe(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_43_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: catalog #73 verdict = {summary['lane_12']['verdict'][:70]}...")
    print(f"  Tier-D status: {summary['lane_12']['tier_D_status']}")
    print(f"  capability gaps: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
