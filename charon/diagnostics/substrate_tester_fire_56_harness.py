"""Substrate-Tester Fire #56 harness — §II Rank Zoo matrix-filling + regression.

Lane 12 — pulled catalog entry #16 (Subrank-rank duality / asymptotic
spectrum description; §II Rank Zoo). Strassen's asymptotic spectrum
of complex tensors: explicit description of all monotone semiring
homomorphisms. Currently known points: matrix flattenings, support
functionals, Razborov rank functions, slice rank, quantum functionals.

Tests whether 5-tier model handles abstract algebraic objects
(monotones, semiring homomorphisms, spectrum points) that don't reduce
to individual tensor instances or distributional populations. If even
this fits, saturation is overdetermined.

Lane 11 — canon-fuzz pytest fresh seed 20260509_01.

Outputs:
  charon/diagnostics/substrate_tester_fire_56_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_12_asymptotic_spectrum_probe() -> Dict[str, Any]:
    """Probe of catalog entry #16 — explicit description of Strassen's
    asymptotic spectrum monotones. Most abstract entry pulled to date."""

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode a single asymptotic-spectrum monotone
    encoding_attempts.append({
        "probe": "encode_single_monotone",
        "attempt": (
            "A monotone is a function phi: T -> R+ that respects the "
            "asymptotic spectrum's restriction preorder T <= S => "
            "phi(T) <= phi(S), is multiplicative under tensor product "
            "phi(T (x) S) = phi(T) * phi(S), and additive under direct "
            "sum phi(T (+) S) = phi(T) + phi(S). Could encode as a "
            "MethodSpec (engine='compute_monotone', strategy='quantum_"
            "functional') with the function as substrate-grade callable."
        ),
        "tier_classification": (
            "MIXED — MethodSpec covers the COMPUTATION (call the "
            "monotone on a tensor) but loses the ALGEBRAIC PROPERTIES "
            "(monotonicity / multiplicativity / additivity). Substrate "
            "treats it as a black-box callable; can't verify or "
            "exploit the semiring-homomorphism structure. Tier-A "
            "refinement: SemiringHomomorphism / MonotoneFunctional as "
            "a property-carrying primitive."
        ),
        "verdict": "TIER_A_REFINEMENT — SemiringHomomorphism primitive needed",
    })

    # Probe 2: encode the asymptotic spectrum itself as a substrate object
    encoding_attempts.append({
        "probe": "encode_asymptotic_spectrum_as_object",
        "attempt": (
            "Strassen's asymptotic spectrum is a TOPOLOGICAL SPACE "
            "(specifically a compact convex subset of R^N for N = "
            "number of monotones) of which each known point is a "
            "specific monotone. The spectrum itself is a substrate-"
            "grade object — could it be a CoordinateChart over a "
            "domain='asymptotic_spectrum'?"
        ),
        "tier_classification": (
            "PARTIAL — CoordinateChart can register the spectrum as a "
            "named region with axes='monotones'. But the spectrum's "
            "convex-geometric structure (extreme points, supporting "
            "hyperplanes, faces) needs Tier C MomentPolytope-like "
            "primitives. The spectrum's POINTS are a different shape "
            "from the spectrum's CONVEX GEOMETRY. Two-tier composition: "
            "Tier A (CoordinateChart for the spectrum) + Tier C "
            "(MomentPolytope for the convex structure)."
        ),
        "verdict": "TIER_A_TIER_C_COMPOSITION — existing primitives compose",
    })

    # Probe 3: encode the OPEN problem (find all monotones)
    encoding_attempts.append({
        "probe": "encode_complete_classification_claim",
        "attempt": (
            "The OPEN problem: 'the known monotones (matrix flattenings, "
            "support functionals, Razborov, slice rank, quantum "
            "functionals) constitute the COMPLETE list.' Equivalently: "
            "no new monotone can be constructed. This is a Tier-B-style "
            "negative existential ('no further monotone exists'). "
            "Substrate's ExclusionCertificate covers."
        ),
        "tier_B_fit": (
            "FITS — the classification claim's negative direction is a "
            "natural ExclusionCertificate. The positive direction "
            "(constructing a NEW monotone) would be Tier-B "
            "ConstructiveExistenceWitness with a witness type = "
            "FunctionalWitness (a callable + monotonicity proof + "
            "multiplicativity proof + additivity proof). "
            "Same asymmetric-existential pattern as fires #38-#41 + "
            "#45."
        ),
        "verdict": "TIER_B_FITS — same asymmetric-existential pattern; FunctionalWitness as new subtype",
    })

    # Probe 4: encode the goal (closing the omega-2 implication chain)
    encoding_attempts.append({
        "probe": "encode_omega_2_implication_chain",
        "attempt": (
            "If the asymptotic spectrum is fully characterized AND the "
            "subrank/rank gap closes for matrix-mult tensor M<n>, then "
            "omega = 2. This is a CHAIN OF IMPLICATIONS across multiple "
            "substrate claims. Could be encoded via REWRITE/EQUIV "
            "opcodes (claim A & claim B => claim C)."
        ),
        "tier_existing_fit": (
            "FITS — REWRITE/EQUIV (existing kernel opcodes) handle "
            "implication chains. Tier B subtypes act as the witness "
            "leaves; REWRITE chains them into a TheoremGraph "
            "(implicit, not as a new primitive). Substrate already "
            "supports this composition."
        ),
        "verdict": "EXISTING_OPCODES_FIT — REWRITE/EQUIV handle implication chain",
    })

    capability_gaps_identified = [
        {
            "primitive": "SemiringHomomorphism / MonotoneFunctional (Tier A refinement)",
            "purpose": "carry algebraic properties (monotonicity, multiplicativity, additivity) of substrate-grade callables; verifiable not just runnable",
            "needed_for": "Strassen's asymptotic spectrum (#16), quantum functionals (#17), semiring-homomorphism arguments across §II",
            "tier_classification": "Refinement of MethodSpec/Tier A; could be specialization or wrapper",
        },
        {
            "primitive": "FunctionalWitness (Tier B subtype #9)",
            "purpose": "constructive witness for 'this callable is a valid monotone' — function value + monotonicity proof + multiplicativity proof + additivity proof",
            "needed_for": "Strassen's monotone classification (#16), border-apolarity functional certificates (§I), spectral functionals (§VIII)",
            "tier_classification": "Specialization of ConstructiveExistenceWitness; brings Tier B subtypes to 9 (after fire #52's InfimalWitness #8)",
        },
    ]

    return {
        "lane": "12_catalog_pulled_asymptotic_spectrum_probe",
        "catalog_entry": "#16 Subrank-rank duality / asymptotic spectrum description",
        "section": "II. The Rank Zoo: Alternative Rank Notions",
        "encoding_attempts": encoding_attempts,
        "verdict": "5_TIER_MODEL_HOLDS — refinements only; saturation overdetermined",
        "capability_gaps_identified": capability_gaps_identified,
        "saturation_note": (
            "FOURTH independent saturation confirmation (after fires #45 "
            "+ #49 + #52). §II Rank Zoo's most abstract entry — "
            "Strassen's asymptotic spectrum, monotone classification — "
            "fits via Tier A refinement (SemiringHomomorphism), Tier B "
            "subtype #9 (FunctionalWitness), and existing REWRITE/EQUIV "
            "for implication chains. No new tier; no new structural "
            "family. Saturation is now overdetermined."
        ),
        "tier_summary_after_10_post_pivot_fires": (
            "Tier A: 4 primitives + 2 refinements (SymmetricTensor #49, "
            "SemiringHomomorphism #56)\n"
            "Tier B: 9 subtypes (added FunctionalWitness #56) + cross-"
            "tier composition with Tier D\n"
            "Tier C: 3 primitives\n"
            "Tier D: 5 primitives + 1 specialization\n"
            "Tier E: 3 primitives\n"
            "\n"
            "Post-pivot matrix-filling at lower cadence has produced "
            "only refinements (no new tiers) since fire #45. The 5-tier "
            "model is doctrinally robust."
        ),
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260509_01"
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
        "lane": "11_canon_fuzz_smoke", "seed": seed,
        "returncode": proc.returncode, "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 56,
        "posture": "lower-cadence: §II Rank Zoo matrix-filling + canon-fuzz regression",
        "lanes": [12, 11],
        "lane_12": lane_12_asymptotic_spectrum_probe(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_56_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12 verdict: {summary['lane_12']['verdict']}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
