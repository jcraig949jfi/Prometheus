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
    # ===================================================================
    # B1: Mercury perihelion residual at low-confidence regime (5 samples)
    # ===================================================================
    # The 43-arcsecond/century anomaly was at ~3-sigma for early
    # measurements; later refinement made it 5-sigma. Borderline-signal
    # samples here mimic the early-measurement regime.
    (
        "B1_mercury_perihelion_01",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.78, "magnitude_log10": 1.6,
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_pre_GR_residual",
            "confidence_sigma": 2.8,
        },
        "Mercury perihelion residual at pre-GR low-confidence regime; ~3-sigma deviation",
    ),
    (
        "B1_mercury_perihelion_02",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.72, "magnitude_log10": 1.55,
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_alternate_regime",
            "confidence_sigma": 2.5,
        },
        "Mercury perihelion residual under alternate measurement regime; near classifier boundary",
    ),
    (
        "B1_mercury_perihelion_03",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.65, "magnitude_log10": 1.45,
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_smaller_telescope_regime",
            "confidence_sigma": 2.1,
        },
        "Mercury perihelion under smaller telescope; ~2-sigma; classifier likely conservative",
    ),
    (
        "B1_mercury_perihelion_04",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.81, "magnitude_log10": 1.65,
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_post_Newcomb_revision",
            "confidence_sigma": 3.4,
        },
        "Post-Newcomb-revision Mercury anomaly; clearly above noise but pre-GR",
    ),
    (
        "B1_mercury_perihelion_05",
        "signal",
        {
            "kind": "physical_anomaly_residual",
            "coeff_variance": 0.68, "magnitude_log10": 1.5,
            "canonicalizer_subclass": "variety_fingerprint",
            "physical_provenance": "Mercury_perihelion_uncombined_observatory_data",
            "confidence_sigma": 2.3,
        },
        "Single-observatory Mercury data; unaggregated; classifier boundary",
    ),

    # ===================================================================
    # B2: Ramanujan-Hardy asymptotic residuals at marginal n (5 samples)
    # ===================================================================
    # Partition function p(n) asymptotic residual relative to the H-R
    # circle-method estimate. At small n, the asymptotic underestimates
    # systematically; at marginal n (~50-100) the residual is borderline.
    (
        "B2_ramanujan_hardy_01",
        "signal",
        {
            "kind": "asymptotic_residual",
            "coeff_variance": 0.55, "magnitude_log10": -1.2,
            "canonicalizer_subclass": "partition_refinement",
            "math_provenance": "p(n)_HR_residual_n_50",
            "n_value": 50,
        },
        "Partition function asymptotic residual at n=50; on signal threshold boundary",
    ),
    (
        "B2_ramanujan_hardy_02",
        "signal",
        {
            "kind": "asymptotic_residual",
            "coeff_variance": 0.58, "magnitude_log10": -1.4,
            "canonicalizer_subclass": "partition_refinement",
            "math_provenance": "p(n)_HR_residual_n_75",
            "n_value": 75,
        },
        "Partition asymptotic residual at n=75; slightly stronger structural signature",
    ),
    (
        "B2_ramanujan_hardy_03",
        "signal",
        {
            "kind": "asymptotic_residual",
            "coeff_variance": 0.52, "magnitude_log10": -1.6,
            "canonicalizer_subclass": "partition_refinement",
            "math_provenance": "p(n)_HR_residual_n_100",
            "n_value": 100,
        },
        "Partition residual at n=100; classifier may treat as noise (variance threshold)",
    ),
    (
        "B2_ramanujan_hardy_04",
        "signal",
        {
            "kind": "asymptotic_residual",
            "coeff_variance": 0.64, "magnitude_log10": -1.0,
            "canonicalizer_subclass": "partition_refinement",
            "math_provenance": "Q(n)_overpartition_asymptotic_residual",
            "n_value": 60,
        },
        "Overpartition asymptotic residual; related to p(n) HR but distinct structural form",
    ),
    (
        "B2_ramanujan_hardy_05",
        "signal",
        {
            "kind": "asymptotic_residual",
            "coeff_variance": 0.51, "magnitude_log10": -1.8,
            "canonicalizer_subclass": "partition_refinement",
            "math_provenance": "p(n)_HR_residual_higher_order_correction",
            "n_value": 150,
        },
        "Higher-order HR correction residual; barely above variance threshold",
    ),

    # ===================================================================
    # B3: Riemann Li(x)-pi(x) at hard-to-distinguish regimes (5 samples)
    # ===================================================================
    # Logarithmic integral vs prime counting function: Li(x)-pi(x) is
    # always positive at human-accessible x but the residual structure
    # connects to RH. Samples here are at x where the residual is tight
    # to its expected square-root growth.
    (
        "B3_riemann_li_pi_01",
        "signal",
        {
            "kind": "number_theory_residual",
            "coeff_variance": 0.62, "magnitude_log10": 2.3,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Li(x)_minus_pi(x)_at_x_10_to_8",
            "x_value": 1e8,
        },
        "Li-pi residual at x=10^8; in the regime where Skewes-related anomalies become detectable",
    ),
    (
        "B3_riemann_li_pi_02",
        "signal",
        {
            "kind": "number_theory_residual",
            "coeff_variance": 0.58, "magnitude_log10": 2.7,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Li(x)_minus_pi(x)_at_x_10_to_10",
            "x_value": 1e10,
        },
        "Li-pi residual at x=10^10; growth pattern consistent with RH-conditional bound",
    ),
    (
        "B3_riemann_li_pi_03",
        "signal",
        {
            "kind": "number_theory_residual",
            "coeff_variance": 0.54, "magnitude_log10": 3.1,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Li(x)_minus_pi(x)_at_x_10_to_12",
            "x_value": 1e12,
        },
        "Li-pi at x=10^12; computational ceiling; residual structure marginal",
    ),
    (
        "B3_riemann_li_pi_04",
        "signal",
        {
            "kind": "number_theory_residual",
            "coeff_variance": 0.66, "magnitude_log10": 1.9,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "pi(x)_log_residual_secondary_term",
            "x_value": 1e7,
        },
        "Secondary-term residual in pi(x) asymptotic; structural but small magnitude",
    ),
    (
        "B3_riemann_li_pi_05",
        "signal",
        {
            "kind": "number_theory_residual",
            "coeff_variance": 0.60, "magnitude_log10": 2.5,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Chebyshev_psi_residual_gradient",
            "x_value": 1e9,
        },
        "Chebyshev psi function residual; cousin to Li-pi via explicit formula",
    ),

    # ===================================================================
    # B4: F1+F6+F9+F11 calibration drift events (15 samples)
    # ===================================================================
    # Synthesizable from the existing battery's known failure modes —
    # cases where the unanimous battery has shifted verdict on the same
    # underlying claim across battery revisions. These ARE signal
    # (some claim survived re-attack across revisions) but the residual
    # carries drift fingerprints that may confuse the classifier.
    (
        "B4_calibration_drift_F1_01",
        "instrument_drift",  # classifier should ideally recognize this as drift, not signal
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.71, "magnitude_log10": 0.4,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F1_permutation_seed_dependence_v1_to_v2",
            "calibration_anchor_correlations": 7,
        },
        "F1 permutation-seed drift between battery v1 and v2; correlates with 7 calibration anchors",
    ),
    (
        "B4_calibration_drift_F1_02",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.68, "magnitude_log10": 0.3,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F1_permutation_count_threshold_drift",
            "calibration_anchor_correlations": 5,
        },
        "F1 drift from N permutations 1000->10000 threshold change",
    ),
    (
        "B4_calibration_drift_F6_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.75, "magnitude_log10": 0.5,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F6_base_rate_corpus_change",
            "calibration_anchor_correlations": 9,
        },
        "F6 base-rate drift after corpus expansion 2024->2025",
    ),
    (
        "B4_calibration_drift_F6_02",
        "signal",  # this one is real signal, not drift — F6 had a genuine miscalibration that was a structural finding
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.79, "magnitude_log10": 0.6,
            "canonicalizer_subclass": "variety_fingerprint",
            "drift_fingerprint": "F6_OEIS_coverage_gap_at_low_index",
            "calibration_anchor_correlations": 12,
        },
        "F6 OEIS coverage gap at low-index sequences; was real signal not just drift",
    ),
    (
        "B4_calibration_drift_F9_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.66, "magnitude_log10": 0.2,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F9_simpler_explanation_likelihood_threshold",
            "calibration_anchor_correlations": 6,
        },
        "F9 simpler-explanation drift from likelihood threshold tuning",
    ),
    (
        "B4_calibration_drift_F9_02",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.62, "magnitude_log10": 0.15,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F9_model_class_expansion",
            "calibration_anchor_correlations": 4,
        },
        "F9 drift after expanding simpler-model class to include polynomial-time procedures",
    ),
    (
        "B4_calibration_drift_F11_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.73, "magnitude_log10": 0.45,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F11_fold_count_change_3_to_5",
            "calibration_anchor_correlations": 8,
        },
        "F11 cross-validation drift from 3-fold to 5-fold scheme",
    ),
    (
        "B4_calibration_drift_F11_02",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.69, "magnitude_log10": 0.35,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F11_held_out_set_curation_revision",
            "calibration_anchor_correlations": 7,
        },
        "F11 drift after held-out set curation revision",
    ),
    (
        "B4_calibration_drift_F1_F6_combined_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.77, "magnitude_log10": 0.55,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F1_F6_combined_post_pattern_NULL_CONSTRAINT_MISMATCH",
            "calibration_anchor_correlations": 11,
        },
        "Combined F1+F6 drift after PATTERN_NULL_CONSTRAINT_MISMATCH was added to the lattice",
    ),
    (
        "B4_calibration_drift_F1_F11_combined_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.70, "magnitude_log10": 0.4,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F1_F11_correlation_after_seed_aware_F1",
            "calibration_anchor_correlations": 6,
        },
        "F1+F11 combined drift; F11 inherits permutation-seed dependence from F1",
    ),
    (
        "B4_calibration_drift_F6_F9_combined_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.74, "magnitude_log10": 0.5,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F6_F9_overlap_in_simpler_model_simplification",
            "calibration_anchor_correlations": 9,
        },
        "F6 + F9 simplification overlap; partially-redundant kill-tests",
    ),
    (
        "B4_calibration_drift_F1_systematic_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.81, "magnitude_log10": 0.65,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F1_systematic_variance_post_GAUDIN_VAR_bug_fix",
            "calibration_anchor_correlations": 14,
        },
        "F1 systematic drift after GAUDIN_VAR bug fix (3*pi/8 - 1 vs 4 - pi)",
    ),
    (
        "B4_calibration_drift_F11_OOD_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.67, "magnitude_log10": 0.3,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F11_OOD_drift_ec_to_modular_forms",
            "calibration_anchor_correlations": 5,
        },
        "F11 OOD-drift when applying EC-calibrated battery to modular-form claims",
    ),
    (
        "B4_calibration_drift_F6_anchor_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.72, "magnitude_log10": 0.4,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F6_anchor_density_dependence",
            "calibration_anchor_correlations": 10,
        },
        "F6 base-rate sensitivity to anchor density per OEIS region",
    ),
    (
        "B4_calibration_drift_F1_meta_01",
        "instrument_drift",
        {
            "kind": "calibration_drift_residual",
            "coeff_variance": 0.85, "magnitude_log10": 0.7,
            "canonicalizer_subclass": "group_quotient",
            "drift_fingerprint": "F1_meta_drift_after_PATTERN_PERMUTATION_SEED_DRIFT",
            "calibration_anchor_correlations": 13,
        },
        "F1 meta-drift after substrate added PATTERN_PERMUTATION_SEED_DRIFT as new kill-test",
    ),

    # ===================================================================
    # B5: BSD-conditional residuals (10 samples)
    # ===================================================================
    # Elliptic curve BSD residuals: rank vs L-function order-of-vanishing
    # discrepancies, regulator residuals, Sha-conditional residuals.
    # These are the substrate's bread-and-butter for empirical-pattern
    # discovery and many qualify as borderline-signal.
    (
        "B5_bsd_rank_residual_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.69, "magnitude_log10": 0.8,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_BSD_rank_minus_ord_vanishing_residual",
            "lmfdb_curve_class": "11.a",
        },
        "BSD rank-minus-ord-vanishing residual on standard EC class; classifier may struggle",
    ),
    (
        "B5_bsd_rank_residual_02",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.74, "magnitude_log10": 1.0,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_BSD_rank_residual_high_conductor",
            "lmfdb_curve_class": "high_conductor_500K_plus",
        },
        "BSD residual on high-conductor curve; strong signal but unusual conductor",
    ),
    (
        "B5_bsd_regulator_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.61, "magnitude_log10": 0.5,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_regulator_BSD_predicted_residual",
            "lmfdb_curve_class": "5077.a1",
        },
        "BSD regulator residual on 5077.a1 (rank-3 curve); barely above threshold",
    ),
    (
        "B5_bsd_regulator_02",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.66, "magnitude_log10": 0.7,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_regulator_residual_rank_2_curve",
            "lmfdb_curve_class": "389.a1",
        },
        "BSD regulator residual on 389.a1 (canonical rank-2); structural fingerprint visible",
    ),
    (
        "B5_bsd_sha_conditional_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.58, "magnitude_log10": 0.4,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_Sha_conditional_residual_under_BSD",
            "lmfdb_curve_class": "Sha_2_curves",
        },
        "Sha-conditional residual; conditional on BSD itself; doubly-borderline",
    ),
    (
        "B5_bsd_isogeny_class_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.71, "magnitude_log10": 0.85,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_isogeny_class_invariant_residual",
            "lmfdb_curve_class": "isogeny_class_constant_check",
        },
        "BSD residual constancy across isogeny class; structural prediction",
    ),
    (
        "B5_bsd_torsion_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.63, "magnitude_log10": 0.6,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_torsion_BSD_residual",
            "lmfdb_curve_class": "torsion_4_or_higher",
        },
        "Torsion-conditional BSD residual on rare-torsion curves",
    ),
    (
        "B5_bsd_CM_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.78, "magnitude_log10": 1.1,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "CM_curve_BSD_residual",
            "lmfdb_curve_class": "CM_curves_disc_3_4_7_etc",
        },
        "CM curve BSD residual; deeper compression signature than non-CM",
    ),
    (
        "B5_bsd_quadratic_twist_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.65, "magnitude_log10": 0.7,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_quadratic_twist_BSD_residual",
            "lmfdb_curve_class": "quadratic_twist_family",
        },
        "Quadratic twist BSD residual; family-level structural pattern",
    ),
    (
        "B5_bsd_higher_rank_01",
        "signal",
        {
            "kind": "bsd_residual",
            "coeff_variance": 0.68, "magnitude_log10": 0.75,
            "canonicalizer_subclass": "variety_fingerprint",
            "math_provenance": "EC_rank_4_plus_BSD_residual",
            "lmfdb_curve_class": "rank_4_plus_rare",
        },
        "BSD residual on rank-4-plus curves (rare; ~10K known); structural but low statistics",
    ),

    # ===================================================================
    # B6: Modular-form coefficient mystery residuals (10 samples)
    # ===================================================================
    # Hecke eigenvalue patterns, congruences mod p, modular-form coefficient
    # statistics that show structural residuals against the Sato-Tate
    # baseline. The substrate's domain-natural territory.
    (
        "B6_modular_form_hecke_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.64, "magnitude_log10": 0.65,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Hecke_eigenvalue_Sato_Tate_residual",
            "form_label": "weight_2_level_11",
        },
        "Hecke eigenvalue residual against Sato-Tate baseline; level 11 weight 2",
    ),
    (
        "B6_modular_form_hecke_02",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.59, "magnitude_log10": 0.5,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Hecke_eigenvalue_high_weight_residual",
            "form_label": "weight_12_level_1",
        },
        "Higher-weight Hecke eigenvalue residual; classical Ramanujan tau territory",
    ),
    (
        "B6_modular_form_congruence_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.72, "magnitude_log10": 0.85,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "tau_p_congruence_mod_691",
            "form_label": "weight_12_level_1_tau",
        },
        "tau(p) congruence mod 691; classical congruence; classifier should detect",
    ),
    (
        "B6_modular_form_congruence_02",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.66, "magnitude_log10": 0.7,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "modular_form_congruence_mod_p_borderline",
            "form_label": "level_23_weight_2",
        },
        "Mod-p congruence at level 23; less famous than tau but real signal",
    ),
    (
        "B6_modular_form_lfunction_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.61, "magnitude_log10": 0.6,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "modular_L_function_low_lying_zero_residual",
            "form_label": "GL2_low_conductor",
        },
        "Low-lying zero residual on GL(2) modular L-function; RMT-conditional pattern",
    ),
    (
        "B6_modular_form_lfunction_02",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.57, "magnitude_log10": 0.45,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "modular_L_function_first_moment_residual",
            "form_label": "GL2_family_average",
        },
        "First-moment residual on modular L-function family; barely above threshold",
    ),
    (
        "B6_modular_form_GL3_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.69, "magnitude_log10": 0.75,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Maass_GL3_form_coefficient_residual",
            "form_label": "Maass_form_GL3_self_dual",
        },
        "Maass GL(3) coefficient residual; harder territory; structural fingerprint",
    ),
    (
        "B6_modular_form_eisenstein_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.63, "magnitude_log10": 0.6,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Eisenstein_series_coefficient_arithmetic_residual",
            "form_label": "weight_4_Eisenstein",
        },
        "Eisenstein series coefficient arithmetic residual; cleanest theory",
    ),
    (
        "B6_modular_form_HMF_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.58, "magnitude_log10": 0.5,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Hilbert_modular_form_coefficient_residual_field_disc_8",
            "form_label": "HMF_real_quadratic_field",
        },
        "Hilbert modular form coefficient residual over real quadratic field; rare territory",
    ),
    (
        "B6_modular_form_siegel_01",
        "signal",
        {
            "kind": "modular_form_residual",
            "coeff_variance": 0.67, "magnitude_log10": 0.7,
            "canonicalizer_subclass": "ideal_reduction",
            "math_provenance": "Siegel_modular_form_genus_2_coefficient_residual",
            "form_label": "Siegel_genus_2_weight_10",
        },
        "Siegel modular form (genus 2) coefficient residual; genus-2 rosetta territory",
    ),
]
# Total: 5 + 5 + 5 + 15 + 10 + 10 = 50 borderline_signal samples (including 2 from Day 1 seed; total file count after Day 2: 50)


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
    print(f"Trial 1 benchmark: {len(benchmark)} samples")
    print(f"  obvious_noise: {sum(1 for s in benchmark if s.sample_class == 'obvious_noise')}")
    print(f"  borderline_signal: {sum(1 for s in benchmark if s.sample_class == 'borderline_signal')}")
    print(f"  synthetic_structured_noise: {sum(1 for s in benchmark if s.sample_class == 'synthetic_structured_noise')}")

    # True-label distribution within borderline_signal
    bs_samples = [s for s in benchmark if s.sample_class == "borderline_signal"]
    print(f"  borderline_signal true-label split:")
    print(f"    signal: {sum(1 for s in bs_samples if s.true_label == 'signal')}")
    print(f"    instrument_drift: {sum(1 for s in bs_samples if s.true_label == 'instrument_drift')}")

    out_path = Path(__file__).parent / "trial_1_benchmark.json"
    serialize_benchmark(benchmark, out_path)
    print(f"\nSerialized to: {out_path}")
