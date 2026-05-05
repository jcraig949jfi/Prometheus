"""sigma_kernel.residual_benchmark — the 30-residual classifier benchmark.

The load-bearing day-4 acceptance test for the Residual primitive
(per proposal §7). Curates 30 residuals split as:

    10 KNOWN-SIGNAL   — hand-picked from mathematical history
    10 KNOWN-NOISE    — synthesized from numerical noise sources
    10 KNOWN-DRIFT    — synthesized to match calibration-drift fingerprints

Each entry has:
    - residual_subset         (dict) : what survived the falsification
    - failure_shape           (dict) : the structured fingerprint
    - expected_classification (str)  : 'signal' / 'noise' / 'instrument_drift'
    - name                    (str)
    - source                  (str)  : reference

Acceptance criteria:
    >=80% accuracy overall, AND zero false-positive `signal` calls on
    known-noise items. (False positives are worse than false negatives
    for this primitive — they drive infinite-rescue.)

Reference: math-tdd skill rubric (authority via cited references for
each entry); proposal §5 (classifier-kill path).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Entry type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BenchmarkEntry:
    name: str
    residual_subset: Dict[str, Any]
    failure_shape: Dict[str, Any]
    expected_classification: str  # signal / noise / instrument_drift
    source: str
    magnitude: float = 0.05


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------


def _signal(
    name: str,
    *,
    coeff_variance: float,
    variety_signature: Optional[str] = None,
    ideal_signature: Optional[str] = None,
    partition_signature: Optional[str] = None,
    group_signature: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    subset_n: int = 5,
    source: str,
    magnitude: float = 0.05,
) -> BenchmarkEntry:
    """Build a known-signal entry. Must populate at least one canonicalizer
    signature OR pass coeff_variance > 0.5 (heuristic threshold)."""
    shape = {"kind": "structured_residual", "coeff_variance": coeff_variance}
    if variety_signature:
        shape["variety_signature"] = variety_signature
    if ideal_signature:
        shape["ideal_signature"] = ideal_signature
    if partition_signature:
        shape["partition_signature"] = partition_signature
    if group_signature:
        shape["group_signature"] = group_signature
    if extra:
        shape.update(extra)
    return BenchmarkEntry(
        name=name,
        residual_subset={"items": [f"{name}_{i}" for i in range(subset_n)],
                         "n": subset_n},
        failure_shape=shape,
        expected_classification="signal",
        source=source,
        magnitude=magnitude,
    )


def _noise(
    name: str,
    *,
    coeff_variance: float = 0.0,
    extra: Optional[Dict[str, Any]] = None,
    subset_n: int = 3,
    source: str,
    magnitude: float = 0.05,
) -> BenchmarkEntry:
    """Build a known-noise entry. coeff_variance below threshold; no
    canonicalizer signatures."""
    shape = {"kind": "uniform_noise", "coeff_variance": coeff_variance}
    if extra:
        shape.update(extra)
    return BenchmarkEntry(
        name=name,
        residual_subset={"items": [f"{name}_{i}" for i in range(subset_n)],
                         "n": subset_n},
        failure_shape=shape,
        expected_classification="noise",
        source=source,
        magnitude=magnitude,
    )


def _drift(
    name: str,
    *,
    drift_kind: str,
    drift_payload: Dict[str, Any],
    subset_n: int = 5,
    source: str,
    magnitude: float = 0.0087,
) -> BenchmarkEntry:
    """Build a known-drift entry. failure_shape['kind'] matches one of
    the calibration_signatures keys."""
    shape: Dict[str, Any] = {"kind": drift_kind, "coeff_variance": 0.05}
    shape.update(drift_payload)
    return BenchmarkEntry(
        name=name,
        residual_subset={"items": [f"{name}_{i}" for i in range(subset_n)],
                         "n": subset_n},
        failure_shape=shape,
        expected_classification="instrument_drift",
        source=source,
        magnitude=magnitude,
    )


# ---------------------------------------------------------------------------
# 10 KNOWN-SIGNAL residuals (mathematical history)
# ---------------------------------------------------------------------------


SIGNAL_ENTRIES: List[BenchmarkEntry] = [
    _signal(
        "mercury_perihelion",
        coeff_variance=1.7,
        variety_signature="elliptic_orbit_residual",
        extra={"magnitude_arcsec_per_century": 43},
        source=("Le Verrier 1859 / Einstein 1915. 43 arcsec/century "
                "structured deviation from Newtonian fit; seed of GR."),
    ),
    _signal(
        "ramanujan_hardy_partition",
        coeff_variance=0.9,
        ideal_signature="circle_method_leading_term",
        extra={"asymptotic_correction": "exp(pi*sqrt(2n/3))/(4n*sqrt(3))"},
        source=("Hardy & Ramanujan 1918, 'Asymptotic Formulae in "
                "Combinatory Analysis'. Leading correction term in p(n)."),
    ),
    _signal(
        "riemann_li_minus_pi",
        coeff_variance=1.1,
        variety_signature="prime_counting_residual",
        extra={"signed": True, "limit_distribution": "Skewes_sign_changes"},
        source=("Riemann 1859; Skewes 1933. Li(x) - pi(x) is a signed, "
                "structured residual that converges to a real distribution."),
    ),
    _signal(
        "obstruction_a148_a149",
        coeff_variance=2.3,
        variety_signature="obstruction_shape_99_13",
        extra={"survival_rate": 0.0087},
        source=("Charon recent work on A148/A149* sequences: 99.13% kill "
                "with 0.87% structured survival — the motivating example "
                "of the proposal."),
    ),
    _signal(
        "lehmer_cluster_M1_176",
        coeff_variance=0.85,
        variety_signature="reciprocal_minimal_polynomial",
        extra={"mahler_measure": 1.17628},
        source=("Mossinghoff Mahler measure tables; Lehmer 1933. "
                "M=1.176... survives all reciprocal poly null distributions."),
    ),
    _signal(
        "gauss_class_number_residual",
        coeff_variance=1.4,
        ideal_signature="ideal_class_residual_after_detrend",
        extra={"detrended": True, "log_h_correction": True},
        source=("Gauss class number h(D) ~ pi*sqrt(|D|)/log|D|; the "
                "residual after detrending exhibits structured fluctuation "
                "(Cohen-Lenstra heuristics)."),
    ),
    _signal(
        "selberg_trace_leading",
        coeff_variance=1.6,
        variety_signature="selberg_trace_main_term",
        extra={"hyperbolic_lengths": "trace_formula_residual"},
        source=("Selberg 1956 trace formula. Leading-term residual after "
                "subtracting the geometric side has spectral structure."),
    ),
    _signal(
        "modular_hecke_eigen_residual",
        coeff_variance=1.05,
        ideal_signature="hecke_eigenvalue_after_detrend",
        extra={"weight": 12, "level": 1, "sato_tate_residual": True},
        source=("Sato-Tate distribution residuals on Hecke eigenvalues "
                "of modular forms (cf. Barnet-Lamb-Geraghty-Harris-Taylor)."),
    ),
    _signal(
        "ramanujan_tau_p_congruence",
        coeff_variance=0.95,
        ideal_signature="mod_p_congruence_pattern",
        extra={"prime": 691, "congruence": "tau(p) == sigma_11(p) mod 691"},
        source=("Ramanujan 1916; Serre 1968. tau(p) congruences mod p — "
                "structured residual after detrending."),
    ),
    _signal(
        "deligne_weil_riemann_residual",
        coeff_variance=1.25,
        variety_signature="weil_l_function_residual",
        extra={"variety_dim": 2, "weight": 1},
        source=("Deligne 1974, 'La conjecture de Weil II'. L-function "
                "residual on smooth proj. variety has bounded structured form."),
    ),
]
assert len(SIGNAL_ENTRIES) == 10


# ---------------------------------------------------------------------------
# 10 KNOWN-NOISE residuals (numerical noise sources)
# ---------------------------------------------------------------------------


NOISE_ENTRIES: List[BenchmarkEntry] = [
    _noise(
        "small_n_gaussian",
        coeff_variance=0.0,
        extra={"distribution": "normal", "n": 10, "z_max": 1.2},
        source="Textbook null. n=10 Gaussians; max |z|=1.2; no structure.",
    ),
    _noise(
        "fp_quantization",
        coeff_variance=0.02,
        extra={"source": "float64_truncation_on_integer_relation",
               "ulp_scale": 1e-15},
        source=("Floating-point quantization residuals on a clean integer "
                "relation. Pure ULP-scale noise."),
    ),
    _noise(
        "bootstrap_single_distribution",
        coeff_variance=0.04,
        extra={"source": "bootstrap_resamples", "n_resamples": 100,
               "underlying_distribution": "single_normal"},
        source=("Bootstrap variance on samples drawn from a single fixed "
                "distribution; not actually structured."),
    ),
    _noise(
        "mc_seed_variance",
        coeff_variance=0.03,
        extra={"source": "monte_carlo_seed_jitter", "converged": True,
               "n_seeds": 50},
        source=("MC seed variance on a converged statistic; should be "
                "indistinguishable from numerical noise."),
    ),
    _noise(
        "uniform_random_residual",
        coeff_variance=0.01,
        extra={"distribution": "uniform_0_1", "n": 50},
        source="Uniform random residuals; null distribution by construction.",
    ),
    _noise(
        "round_trip_cancellation",
        coeff_variance=0.0,
        extra={"source": "round_trip_arithmetic", "expected": 0.0},
        source=("Round-trip arithmetic residuals (a+b-b-a). Pure FP cancellation."),
    ),
    _noise(
        "shuffled_index_artifact",
        coeff_variance=0.03,
        extra={"source": "index_shuffle", "n": 30},
        source=("Residuals from random index shuffle; no underlying signal."),
    ),
    _noise(
        "k_fold_residual_variance",
        coeff_variance=0.02,
        extra={"source": "k_fold_cv_split", "k": 5, "underlying_homogeneous": True},
        source=("k-fold CV split variance on a truly homogeneous dataset."),
    ),
    _noise(
        "permutation_null_residual",
        coeff_variance=0.04,
        extra={"source": "label_permutation", "n_permutations": 1000,
               "p_value": 0.5},
        source=("Permutation-null residuals at p=0.5; defines the noise floor."),
    ),
    _noise(
        "thermal_jitter_residual",
        coeff_variance=0.02,
        extra={"source": "thermal_clock_jitter", "amplitude_ns": 0.1},
        source=("Sub-nanosecond thermal jitter on a stable clock signal."),
    ),
]
assert len(NOISE_ENTRIES) == 10


# ---------------------------------------------------------------------------
# 10 KNOWN-DRIFT residuals (calibration-drift fingerprints)
# ---------------------------------------------------------------------------


DRIFT_ENTRIES: List[BenchmarkEntry] = [
    _drift(
        "anchor_recovery_99_13",
        drift_kind="anchor_recovery_drift",
        drift_payload={"anchor_recovery_rate": 0.9913,
                       "anchors_checked": 5},
        source=("Anchor recovery rate dropped 100%->99.13% — the OPERA "
                "loose-cable signature applied to F1-F20 battery."),
    ),
    _drift(
        "anchor_recovery_98",
        drift_kind="anchor_recovery_drift",
        drift_payload={"anchor_recovery_rate": 0.98,
                       "anchors_checked": 10},
        source="Anchor recovery dropped to 98% — calibration regression.",
    ),
    _drift(
        "prime_decile_overfit_p3",
        drift_kind="prime_decile_bias",
        drift_payload={"decile_correlation": 0.72,
                       "biased_decile": 3},
        source=("PATTERN_PRIME_GRAVITATIONAL_OVERFIT: bias concentrated "
                "in prime decile 3."),
    ),
    _drift(
        "prime_decile_overfit_p7",
        drift_kind="prime_decile_bias",
        drift_payload={"decile_correlation": 0.65,
                       "biased_decile": 7},
        source=("PATTERN_PRIME_GRAVITATIONAL_OVERFIT: bias concentrated "
                "in prime decile 7."),
    ),
    _drift(
        "conductor_decile_correlation",
        drift_kind="conductor_decile_correlation",
        drift_payload={"conductor_correlation": 0.81,
                       "biased_decile": 5},
        source=("PATTERN_CONDUCTOR_CONFOUND: null breakdown correlated "
                "with conductor decile 5."),
    ),
    _drift(
        "conductor_decile_correlation_high",
        drift_kind="conductor_decile_correlation",
        drift_payload={"conductor_correlation": 0.93,
                       "biased_decile": 9},
        source=("PATTERN_CONDUCTOR_CONFOUND: high correlation with "
                "conductor decile 9; battery integrity flag."),
    ),
    _drift(
        "anchor_recovery_drift_subtle",
        drift_kind="anchor_recovery_drift",
        drift_payload={"anchor_recovery_rate": 0.995,
                       "anchors_checked": 20},
        source=("Subtle anchor recovery drift (99.5%); within the drift "
                "fingerprint window of the calibration set."),
    ),
    _drift(
        "anchor_recovery_drift_severe",
        drift_kind="anchor_recovery_drift",
        drift_payload={"anchor_recovery_rate": 0.96,
                       "anchors_checked": 50},
        source="Severe anchor drift (96%) on F1-F20 with N=50 anchors checked.",
    ),
    _drift(
        "prime_decile_overfit_strong",
        drift_kind="prime_decile_bias",
        drift_payload={"decile_correlation": 0.90,
                       "biased_decile": 1},
        source=("PATTERN_PRIME_GRAVITATIONAL_OVERFIT: strong correlation "
                "0.90 in decile 1 — clear instrument fault."),
    ),
    _drift(
        "conductor_decile_correlation_low",
        drift_kind="conductor_decile_correlation",
        drift_payload={"conductor_correlation": 0.55,
                       "biased_decile": 2},
        source=("PATTERN_CONDUCTOR_CONFOUND: marginal correlation 0.55 "
                "in conductor decile 2 — at threshold of fingerprint match."),
    ),
]
assert len(DRIFT_ENTRIES) == 10


# ---------------------------------------------------------------------------
# Combined benchmark
# ---------------------------------------------------------------------------


BENCHMARK_ENTRIES: List[BenchmarkEntry] = (
    SIGNAL_ENTRIES + NOISE_ENTRIES + DRIFT_ENTRIES
)
assert len(BENCHMARK_ENTRIES) == 30


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_benchmark(ext, kernel, entries: List[BenchmarkEntry]) -> Dict[str, Any]:
    """Run the classifier on every benchmark entry; return per-class
    precision/recall + the load-bearing false-positive count.

    The kernel must already be SQLite-backed; the parent claim used as
    a stable anchor is bootstrapped on entry.
    """
    parent = kernel.CLAIM(
        target_name="benchmark_parent",
        hypothesis="benchmark anchor",
        evidence={"benchmark": "30_residual"},
        kill_path="benchmark_kill",
    )
    correct = 0
    confusion: Dict[str, Dict[str, int]] = {
        "signal": {"signal": 0, "noise": 0, "instrument_drift": 0,
                   "unclassified": 0},
        "noise": {"signal": 0, "noise": 0, "instrument_drift": 0,
                  "unclassified": 0},
        "instrument_drift": {"signal": 0, "noise": 0, "instrument_drift": 0,
                             "unclassified": 0},
    }
    fp_signal_items: List[str] = []
    misclassified: List[Dict[str, str]] = []

    for entry in entries:
        res = ext.record_residual(
            parent_claim_id=parent.id,
            test_id=f"bench_{entry.name}",
            magnitude=entry.magnitude,
            surviving_subset=entry.residual_subset,
            failure_shape=entry.failure_shape,
            instrument_id="F1_F20_battery",
            cost_budget=10.0,
        )
        actual = res.classification
        expected = entry.expected_classification
        confusion[expected][actual] = confusion[expected].get(actual, 0) + 1
        if actual == expected:
            correct += 1
        else:
            misclassified.append({
                "name": entry.name,
                "expected": expected,
                "actual": actual,
                "source": entry.source,
            })
        # False-positive `signal` on known-noise: load-bearing.
        if expected == "noise" and actual == "signal":
            fp_signal_items.append(entry.name)

    n = len(entries)
    accuracy = correct / n if n else 0.0

    # Per-class precision/recall.
    per_class: Dict[str, Dict[str, float]] = {}
    for cls in ("signal", "noise", "instrument_drift"):
        # tp = predicted cls and was cls
        tp = confusion[cls][cls]
        # fn = was cls, predicted other
        fn = sum(v for k, v in confusion[cls].items() if k != cls)
        # fp = was other, predicted cls
        fp = sum(confusion[other].get(cls, 0) for other in confusion if other != cls)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        per_class[cls] = {"precision": precision, "recall": recall, "n": tp + fn}

    return {
        "n": n,
        "correct": correct,
        "accuracy": accuracy,
        "confusion": confusion,
        "per_class": per_class,
        "false_positive_signal_count": len(fp_signal_items),
        "false_positive_signal_items": fp_signal_items,
        "misclassified": misclassified,
    }
