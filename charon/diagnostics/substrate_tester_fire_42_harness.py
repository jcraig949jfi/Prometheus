"""Substrate-Tester Fire #42 harness — fifth fire under HARD-6 posture.

Lane 12 — pulled catalog entry #66 (Z-eigenvalue distribution; §VIII
Spectral and Eigenvalue Theory). DELIBERATE DIVERGENCE TEST: this is
a distributional / probabilistic flavor problem (count and statistical
distribution of Z-eigenvalues for symmetric tensors), structurally
orthogonal to rank/decomposition/equivalence/membership. If Tier-B
(ConstructiveExistenceWitness) surfaces even here, the substrate-wide
finding is even stronger. If it DIVERGES with a new gap shape, that
qualifies the substrate-wide claim and surfaces NEW primitive needs.

Lane 9 — sigma_kernel test suite full sweep (different from per-primitive
regressions in fires #38-#41).

Outputs:
  charon/diagnostics/substrate_tester_fire_42_results.json
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — catalog entry #66: Z-eigenvalue distribution
# ---------------------------------------------------------------------------


def lane_12_z_eigenvalue_distribution_probe() -> Dict[str, Any]:
    """Attempt to encode catalog entry #66 — Z-eigenvalue distribution
    of symmetric tensors — using existing substrate primitives.
    Distributional/probabilistic flavor. Tests whether Tier-B keeps
    surfacing or whether NEW gap shapes emerge."""

    # Conceptual setup: For symmetric tensor T in S^d V (V = R^n), a
    # Z-eigenvalue is a real lambda such that there exists unit vector
    # x with T x^{d-1} = lambda x. By Cartwright-Sturmfels the COMPLEX
    # count is bounded by ((d-1)^n - 1)/(d-2) for general T. Real count
    # is more delicate.
    #
    # Distribution problem: as n grows / T is randomized (e.g. Gaussian
    # entries), what is the distribution of (count, gap, magnitude) of
    # Z-eigenvalues? Random matrix theory adapted (Auffinger-Ben Arous).
    # This is a STATISTICAL question over an ENSEMBLE of tensors.

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode the distribution as KillVector evidence
    encoding_attempts.append({
        "probe": "encode_distribution_as_KillVector_population",
        "attempt": (
            "Run Monte Carlo: sample T_1, T_2, ... from Gaussian "
            "ensemble. For each, compute Z-eigenvalue counts; aggregate "
            "into KillVector evidence. Fit empirical distribution; "
            "compare to predicted limit law."
        ),
        "blocker": (
            "KillVector is a single-instance falsifier outcome, not a "
            "DISTRIBUTION over outcomes. Substrate has no "
            "DistributionObject / EmpiricalCDF / RandomTensorEnsemble "
            "primitive. Could store individual KillVectors per sample "
            "but the AGGREGATE statistical content (mean, variance, "
            "quantile, predicted-vs-empirical-CDF distance) has no "
            "substrate-grade home."
        ),
        "verdict": "FAIL_ENCODING — no DistributionObject / Ensemble primitive",
    })

    # Probe 2: encode the population claim as CLAIM
    encoding_attempts.append({
        "probe": "encode_population_claim_as_CLAIM",
        "attempt": (
            "CLAIM(target_name='gaussian_symmetric_tensor_3_n', "
            "hypothesis='Z-eigenvalue count is asymptotically log-normal "
            "with parameters mu(n,d), sigma(n,d)', "
            "evidence={...empirical fit metrics...}, "
            "kill_path='KS_test_against_predicted_distribution')."
        ),
        "blocker": (
            "CLAIM with hypothesis as a string can carry a "
            "DISTRIBUTIONAL hypothesis at the text level. BUT the "
            "substrate's evidence dict is opaque — no schema for "
            "distributional evidence (sample size, test statistic, "
            "p-value, CI). Falsification via KS test relies on the "
            "kill_path running an external statistical test; substrate "
            "has no StatisticalTestSpec primitive that knows about "
            "test statistics, sample-size requirements, or false "
            "discovery rate."
        ),
        "verdict": "PARTIAL — claim shape works at text level, evidence semantics missing",
    })

    # Probe 3: encode random tensor ensemble as CoordinateChart
    encoding_attempts.append({
        "probe": "encode_ensemble_as_CoordinateChart",
        "attempt": (
            "CoordinateChart(domain='random_tensor_ensemble', "
            "region_key='gaussian_symmetric_3_n', coordinate_system="
            "('mean', 'covariance', 'sample_size'), metric=...)."
        ),
        "blocker": (
            "CoordinateChart represents a deterministic geometric region; "
            "random ensembles are PROBABILITY MEASURES on tensor space, "
            "which require a sigma-algebra + measure structure. Chart's "
            "metric/coordinate semantics is too poor — can register the "
            "PARAMETERS of an ensemble (mean, covariance) but not the "
            "MEASURE-THEORETIC SUPPORT and probability semantics. "
            "ProbabilityMeasure / RandomVariable primitives missing."
        ),
        "verdict": "FAIL_ENCODING — no ProbabilityMeasure / RandomVariable",
    })

    # Probe 4: tier-B re-test — is there a positive existential witness
    # angle here?
    encoding_attempts.append({
        "probe": "search_for_tier_B_pattern",
        "attempt": (
            "Search for the asymmetric-existential gap. Z-eigenvalue "
            "distribution is fundamentally a POPULATION-LEVEL claim, "
            "not an individual existential. The 'witness' is a sample "
            "+ statistical test, not a constructive object."
        ),
        "blocker": (
            "TIER-B DOES NOT NATURALLY APPLY. This problem class is "
            "DISTRIBUTIONAL/POPULATION-LEVEL, not "
            "individual-existential. ConstructiveExistenceWitness "
            "doesn't fit — there's no individual T to witness. "
            "ENCOURAGING DIVERGENCE FINDING: Tier B is decision-problem-"
            "specific, NOT universal across the catalog. Distributional "
            "problems need a SEPARATE primitive class."
        ),
        "verdict": "DIVERGENCE_CONFIRMED — Tier B does not apply",
    })

    capability_gaps_identified = [
        {
            "missing_primitive": "DistributionObject / EmpiricalCDF / RandomTensorEnsemble",
            "purpose": "represent probability distributions over tensor space; ensemble-level claims",
            "needed_for": "random tensor problems (#71-74), Z-eigenvalue distribution (#66), random matrix theory adaptations",
            "blocks_paradigms": ["P28 (asymptotic spectrum)"],
            "blocks_catalog_entries": "Section IX (#71-74) + #66 + parts of §VIII",
            "convergence_note": (
                "NEW PRIMITIVE FAMILY not surfaced in fires #38/#39/#40/#41. "
                "Tier A (TensorAlgebra) + Tier B (ConstructiveExistenceWitness) "
                "+ Tier C (discrete-optimization) all assume INDIVIDUAL OBJECTS. "
                "This fire reveals a fourth tier needed: DISTRIBUTIONAL "
                "primitives for population-level claims."
            ),
        },
        {
            "missing_primitive": "StatisticalTestSpec",
            "purpose": "encode a statistical test (KS, chi-squared, permutation null, etc.) as substrate-grade method with known null distribution + p-value contract",
            "needed_for": "any population-level claim needing falsification via statistical test",
            "blocks_paradigms": ["P28"],
            "convergence_with_existing_substrate": (
                "RELATED to but NOT the same as MethodSpec. MethodSpec is "
                "for deterministic computational methods; StatisticalTestSpec "
                "would carry distributional assumptions, sample-size "
                "requirements, false-discovery-rate semantics. Could be a "
                "specialization of MethodSpec or a separate primitive."
            ),
        },
        {
            "missing_primitive": "ProbabilityMeasure / RandomVariable",
            "purpose": "measure-theoretic primitive for probability distributions on tensor space",
            "needed_for": "random matrix theory, Gaussian ensembles, free-probability adaptations",
            "blocks_paradigms": ["P28"],
            "blocks_catalog_entries": "all of Section IX + parts of §VIII",
        },
    ]

    return {
        "lane": "12_catalog_pulled_z_eigenvalue_distribution_probe",
        "catalog_entry": "#66 Z-eigenvalue distribution",
        "section": "VIII. Spectral and Eigenvalue Theory",
        "attack_paradigms": ["P28 (asymptotic spectrum, distributional flavor)"],
        "encoding_attempts": encoding_attempts,
        "tier_B_prediction_test": (
            "DIVERGENCE CONFIRMED. Tier B (ConstructiveExistenceWitness) "
            "does NOT naturally apply to this distributional problem. "
            "This is informative — Tier B's substrate-wide claim is "
            "QUALIFIED to decision-problems-with-individual-witness; not "
            "all 104 catalog entries reduce to it. NEW Tier D "
            "(distributional primitives) emerges."
        ),
        "capability_gaps_identified": capability_gaps_identified,
        "verdict": "DIVERGENCE_FINDING — Tier B doesn't apply; new Tier D (distributional primitives) emerges",
        "feeds_techne_ticket": "T-2026-05-08-T038 + supplements ST-fire41-002 strategic ticket with qualified Tier-B scope",
        "tier_summary_after_5_fires": (
            "Tier A (TensorAlgebra subsystem foundational objects): "
            "TensorObject + TensorNetworkGraph + GroupAction + SchemeObject "
            "(fires #38/#39/#40/#41)\n"
            "\n"
            "Tier B (ConstructiveExistenceWitness — substrate-wide for "
            "DECISION PROBLEMS WITH INDIVIDUAL WITNESS — qualified by "
            "fire #42 divergence): RankDecompositionWitness + "
            "ContractionOrderWitness + IsomorphismCertificate + "
            "LimitWitness/BorderRankWitness\n"
            "\n"
            "Tier C (discrete-optimization geometry): MomentPolytope + "
            "RewriteSearchTree + OrbitStratification\n"
            "\n"
            "Tier D (distributional / population-level — NEW from fire "
            "#42): DistributionObject + StatisticalTestSpec + "
            "ProbabilityMeasure/RandomVariable\n"
            "\n"
            "Five fires now produce a 4-tier substrate-extension proposal. "
            "Tier B's QUALIFIED scope (decision-problems-with-witness, "
            "not literally all 104 entries) is the most important "
            "substrate-tester finding from fire #42 — it's a CALIBRATION "
            "of the Tier-B claim, not a refutation."
        ),
    }


# ---------------------------------------------------------------------------
# Lane 9 — sigma_kernel test suite full sweep
# ---------------------------------------------------------------------------


def lane_9_sigma_kernel_full_sweep() -> Dict[str, Any]:
    # NOTE: must use `python -m pytest` rather than bare `pytest`. Three
    # test files (test_frozen_invariance.py + 2 mini-window-era tests)
    # have `import sigma_kernel` at module top — bare pytest can't put
    # the repo root on sys.path early enough; `python -m pytest` does.
    # File this as P3 infra ticket if convenient.
    import sys as _sys
    cmd = [
        _sys.executable, "-m", "pytest", "sigma_kernel/tests/", "-q",
        "--no-header",
    ]
    proc = subprocess.run(
        cmd, cwd=str(REPO), capture_output=True, text=True, timeout=600,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    stdout_tail = "\n".join(proc.stdout.splitlines()[-15:])
    return {
        "lane": "9_sigma_kernel_full_sweep",
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "stdout_tail": stdout_tail,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 42,
        "posture": "fifth-HARD-6-fire (matrix-filling: §VIII catalog entry #66; DELIBERATE DIVERGENCE TEST of Tier B)",
        "lanes": [12, 9],
        "lane_12": lane_12_z_eigenvalue_distribution_probe(),
        "lane_9": lane_9_sigma_kernel_full_sweep(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_42_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: catalog #66 verdict = {summary['lane_12']['verdict'][:70]}...")
    print(f"  capability gaps: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"  tier_B_prediction_test: {summary['lane_12']['tier_B_prediction_test'][:60]}...")
    print(f"Lane 9: {summary['lane_9']['verdict']} ({summary['lane_9']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
