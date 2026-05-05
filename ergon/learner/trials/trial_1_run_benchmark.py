"""Trial 1 Day 4 — Run residual benchmark + report.

Runs all 200 benchmark samples through `sigma_kernel.residuals._classify_residual`
and reports:
- overall accuracy
- per-class confusion matrix
- FP rate on synthetic structured-noise specifically (load-bearing constraint)
- w_R activation tier per v6 confidence-tiered specification

NOTE: the v5 residual classifier is rule-based (not probabilistic). It returns
hard classifications (signal / noise / instrument_drift / unclassified) without
confidence scores. ECE-across-bins (which v6 §2.6 specifies as a required
acceptance criterion) cannot be computed against a rule-based classifier;
it requires a probabilistic classifier head.

For Trial 1 Day 4: report the rule-based accuracy + FP rate; flag ECE
as N/A pending probabilistic-classifier implementation (v0.5+ work).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Make sure we can import sigma_kernel
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ergon.learner.trials.trial_1_residual_benchmark import (
    BenchmarkSample,
    assemble_benchmark,
)


# ---------------------------------------------------------------------------
# Adapter — translate benchmark-sample shape to classifier-expected shape
# ---------------------------------------------------------------------------
#
# The benchmark samples carry `canonicalizer_subclass: "<subclass>"`. The
# v5 classifier (sigma_kernel/residuals.py:_classify_residual) checks for
# `<subclass>_signature: <truthy_value>` keys. The adapter translates one
# shape into the other while preserving the rest of the failure_shape.

CANONICALIZER_SUBCLASSES = (
    "group_quotient",
    "partition_refinement",
    "ideal_reduction",
    "variety_fingerprint",
)


def adapt_for_classifier(sample: BenchmarkSample) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
    """Convert a BenchmarkSample into the (magnitude, surviving_subset, failure_shape)
    triple the v5 classifier expects.

    - magnitude: 10 ** magnitude_log10 (the classifier wants linear magnitude;
      benchmark samples carry log-magnitude). For -inf log-magnitude we map
      to 0.0 (classifier rule 1 short-circuits zero-magnitude as noise).
    - surviving_subset: synthesized as {"items": ["adapter_synthetic"], "n": 1}
      for non-zero magnitudes, {"items": [], "n": 0} for zero. The classifier
      uses surviving_subset only to short-circuit on n==0.
    - failure_shape: copies all keys from sample.failure_shape, plus translates
      canonicalizer_subclass into a <subclass>_signature truthy key.
    """
    fs = dict(sample.failure_shape)

    # Translate magnitude_log10 → magnitude (linear)
    log_mag = fs.pop("magnitude_log10", None)
    if log_mag is None or log_mag == float("-inf"):
        magnitude = 0.0
    else:
        magnitude = 10.0 ** float(log_mag)

    # Translate canonicalizer_subclass → <subclass>_signature
    subclass = fs.pop("canonicalizer_subclass", None)
    if subclass and subclass in CANONICALIZER_SUBCLASSES:
        # Use the sample_id as the truthy fingerprint (any non-empty string works)
        fs[f"{subclass}_signature"] = f"benchmark_fingerprint_{sample.sample_id}"

    # Synthesize surviving_subset
    if magnitude == 0.0:
        surviving_subset = {"items": [], "n": 0}
    else:
        surviving_subset = {"items": [f"adapter_{sample.sample_id}"], "n": 1}

    return magnitude, surviving_subset, fs


# ---------------------------------------------------------------------------
# Classifier instantiation
# ---------------------------------------------------------------------------


def make_classifier():
    """Build a minimal ResidualExtension instance to call _classify_residual.

    We use an in-memory SQLite kernel and a small calibration_signatures
    map covering the F1+F6+F9+F11 unanimous battery's known drift
    fingerprints. The benchmark's B4 samples carry drift_fingerprint
    keys that should match these.
    """
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.residuals import ResidualExtension

    kernel = SigmaKernel(":memory:")

    # Calibration signatures: each B4 sample's drift_fingerprint should
    # match one of these so the classifier returns instrument_drift.
    # The drift detector (sigma_kernel/residuals.py:_matches_drift_signature)
    # looks for a "kind" containing drift-related keywords AND matches
    # against signatures that share structural fields.
    calibration_signatures = {
        "F1_permutation_drift": {
            "kind": "calibration_drift_residual",
            "drift_fingerprint_substring": "F1_",
        },
        "F6_base_rate_drift": {
            "kind": "calibration_drift_residual",
            "drift_fingerprint_substring": "F6_",
        },
        "F9_simpler_explanation_drift": {
            "kind": "calibration_drift_residual",
            "drift_fingerprint_substring": "F9_",
        },
        "F11_cross_validation_drift": {
            "kind": "calibration_drift_residual",
            "drift_fingerprint_substring": "F11_",
        },
    }

    ext = ResidualExtension(kernel, calibration_signatures=calibration_signatures)
    return ext


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------


def run_benchmark() -> Dict[str, Any]:
    """Run the full 200-sample benchmark; return per-sample predictions + aggregates."""
    samples = assemble_benchmark()
    classifier = make_classifier()

    predictions: List[Dict[str, Any]] = []
    for s in samples:
        magnitude, surviving_subset, failure_shape = adapt_for_classifier(s)
        try:
            predicted = classifier._classify_residual(
                magnitude=magnitude,
                surviving_subset=surviving_subset,
                failure_shape=failure_shape,
            )
        except Exception as e:
            predicted = f"ERROR:{type(e).__name__}"

        predictions.append({
            "sample_id": s.sample_id,
            "sample_class": s.sample_class,
            "true_label": s.true_label,
            "predicted_label": predicted,
            "rationale": s.rationale,
        })

    return {
        "n_samples": len(samples),
        "predictions": predictions,
    }


def compute_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Compute accuracy, per-class confusion, FP rate on synthetic structured-noise."""
    preds = result["predictions"]
    n = len(preds)

    # Overall accuracy: predicted_label == true_label
    n_correct = sum(1 for p in preds if p["predicted_label"] == p["true_label"])
    overall_accuracy = n_correct / n if n > 0 else 0.0

    # Per-sample-class accuracy
    per_class_accuracy: Dict[str, Dict[str, Any]] = {}
    for cls in ("obvious_noise", "borderline_signal", "synthetic_structured_noise"):
        cls_preds = [p for p in preds if p["sample_class"] == cls]
        if not cls_preds:
            continue
        n_cls = len(cls_preds)
        n_correct_cls = sum(1 for p in cls_preds if p["predicted_label"] == p["true_label"])
        per_class_accuracy[cls] = {
            "n": n_cls,
            "n_correct": n_correct_cls,
            "accuracy": n_correct_cls / n_cls,
        }

    # Confusion matrix (predicted_label x true_label)
    confusion: Dict[Tuple[str, str], int] = Counter()
    for p in preds:
        confusion[(p["true_label"], p["predicted_label"])] += 1

    # LOAD-BEARING METRIC: FP rate on synthetic structured-noise specifically.
    # These samples have true_label="noise". The classifier should NOT predict
    # "signal" on them. Each "signal" prediction is a false positive (FP).
    ssn = [p for p in preds if p["sample_class"] == "synthetic_structured_noise"]
    ssn_signal_count = sum(1 for p in ssn if p["predicted_label"] == "signal")
    ssn_fp_rate = ssn_signal_count / len(ssn) if ssn else 0.0

    # 95% upper one-sided CI on FP rate using Wilson score (standard for proportions)
    # For 100 samples: upper bound = (k + 1.96^2/2 + 1.96*sqrt(k*(n-k)/n + 1.96^2/4)) / (n + 1.96^2)
    n_ssn = len(ssn)
    k_ssn = ssn_signal_count
    if n_ssn > 0:
        z = 1.645  # one-sided 95% (vs 1.96 for two-sided)
        denom = n_ssn + z**2
        center = k_ssn + z**2 / 2
        spread = z * (k_ssn * (n_ssn - k_ssn) / n_ssn + z**2 / 4) ** 0.5
        ssn_fp_rate_upper_95_ci = (center + spread) / denom
    else:
        ssn_fp_rate_upper_95_ci = 0.0

    # Determine w_R activation tier per v6 §2.6
    if ssn_fp_rate_upper_95_ci <= 0.047:  # observed FP ≤2%, CI ≤4.7%
        w_r_activation = 0.15
        w_r_tier = "full"
    elif ssn_fp_rate_upper_95_ci <= 0.094:  # observed FP ≤5%, CI ≤9.4%
        w_r_activation = 0.075
        w_r_tier = "half"
    elif ssn_fp_rate_upper_95_ci <= 0.164:  # observed FP ≤10%, CI ≤16.4%
        w_r_activation = 0.0
        w_r_tier = "escrow_diagnostics_only"
    else:
        w_r_activation = 0.0
        w_r_tier = "deep_escrow_retrain_required"

    # Acceptance criteria (v8 §4 Trial 1)
    acceptance = {
        "overall_accuracy_>=_0.85": overall_accuracy >= 0.85,
        "ssn_fp_rate_<=_0.05": ssn_fp_rate <= 0.05,
        "ssn_fp_rate_<=_0.02_for_full_w_R": ssn_fp_rate <= 0.02,
    }

    return {
        "overall_accuracy": overall_accuracy,
        "per_class_accuracy": per_class_accuracy,
        "confusion_matrix": {f"{t}->{p}": c for (t, p), c in confusion.items()},
        "ssn_fp_rate": ssn_fp_rate,
        "ssn_fp_rate_upper_95_ci": ssn_fp_rate_upper_95_ci,
        "ssn_signal_count": ssn_signal_count,
        "ssn_n": n_ssn,
        "w_R_activation": w_r_activation,
        "w_R_tier": w_r_tier,
        "acceptance": acceptance,
        "ece_across_5_bins": None,  # N/A — rule-based classifier has no confidence scores
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def format_report(result: Dict[str, Any], metrics: Dict[str, Any]) -> str:
    """Format human-readable Trial 1 results report."""
    lines = []
    lines.append("=" * 72)
    lines.append("TRIAL 1 — Adversarial Residual Benchmark Results")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Total samples: {result['n_samples']}")
    lines.append(f"Overall accuracy: {metrics['overall_accuracy']:.4f}")
    lines.append("")
    lines.append("Per-sample-class accuracy:")
    for cls, info in metrics["per_class_accuracy"].items():
        lines.append(f"  {cls:30s}: {info['n_correct']:3d}/{info['n']:3d} = {info['accuracy']:.4f}")
    lines.append("")
    lines.append("LOAD-BEARING — Synthetic structured-noise FP rate:")
    lines.append(f"  observed: {metrics['ssn_signal_count']}/{metrics['ssn_n']} = {metrics['ssn_fp_rate']:.4f}")
    lines.append(f"  95% upper one-sided CI: {metrics['ssn_fp_rate_upper_95_ci']:.4f}")
    lines.append("")
    lines.append(f"w_R activation tier: {metrics['w_R_tier']}")
    lines.append(f"w_R weight: {metrics['w_R_activation']}")
    lines.append("")
    lines.append("Acceptance criteria (v8 §4 Trial 1):")
    for criterion, passed in metrics["acceptance"].items():
        status = "PASS" if passed else "FAIL"
        lines.append(f"  [{status}] {criterion}")
    lines.append("")
    lines.append("Confusion matrix (true -> predicted):")
    for key, count in sorted(metrics["confusion_matrix"].items(), key=lambda x: -x[1]):
        lines.append(f"  {key:50s}: {count}")
    lines.append("")
    lines.append("Note: ECE-across-5-bins is N/A — the v5 residual classifier is rule-based")
    lines.append("(no confidence scores). Probabilistic classifier head deferred to v0.5+.")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Running Trial 1 benchmark...")
    result = run_benchmark()
    metrics = compute_metrics(result)

    # Save raw results
    out_dir = Path(__file__).parent
    (out_dir / "trial_1_results.json").write_text(
        json.dumps({"result": result, "metrics": metrics}, indent=2),
        encoding="utf-8",
    )

    # Generate report
    report = format_report(result, metrics)
    (out_dir / "TRIAL_1_REPORT.md").write_text(report, encoding="utf-8")

    print(report)
    print(f"\nFull JSON: {out_dir / 'trial_1_results.json'}")
    print(f"Report: {out_dir / 'TRIAL_1_REPORT.md'}")
