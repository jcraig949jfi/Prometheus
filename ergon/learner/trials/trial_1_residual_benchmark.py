"""Trial 1 — Adversarial Residual Benchmark.

Per pivot/ergon_learner_proposal_v8.md S4:

Goal: Is the residual classifier accurate enough to serve as reward signal?

Implementation:
- 200 curated samples: 50 obvious noise + 50 borderline signal + 100 synthetic structured-noise
- Run sigma_kernel.residuals._classify_residual on all 200
- Report: overall accuracy, FP rate on synthetic structured-noise, ECE across 5 confidence bins

Acceptance:
- >=85% overall accuracy
- <=5% FP on synthetic structured-noise (target <=2% for full w_R activation)
- ECE <=0.05

w_R activation tier (per v6 confidence-tiered specification):
- Observed FP <=2% (95% upper CI <=4.7%): w_R = 0.15 (full)
- 3-5 (CI <=9.4%): w_R = 0.075 (half)
- 6-10: w_R = 0 (escrow - diagnostics only)
- >10: w_R = 0 (deep escrow - retrain or replace classifier)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np


SampleClass = Literal["obvious_noise", "borderline_signal", "synthetic_structured_noise"]
TrueLabel = Literal["noise", "signal", "instrument_drift"]


@dataclass(frozen=True)
class BenchmarkSample:
    """One curated sample for the adversarial residual benchmark.

    Each sample carries the failure_shape that would be passed to the
    residual classifier (sigma_kernel.residuals._classify_residual), plus
    the ground-truth label and the sample-class category that determines
    which curation pass it belonged to.

    The ground-truth label answers "what should the classifier ideally
    return?" The sample_class answers "which curation pass produced
    this?" These are different — a borderline_signal sample's true label
    is "signal" but the sample is curated to be statistically near the
    decision boundary; the classifier may easily misclassify it.
    """

    sample_id: str
    sample_class: SampleClass
    true_label: TrueLabel
    failure_shape: Dict[str, Any]
    rationale: str  # one-sentence justification of the true_label


# ---------------------------------------------------------------------------
# Pass A: obvious noise (50 samples)
# ---------------------------------------------------------------------------
#
# These samples should be classified as "noise" by any competent residual
# classifier. They span: FP-quantization residuals, MC-seed jitter,
# noise-floor Gaussian residuals, uniform-distribution residuals from
# random polynomial draws, and empty/zero residuals.
#
# Curated mostly programmatically — these are statistical samples, not
# domain-curated. Reproducibility via seed.

def generate_obvious_noise_samples(seed: int = 0) -> List[BenchmarkSample]:
    """Generate the 50 obvious-noise samples (deterministic given seed)."""
    rng = np.random.default_rng(seed)
    out: List[BenchmarkSample] = []

    # Sub-class A1: FP-quantization residuals (10 samples)
    # Failure shape mimics floating-point rounding artifacts at IEEE-754
    # 64-bit boundary; coefficient variance is at the noise floor (~1e-16).
    for i in range(10):
        out.append(BenchmarkSample(
            sample_id=f"A1_fp_quant_{i:02d}",
            sample_class="obvious_noise",
            true_label="noise",
            failure_shape={
                "kind": "fp_quantization",
                "coeff_variance": float(rng.uniform(1e-17, 1e-15)),
                "magnitude_log10": float(rng.uniform(-16, -14)),
                "canonicalizer_subclass": None,
            },
            rationale="FP-quantization noise at IEEE-754 boundary; no structural signature",
        ))

    # Sub-class A2: MC-seed jitter residuals (10 samples)
    # Failure shape mimics Monte-Carlo seed-to-seed variance at expected
    # statistical floor; non-trivial coefficient variance but no
    # canonicalizer fingerprint.
    for i in range(10):
        out.append(BenchmarkSample(
            sample_id=f"A2_mc_seed_jitter_{i:02d}",
            sample_class="obvious_noise",
            true_label="noise",
            failure_shape={
                "kind": "mc_seed_jitter",
                "coeff_variance": float(rng.uniform(0.01, 0.05)),
                "magnitude_log10": float(rng.uniform(-3, -1)),
                "canonicalizer_subclass": None,
                "n_seeds_sampled": int(rng.integers(50, 500)),
            },
            rationale="MC-seed-to-seed variance at expected statistical floor",
        ))

    # Sub-class A3: Gaussian residuals at noise-floor magnitude (10 samples)
    for i in range(10):
        out.append(BenchmarkSample(
            sample_id=f"A3_gaussian_noise_floor_{i:02d}",
            sample_class="obvious_noise",
            true_label="noise",
            failure_shape={
                "kind": "gaussian_noise_floor",
                "coeff_variance": float(rng.uniform(0.001, 0.01)),
                "magnitude_log10": float(rng.uniform(-5, -3)),
                "canonicalizer_subclass": None,
                "skewness": float(rng.normal(0, 0.1)),
                "kurtosis": float(rng.normal(3, 0.5)),
            },
            rationale="Gaussian residual at noise floor; consistent with pure measurement noise",
        ))

    # Sub-class A4: Uniform-distribution residuals from random polynomial draws (10 samples)
    for i in range(10):
        out.append(BenchmarkSample(
            sample_id=f"A4_uniform_random_poly_{i:02d}",
            sample_class="obvious_noise",
            true_label="noise",
            failure_shape={
                "kind": "uniform_random_poly",
                "coeff_variance": float(rng.uniform(0.1, 0.3)),
                "magnitude_log10": float(rng.uniform(0, 2)),
                "canonicalizer_subclass": None,
                "poly_degree": int(rng.integers(3, 12)),
                "n_distinct_factors": int(rng.integers(1, 4)),
            },
            rationale="Random polynomial residual; no structural pattern beyond uniform draws",
        ))

    # Sub-class A5: empty / zero residuals (10 samples)
    for i in range(10):
        out.append(BenchmarkSample(
            sample_id=f"A5_empty_zero_{i:02d}",
            sample_class="obvious_noise",
            true_label="noise",
            failure_shape={
                "kind": "empty_zero",
                "coeff_variance": 0.0,
                "magnitude_log10": float("-inf") if i % 2 == 0 else float(rng.uniform(-20, -18)),
                "canonicalizer_subclass": None,
            },
            rationale="Empty or near-zero residual; classifier should return noise via empty/zero rule",
        ))

    return out


# ---------------------------------------------------------------------------
# Pass B: borderline signal (50 samples) — domain-curated from mathematical history
# ---------------------------------------------------------------------------
#
# These samples carry true_label="signal" but the failure_shape is at the
# classifier's decision boundary. A conservative classifier may misclassify
# these as noise; that's an acceptable failure mode (over-rejection of
# marginal signal) per v8 Trial 1 acceptance criterion (FP on synthetic
# structured-noise is the load-bearing constraint).
#
# Curated from real mathematical history; each sample carries a citation.

BORDERLINE_SIGNAL_SAMPLES_RAW: List[Tuple[str, str, Dict[str, Any], str]] = [
    # Mercury perihelion residual at low-confidence regime (5 samples)
    # The 43-arcsecond/century anomaly was at ~3-sigma for early
    # measurements; later refinement made it 5-sigma. Borderline-signal
    # samples here mimic the early-measurement regime.
    (
        "B1_mercury_perihelion_low_conf_01",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.78,  # > 0.5 threshold in classifier
            "magnitude_log10": 1.6,  # ~43 arcsec/century
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_pre_GR_residual",
            "confidence_sigma": 2.8,  # borderline
        },
        "Mercury perihelion residual at pre-GR low-confidence regime; ~3-sigma deviation",
    ),
    (
        "B1_mercury_perihelion_low_conf_02",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.72,
            "magnitude_log10": 1.55,
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_alternate_regime",
            "confidence_sigma": 2.5,
        },
        "Mercury perihelion residual under alternate measurement regime; near classifier boundary",
    ),
    # ... (additional 48 borderline_signal samples to be curated)
    # For Day 1 of Trial 1, this initial 2 are the seed. Pass B continues
    # on Day 2 with full 50-sample curation (Mercury perihelion 5,
    # Ramanujan-Hardy 5, Riemann Li(x)-pi(x) 5, calibration drift 15,
    # BSD-conditional 10, modular-form coefficient 10).
]


def generate_borderline_signal_samples_seed() -> List[BenchmarkSample]:
    """Day 1 seed of the borderline_signal pass. Full curation continues on Day 2."""
    out: List[BenchmarkSample] = []
    for sample_id, true_label, failure_shape, rationale in BORDERLINE_SIGNAL_SAMPLES_RAW:
        out.append(BenchmarkSample(
            sample_id=sample_id,
            sample_class="borderline_signal",
            true_label=true_label,
            failure_shape=failure_shape,
            rationale=rationale,
        ))
    return out


# ---------------------------------------------------------------------------
# Pass C: synthetic structured-noise (100 samples) — adversarial
# ---------------------------------------------------------------------------
#
# These are deliberately constructed to LOOK like signal but be UNCORRELATED
# with truth. The load-bearing constraint of Trial 1 is FP rate on these
# samples; they're the residual-gaming attractor's training set in
# adversarial form.
#
# Curation method: programmatic generation with structural features that
# match signal-class triggers (high coefficient variance, canonicalizer-
# subclass fingerprints, structured magnitude distributions) but with no
# true mathematical content.

def generate_synthetic_structured_noise_samples(seed: int = 1) -> List[BenchmarkSample]:
    """Generate the 100 synthetic structured-noise samples (deterministic given seed).

    These are the load-bearing test of classifier robustness. A classifier
    that mistakes synthetic structured-noise for signal at >5% rate enables
    the residual-gaming attractor.
    """
    rng = np.random.default_rng(seed)
    out: List[BenchmarkSample] = []

    # Sub-class C1: high-coefficient-variance residuals from random polynomial draws (30 samples)
    # Coefficient variance >0.5 (the classifier's signal threshold) but
    # generated from random polynomials with no structural content.
    for i in range(30):
        out.append(BenchmarkSample(
            sample_id=f"C1_high_var_random_{i:02d}",
            sample_class="synthetic_structured_noise",
            true_label="noise",  # GROUND TRUTH: noise; classifier may say signal incorrectly
            failure_shape={
                "kind": "synthetic_high_variance",
                "coeff_variance": float(rng.uniform(0.6, 1.5)),  # ABOVE classifier threshold
                "magnitude_log10": float(rng.uniform(0, 4)),
                "canonicalizer_subclass": None,  # no real subclass match
                "n_distinct_factors": int(rng.integers(2, 6)),
                "poly_degree": int(rng.integers(5, 15)),
            },
            rationale="High-variance random polynomial; coefficient variance triggers classifier but no real signal",
        ))

    # Sub-class C2: canonicalizer-subclass-matching residuals built from random hash collisions (30 samples)
    # These have subclass tags assigned via random hash collision rather
    # than real structural matching; classifier may treat them as signal.
    for i in range(30):
        subclass = rng.choice(
            ["group_quotient", "partition_refinement", "ideal_reduction", "variety_fingerprint"]
        )
        out.append(BenchmarkSample(
            sample_id=f"C2_subclass_collision_{i:02d}",
            sample_class="synthetic_structured_noise",
            true_label="noise",
            failure_shape={
                "kind": "synthetic_subclass_collision",
                "coeff_variance": float(rng.uniform(0.05, 0.4)),  # below threshold
                "magnitude_log10": float(rng.uniform(-2, 3)),
                "canonicalizer_subclass": subclass,  # MATCHES classifier subclass rule
                "subclass_provenance": "hash_collision_random_assignment",
            },
            rationale="Subclass tag from hash collision, not real structural matching",
        ))

    # Sub-class C3: fake-drift fingerprints from time-correlated noise (20 samples)
    # These look like instrument-drift to the classifier but are pure
    # autocorrelated noise with no calibration-anchor connection.
    for i in range(20):
        out.append(BenchmarkSample(
            sample_id=f"C3_fake_drift_{i:02d}",
            sample_class="synthetic_structured_noise",
            true_label="noise",
            failure_shape={
                "kind": "synthetic_fake_drift",
                "coeff_variance": float(rng.uniform(0.1, 0.3)),
                "magnitude_log10": float(rng.uniform(-3, 1)),
                "canonicalizer_subclass": None,
                "drift_fingerprint": "autocorrelated_noise_t10",  # looks like drift to classifier
                "calibration_anchor_correlations": 0,  # but no real anchor connection
            },
            rationale="Time-correlated noise resembling instrument drift; no calibration-anchor signal",
        ))

    # Sub-class C4: cyclotomic-near-miss residuals (20 samples)
    # Polynomials with M (Mahler measure) close to 1 (cyclotomic
    # boundary) but not exactly cyclotomic. Could trigger classifier's
    # variety_fingerprint subclass but are computational artifacts of
    # polynomials near the cyclotomic manifold.
    for i in range(20):
        out.append(BenchmarkSample(
            sample_id=f"C4_cyclotomic_near_miss_{i:02d}",
            sample_class="synthetic_structured_noise",
            true_label="noise",
            failure_shape={
                "kind": "synthetic_cyclotomic_near_miss",
                "coeff_variance": float(rng.uniform(0.5, 0.8)),  # above threshold
                "magnitude_log10": float(rng.uniform(0.0, 0.05)),  # M near 1
                "canonicalizer_subclass": "variety_fingerprint",
                "mahler_measure_distance_from_unity": float(rng.uniform(1e-6, 1e-3)),
                "poly_irreducible": False,  # reducible — disqualifies as Salem candidate
            },
            rationale="Polynomial near cyclotomic manifold; reducible; computational artifact rather than discovery",
        ))

    return out


# ---------------------------------------------------------------------------
# Top-level benchmark assembly
# ---------------------------------------------------------------------------


def assemble_benchmark(
    seed_obvious: int = 0,
    seed_synthetic: int = 1,
    include_borderline_seed: bool = True,
) -> List[BenchmarkSample]:
    """Assemble the 200-sample benchmark.

    Day 1 produces full obvious_noise + synthetic_structured_noise + a 2-sample
    borderline_signal seed. Day 2 of Trial 1 fills out the remaining 48
    borderline_signal samples by domain curation.
    """
    out: List[BenchmarkSample] = []
    out.extend(generate_obvious_noise_samples(seed=seed_obvious))
    if include_borderline_seed:
        out.extend(generate_borderline_signal_samples_seed())
    out.extend(generate_synthetic_structured_noise_samples(seed=seed_synthetic))
    return out


def serialize_benchmark(samples: List[BenchmarkSample], path: Path) -> None:
    """Serialize benchmark to JSON for reproducibility and checkpoint."""
    data = [asdict(s) for s in samples]
    # Replace -inf with sentinel for JSON
    for entry in data:
        for k, v in entry["failure_shape"].items():
            if isinstance(v, float) and (v == float("-inf") or v == float("inf")):
                entry["failure_shape"][k] = None  # encode sentinel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    benchmark = assemble_benchmark()
    print(f"Day 1 benchmark seed: {len(benchmark)} samples")
    print(f"  obvious_noise: {sum(1 for s in benchmark if s.sample_class == 'obvious_noise')}")
    print(f"  borderline_signal (seed): {sum(1 for s in benchmark if s.sample_class == 'borderline_signal')}")
    print(f"  synthetic_structured_noise: {sum(1 for s in benchmark if s.sample_class == 'synthetic_structured_noise')}")

    out_path = Path(__file__).parent / "trial_1_benchmark_day1_seed.json"
    serialize_benchmark(benchmark, out_path)
    print(f"\nSerialized to: {out_path}")
    print("\nDay 2: fill out 48 more borderline_signal samples (Mercury perihelion 5,")
    print("Ramanujan-Hardy 5, Riemann Li-pi 5, calibration drift 15, BSD-conditional 10,")
    print("modular-form coefficient 10) by domain curation.")
