"""Substrate-Tester Fire #52 harness — §VI matrix-filling + Lane 16 on exclusion_certificate.

Lane 12 — pulled catalog entry #43 (Existence of best rank-r tensor
approximations; §VI Numerical Tensor Decomposition). Tests how the
5-tier model handles ILL-POSEDNESS — best rank-r approximation may
not exist (de Silva-Lim 2008). Different from existence-by-witness
(Tier B) and from threshold scaling (Tier D).

Lane 16 — mutation-testing on sigma_kernel/exclusion_certificate.py
(last audited fire #15). Maintenance + finding-surfacing.

Outputs:
  charon/diagnostics/substrate_tester_fire_52_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_12_ill_posed_approximation_probe() -> Dict[str, Any]:
    """Probe of catalog entry #43 — best rank-r tensor approximation
    may not exist. Tests how 5-tier model handles ill-posedness."""

    # de Silva-Lim 2008 example: 2x2x2 tensor T = e_1 (x) e_1 (x) e_2
    # + e_1 (x) e_2 (x) e_1 + e_2 (x) e_1 (x) e_1 (the W tensor, rank 3).
    # Has border rank 2 but rank 3. The optimization problem
    # "find best rank-2 approximation to T in Frobenius norm" has NO
    # MINIMIZER — the infimum is approached by sequences but never
    # attained. The set of rank-r tensors is not closed.

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode the optimization problem as a Tier B + D claim
    encoding_attempts.append({
        "probe": "encode_best_rank_r_optimization_as_Tier_B_or_D",
        "attempt": (
            "Tier B / D approach: 'there exists a rank-r approximation "
            "achieving error E' (Tier B) + 'as r varies, the achievable-"
            "error curve has a phase transition' (Tier D). For ill-posed "
            "instances, the infimum E* is approached but never attained — "
            "no Tier-B existential witness exists at E = E*."
        ),
        "blocker": (
            "Substrate's existing Tier-B ConstructiveExistenceWitness "
            "design assumes existence ATTAINED at the claimed bound. "
            "For ill-posed problems, only approximate witnesses exist "
            "(error <= E* + epsilon for arbitrarily small epsilon, but "
            "no witness for error = E*). Tier B needs a refinement: "
            "INFIMAL WITNESS subtype that carries epsilon-approximate "
            "existence + 'limit-not-attained' annotation."
        ),
        "verdict": "TIER_B_REFINEMENT — InfimalWitness subtype needed",
    })

    # Probe 2: encode ill-posedness using border-rank closure
    encoding_attempts.append({
        "probe": "encode_via_border_rank_closure_Tier_A",
        "attempt": (
            "Substitute border rank for rank: use TensorObject + "
            "SchemeObject (Tier A; sigma_r is an algebraic variety, "
            "the closure of rank-r tensors). Best border-rank-r "
            "approximation IS well-posed (sigma_r is closed in projective "
            "topology). LimitWitness (Tier B subtype #4 from fire #41) "
            "captures the degeneration sequence."
        ),
        "tier_fit": (
            "FITS — the standard remediation IS to use border rank, and "
            "Tier A's SchemeObject + Tier B's LimitWitness already cover "
            "this. The substrate handles ill-posed rank-r approximation "
            "by REDIRECTING to well-posed border-rank-r approximation. "
            "Existing primitives suffice; refinement is a USAGE PATTERN "
            "not a new primitive."
        ),
        "verdict": "TIER_A_TIER_B_FITS — standard border-rank substitution covers",
    })

    # Probe 3: encode ill-posedness as a Tier-D classification
    encoding_attempts.append({
        "probe": "encode_ill_posed_class_as_Tier_D",
        "attempt": (
            "Tier D distributional: 'almost no tensors of order >=3 are "
            "ill-posed for rank-r approximation; the ill-posed locus is "
            "measure-zero in tensor space.' GenericityAlmostEverywhereCert "
            "(fire #45 refinement) carries the claim."
        ),
        "tier_D_fit": (
            "FITS — generic well-posedness claims fit Tier D's "
            "GenericityAlmostEverywhereCert specialization. The ill-posed "
            "set has measure zero (de Silva-Lim) but contains "
            "specific concrete instances (the W tensor). Substrate "
            "handles this with the existing exception-annotation in "
            "GenericityAlmostEverywhereCert."
        ),
        "verdict": "TIER_D_FITS — GenericityAlmostEverywhereCert covers ill-posed locus",
    })

    capability_gaps_identified = [
        {
            "primitive": "InfimalWitness (Tier B subtype #8 — refinement)",
            "purpose": "epsilon-approximate existence with 'limit-not-attained' annotation; the right shape for ill-posed optimization claims",
            "needed_for": "best rank-r tensor approximation (#43), ill-posed inverse problems generally, infimum-not-min claims in algebraic geometry",
            "tier_classification": "Refinement of Tier B; brings subtypes to 8",
            "alternative": "could be a flag on existing RankDecompositionWitness (closed_attained: bool) rather than separate subtype — design call",
        },
    ]

    return {
        "lane": "12_catalog_pulled_ill_posed_approximation_probe",
        "catalog_entry": "#43 Existence of best rank-r tensor approximations",
        "section": "VI. Numerical Tensor Decomposition and Approximation",
        "encoding_attempts": encoding_attempts,
        "verdict": "5_TIER_MODEL_HOLDS_WITH_REFINEMENT — InfimalWitness as Tier B subtype #8 OR flag on existing",
        "capability_gaps_identified": capability_gaps_identified,
        "saturation_note": (
            "THIRD independent saturation confirmation (fires #45 + #49 "
            "were 1st and 2nd). §VI numerical decomposition fits cleanly "
            "into 5-tier model; ill-posedness handled by Tier-A border-"
            "rank substitution + Tier-B LimitWitness + Tier-D "
            "GenericityAlmostEverywhereCert + new InfimalWitness "
            "refinement. No new tier."
        ),
    }


def lane_16_mutation_testing_exclusion_certificate() -> Dict[str, Any]:
    """Mutation-test sigma_kernel/exclusion_certificate.py against the
    relevant test suite. Last audited fire #15."""
    import sys as _sys
    target = "sigma_kernel/exclusion_certificate.py"
    test_cmd = (
        f'"{_sys.executable}" -m pytest '
        f'sigma_kernel/tests/test_frozen_invariance.py '
        f'sigma_kernel/tests/test_frozen_baseline_manifest.py '
        f'sigma_kernel/tests/test_enum_validation_2026_05_08.py '
        f'sigma_kernel/tests/test_claim_kill_path_typing_2026_05_08.py '
        f'-q --no-header -x'
    )
    cmd = [
        _sys.executable, "-m", "prometheus_math.mutation_testing",
        "--target", target,
        "--test-cmd", test_cmd,
        "--max-mutations", "10",
        "--timeout", "120",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=900)

    counts = {"killed": 0, "survived": 0, "errored": 0}
    score: float = -1.0
    summary_lines: List[str] = []
    for line in proc.stdout.splitlines():
        s = line.strip()
        if s.startswith("[mutation"):
            summary_lines.append(s)
            for k in counts:
                if f" {k}=" in s:
                    try:
                        counts[k] = int(s.split(f" {k}=")[1].split()[0])
                    except (ValueError, IndexError):
                        pass
            if "score=" in s:
                try:
                    score = float(s.split("score=")[1].split()[0])
                except (ValueError, IndexError):
                    pass

    return {
        "lane": "16_mutation_testing_exclusion_certificate",
        "target": target,
        "max_mutations": 10,
        "returncode": proc.returncode,
        "summary_lines": summary_lines[-12:],
        "kill_counts": counts,
        "score": score,
        "verdict": "INFORMATIVE" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 52,
        "posture": "lower-cadence: §VI matrix-filling + Lane 16 mutation-testing on exclusion_certificate",
        "lanes": [12, 16],
        "lane_12": lane_12_ill_posed_approximation_probe(),
        "lane_16": lane_16_mutation_testing_exclusion_certificate(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_52_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12 verdict: {summary['lane_12']['verdict'][:70]}")
    print(f"Lane 16 verdict: {summary['lane_16']['verdict']} | counts: {summary['lane_16']['kill_counts']} | score: {summary['lane_16']['score']:.3f}")
    return summary


if __name__ == "__main__":
    run()
