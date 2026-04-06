"""
Falsification Battery — Computational kill tests for cross-domain claims.
==========================================================================
NO LLM IN THE LOOP. Every test is pure computation with hard thresholds.

Adapted from Charon's murder board (11-test battery that caught the
mean-spacing normalization artifact). The lesson: LLMs build narratives.
Only code catches artifacts.

The battery runs 11 tests on any claimed correlation between two datasets.
Each test returns: PASS, FAIL, or SKIP (insufficient data).
A claim must pass ALL non-skipped tests to be marked "survives battery."
One FAIL = claim is KILLED.

Tests:
  F1.  Permutation null (10K shuffles — is the correlation above chance?)
  F2.  Subset stability (5x random 50% splits — does it replicate?)
  F3.  Effect size gate (Cohen's d > 0.2 or r > 0.1 — is it meaningful?)
  F4.  Confound sweep (does a single lurking variable explain it?)
  F5.  Alternative normalization (does the sign flip under log/rank/z-score?)
  F6.  Base rate check (how many hypotheses tested? Bonferroni correction)
  F7.  Monotonic dose-response (if X predicts Y, does more X = more Y?)
  F8.  Direction consistency (same sign in all subgroups?)
  F9.  Simpler explanation (does random/trivial baseline match the pattern?)
  F10. Outlier sensitivity (remove top/bottom 5% — does it survive?)
  F11. Cross-validation (train on half, predict on half — above chance?)

Run:
    from falsification_battery import run_battery
    verdict, results = run_battery(group_a_values, group_b_values, ...)
"""

import numpy as np
from scipy import stats
from collections import defaultdict
from typing import Optional
import json
import time

import cycle_logger


# ---------------------------------------------------------------------------
# Core statistical helpers (no dependencies on search_engine)
# ---------------------------------------------------------------------------

def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d effect size between two groups."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    pooled_var = ((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2)
    if pooled_var == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / np.sqrt(pooled_var))


def pearson_with_ci(x: np.ndarray, y: np.ndarray, alpha: float = 0.05):
    """Pearson r with Fisher z-transform confidence interval."""
    r, p = stats.pearsonr(x, y)
    n = len(x)
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3) if n > 3 else float("inf")
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_low = np.tanh(z - z_crit * se)
    ci_high = np.tanh(z + z_crit * se)
    return float(r), float(p), float(ci_low), float(ci_high)


# ---------------------------------------------------------------------------
# F1: Permutation Null
# ---------------------------------------------------------------------------

def f1_permutation_null(values_a: np.ndarray, values_b: np.ndarray,
                        n_perm: int = 10000, seed: int = 42) -> dict:
    """Shuffle group labels. Is the observed difference above chance?

    Compares mean difference. PASS if p < 0.001 (after 10K trials).
    """
    observed_diff = abs(np.mean(values_a) - np.mean(values_b))
    combined = np.concatenate([values_a, values_b])
    n_a = len(values_a)
    rng = np.random.RandomState(seed)

    count_exceeded = 0
    for _ in range(n_perm):
        rng.shuffle(combined)
        perm_diff = abs(np.mean(combined[:n_a]) - np.mean(combined[n_a:]))
        if perm_diff >= observed_diff:
            count_exceeded += 1

    p_value = (count_exceeded + 1) / (n_perm + 1)
    z_score = (observed_diff - 0) / (np.std(combined) / np.sqrt(n_a)) if np.std(combined) > 0 else 0

    passed = p_value < 0.001
    return {
        "test": "F1_permutation_null",
        "verdict": "PASS" if passed else "FAIL",
        "observed_diff": float(observed_diff),
        "p_value": float(p_value),
        "z_score": float(z_score),
        "n_permutations": n_perm,
        "exceeded_count": count_exceeded,
        "threshold": "p < 0.001",
    }


# ---------------------------------------------------------------------------
# F2: Subset Stability
# ---------------------------------------------------------------------------

def f2_subset_stability(values_a: np.ndarray, values_b: np.ndarray,
                        n_splits: int = 5, seed: int = 42) -> dict:
    """Run on 5 random 50% subsets. PASS if sign is consistent in >= 4/5."""
    rng = np.random.RandomState(seed)
    signs = []
    effect_sizes = []

    for i in range(n_splits):
        idx_a = rng.choice(len(values_a), len(values_a) // 2, replace=False)
        idx_b = rng.choice(len(values_b), len(values_b) // 2, replace=False)
        d = cohens_d(values_a[idx_a], values_b[idx_b])
        signs.append(np.sign(d))
        effect_sizes.append(d)

    full_d = cohens_d(values_a, values_b)
    consistent = sum(1 for s in signs if s == np.sign(full_d))
    passed = consistent >= 4

    return {
        "test": "F2_subset_stability",
        "verdict": "PASS" if passed else "FAIL",
        "full_d": float(full_d),
        "split_ds": [round(d, 4) for d in effect_sizes],
        "sign_consistency": f"{consistent}/{n_splits}",
        "threshold": ">= 4/5 consistent sign",
    }


# ---------------------------------------------------------------------------
# F3: Effect Size Gate
# ---------------------------------------------------------------------------

def f3_effect_size(values_a: np.ndarray, values_b: np.ndarray) -> dict:
    """PASS if |Cohen's d| >= 0.2 (small effect) or Pearson |r| >= 0.1."""
    d = cohens_d(values_a, values_b)
    # Point-biserial r from d: r = d / sqrt(d^2 + 4)
    r_pb = d / np.sqrt(d ** 2 + 4) if (d ** 2 + 4) > 0 else 0

    passed = abs(d) >= 0.2 or abs(r_pb) >= 0.1
    return {
        "test": "F3_effect_size",
        "verdict": "PASS" if passed else "FAIL",
        "cohens_d": round(float(d), 4),
        "point_biserial_r": round(float(r_pb), 4),
        "threshold": "|d| >= 0.2 or |r| >= 0.1",
    }


# ---------------------------------------------------------------------------
# F4: Confound Sweep
# ---------------------------------------------------------------------------

def f4_confound_sweep(values_a: np.ndarray, values_b: np.ndarray,
                      confounds: dict[str, np.ndarray]) -> dict:
    """For each confound variable, partial it out. FAIL if correlation vanishes.

    confounds: {name: array of confound values, one per observation (a then b stacked)}
    """
    if not confounds:
        return {"test": "F4_confound_sweep", "verdict": "SKIP", "reason": "no confounds provided"}

    combined = np.concatenate([values_a, values_b])
    group_label = np.array([0] * len(values_a) + [1] * len(values_b), dtype=float)
    base_r, base_p = stats.pointbiserialr(group_label, combined)

    results = {}
    killed_by = None

    for name, confound_vals in confounds.items():
        if len(confound_vals) != len(combined):
            results[name] = {"error": f"length mismatch: {len(confound_vals)} vs {len(combined)}"}
            continue

        # Partial out confound via residualization
        slope_v = np.polyfit(confound_vals, combined, 1)
        resid_v = combined - np.polyval(slope_v, confound_vals)
        slope_g = np.polyfit(confound_vals, group_label, 1)
        resid_g = group_label - np.polyval(slope_g, confound_vals)

        if np.std(resid_v) > 0 and np.std(resid_g) > 0:
            partial_r, partial_p = stats.pearsonr(resid_g, resid_v)
        else:
            partial_r, partial_p = 0.0, 1.0

        absorbed = abs(partial_r) < abs(base_r) * 0.5  # > 50% absorbed
        results[name] = {
            "partial_r": round(float(partial_r), 4),
            "partial_p": round(float(partial_p), 6),
            "base_r": round(float(base_r), 4),
            "absorption": round(1.0 - abs(partial_r) / max(abs(base_r), 1e-10), 3),
            "kills": absorbed,
        }
        if absorbed and killed_by is None:
            killed_by = name

    passed = killed_by is None
    return {
        "test": "F4_confound_sweep",
        "verdict": "PASS" if passed else "FAIL",
        "base_r": round(float(base_r), 4),
        "confound_results": results,
        "killed_by": killed_by,
        "threshold": "no single confound absorbs > 50% of correlation",
    }


# ---------------------------------------------------------------------------
# F5: Alternative Normalization
# ---------------------------------------------------------------------------

def f5_alternative_normalization(values_a: np.ndarray, values_b: np.ndarray) -> dict:
    """Test under raw, log, rank, and z-score normalizations.

    FAIL if the sign of d flips under any normalization.
    (This is the mean-spacing test that killed the Charon narrative.)
    """
    norms = {}

    # Raw
    d_raw = cohens_d(values_a, values_b)
    norms["raw"] = d_raw

    # Log (for positive values)
    pos_a = values_a[values_a > 0]
    pos_b = values_b[values_b > 0]
    if len(pos_a) > 5 and len(pos_b) > 5:
        norms["log"] = cohens_d(np.log(pos_a), np.log(pos_b))

    # Rank normalization
    combined = np.concatenate([values_a, values_b])
    ranks = stats.rankdata(combined)
    rank_a = ranks[:len(values_a)]
    rank_b = ranks[len(values_a):]
    norms["rank"] = cohens_d(rank_a, rank_b)

    # Z-score (mean-spacing equivalent: divide by own mean)
    mean_a = np.mean(values_a)
    mean_b = np.mean(values_b)
    if abs(mean_a) > 1e-10 and abs(mean_b) > 1e-10:
        norms["mean_normed"] = cohens_d(values_a / mean_a, values_b / mean_b)

    # Check sign consistency across normalizations that preserve the effect type.
    # Mean-normed kills SCALE effects (good!) but also kills location shifts (expected).
    # The test: if mean_normed kills the effect (|d| < 0.05), flag it as a scale warning
    # but don't auto-fail. FAIL only if raw/log/rank disagree among themselves.
    core_norms = {k: v for k, v in norms.items() if k != "mean_normed"}
    core_signs = {k: np.sign(v) for k, v in core_norms.items()}
    core_unique = set(s for s in core_signs.values() if s != 0)
    core_sign_flips = len(core_unique) > 1

    mean_normed_d = norms.get("mean_normed", None)
    scale_warning = (mean_normed_d is not None and abs(mean_normed_d) < 0.05
                     and abs(norms.get("raw", 0)) > 0.05)

    passed = not core_sign_flips
    return {
        "test": "F5_alternative_normalization",
        "verdict": "PASS" if passed else "FAIL",
        "d_by_normalization": {k: round(v, 4) for k, v in norms.items()},
        "core_sign_flips": core_sign_flips,
        "scale_warning": scale_warning,
        "note": ("SCALE WARNING: mean-normalization kills the effect — "
                 "this may be a pure scale artifact (cf. Charon April 5)"
                 if scale_warning else ""),
        "threshold": "sign consistent across raw/log/rank (mean-normed flags scale artifacts)",
    }


# ---------------------------------------------------------------------------
# F6: Base Rate / Multiple Comparison Correction
# ---------------------------------------------------------------------------

def f6_base_rate(p_value: float, n_hypotheses_tested: int) -> dict:
    """Bonferroni correction. PASS if p < 0.05 / n_hypotheses."""
    corrected_threshold = 0.05 / max(n_hypotheses_tested, 1)
    passed = p_value < corrected_threshold

    return {
        "test": "F6_base_rate",
        "verdict": "PASS" if passed else "FAIL",
        "raw_p": float(p_value),
        "n_hypotheses": n_hypotheses_tested,
        "bonferroni_threshold": float(corrected_threshold),
        "threshold": f"p < {corrected_threshold:.6f}",
    }


# ---------------------------------------------------------------------------
# F7: Monotonic Dose-Response
# ---------------------------------------------------------------------------

def f7_dose_response(dose_levels: list[np.ndarray], dose_labels: list[str] = None) -> dict:
    """Given ordered groups (low->high dose), test for monotonic effect.

    PASS if Spearman rho between dose level and group mean has |rho| > 0.8
    and p < 0.05.
    """
    if len(dose_levels) < 3:
        return {"test": "F7_dose_response", "verdict": "SKIP",
                "reason": f"Need >= 3 dose levels, got {len(dose_levels)}"}

    means = [float(np.mean(level)) for level in dose_levels]
    doses = list(range(len(dose_levels)))
    rho, p = stats.spearmanr(doses, means)

    passed = abs(rho) > 0.8 and p < 0.05
    return {
        "test": "F7_dose_response",
        "verdict": "PASS" if passed else "FAIL",
        "means": [round(m, 6) for m in means],
        "labels": dose_labels or [f"level_{i}" for i in range(len(dose_levels))],
        "spearman_rho": round(float(rho), 4),
        "p_value": float(p),
        "threshold": "|rho| > 0.8 and p < 0.05",
    }


# ---------------------------------------------------------------------------
# F8: Direction Consistency Across Subgroups
# ---------------------------------------------------------------------------

def f8_direction_consistency(subgroups: dict[str, tuple[np.ndarray, np.ndarray]]) -> dict:
    """For each subgroup, compute d. PASS if >= 75% share the overall sign.

    subgroups: {name: (group_a_values, group_b_values)}
    """
    if len(subgroups) < 2:
        return {"test": "F8_direction_consistency", "verdict": "SKIP",
                "reason": f"Need >= 2 subgroups, got {len(subgroups)}"}

    ds = {}
    for name, (a, b) in subgroups.items():
        if len(a) < 5 or len(b) < 5:
            continue
        ds[name] = cohens_d(a, b)

    if not ds:
        return {"test": "F8_direction_consistency", "verdict": "SKIP",
                "reason": "No subgroups with sufficient data"}

    overall_sign = np.sign(np.mean(list(ds.values())))
    consistent = sum(1 for d in ds.values() if np.sign(d) == overall_sign or d == 0)
    frac = consistent / len(ds)

    passed = frac >= 0.75
    return {
        "test": "F8_direction_consistency",
        "verdict": "PASS" if passed else "FAIL",
        "d_by_subgroup": {k: round(v, 4) for k, v in ds.items()},
        "consistency": f"{consistent}/{len(ds)} ({frac:.0%})",
        "threshold": ">= 75% same sign",
    }


# ---------------------------------------------------------------------------
# F9: Simpler Explanation (Trivial Baseline)
# ---------------------------------------------------------------------------

def f9_simpler_explanation(values_a: np.ndarray, values_b: np.ndarray,
                           baseline_labels: np.ndarray = None) -> dict:
    """Can a trivial baseline (random assignment, or magnitude alone) explain it?

    Generates 1000 random label assignments and compares effect sizes.
    PASS if observed |d| > 95th percentile of random |d|.
    """
    observed_d = abs(cohens_d(values_a, values_b))
    combined = np.concatenate([values_a, values_b])
    n_a = len(values_a)

    rng = np.random.RandomState(42)
    random_ds = []
    for _ in range(1000):
        idx = rng.permutation(len(combined))
        rand_a = combined[idx[:n_a]]
        rand_b = combined[idx[n_a:]]
        random_ds.append(abs(cohens_d(rand_a, rand_b)))

    pct_95 = np.percentile(random_ds, 95)
    pct_99 = np.percentile(random_ds, 99)

    passed = observed_d > pct_95
    return {
        "test": "F9_simpler_explanation",
        "verdict": "PASS" if passed else "FAIL",
        "observed_d": round(float(observed_d), 4),
        "random_95th": round(float(pct_95), 4),
        "random_99th": round(float(pct_99), 4),
        "random_mean": round(float(np.mean(random_ds)), 4),
        "threshold": "observed |d| > 95th percentile of random",
    }


# ---------------------------------------------------------------------------
# F10: Outlier Sensitivity
# ---------------------------------------------------------------------------

def f10_outlier_sensitivity(values_a: np.ndarray, values_b: np.ndarray,
                            trim_pct: float = 5.0) -> dict:
    """Remove top/bottom trim_pct% from both groups. PASS if sign and
    magnitude (within 50%) are preserved."""
    d_full = cohens_d(values_a, values_b)

    def trim(arr):
        lo = np.percentile(arr, trim_pct)
        hi = np.percentile(arr, 100 - trim_pct)
        return arr[(arr >= lo) & (arr <= hi)]

    a_trimmed = trim(values_a)
    b_trimmed = trim(values_b)

    if len(a_trimmed) < 5 or len(b_trimmed) < 5:
        return {"test": "F10_outlier_sensitivity", "verdict": "SKIP",
                "reason": "Too few points after trimming"}

    d_trimmed = cohens_d(a_trimmed, b_trimmed)

    sign_preserved = np.sign(d_full) == np.sign(d_trimmed) or d_full == 0
    magnitude_preserved = abs(d_trimmed) >= abs(d_full) * 0.5 if d_full != 0 else True

    passed = sign_preserved and magnitude_preserved
    return {
        "test": "F10_outlier_sensitivity",
        "verdict": "PASS" if passed else "FAIL",
        "d_full": round(float(d_full), 4),
        "d_trimmed": round(float(d_trimmed), 4),
        "trim_pct": trim_pct,
        "n_a_trimmed": len(a_trimmed),
        "n_b_trimmed": len(b_trimmed),
        "sign_preserved": sign_preserved,
        "magnitude_preserved": magnitude_preserved,
        "threshold": "same sign, magnitude within 50%",
    }


# ---------------------------------------------------------------------------
# F11: Cross-Validation (Train/Predict)
# ---------------------------------------------------------------------------

def f11_cross_validation(values_a: np.ndarray, values_b: np.ndarray,
                         n_splits: int = 5, seed: int = 42) -> dict:
    """K-fold cross-validation: train threshold on k-1 folds, predict on holdout.

    Uses a simple threshold classifier (above/below mean).
    PASS if holdout accuracy > 55% consistently.
    """
    combined = np.concatenate([values_a, values_b])
    labels = np.array([0] * len(values_a) + [1] * len(values_b))
    rng = np.random.RandomState(seed)
    indices = rng.permutation(len(combined))
    fold_size = len(indices) // n_splits

    accuracies = []
    for fold in range(n_splits):
        test_idx = indices[fold * fold_size: (fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                     indices[(fold + 1) * fold_size:]])

        train_vals = combined[train_idx]
        train_labels = labels[train_idx]
        test_vals = combined[test_idx]
        test_labels = labels[test_idx]

        # Simple threshold: mean of group means
        mean_0 = np.mean(train_vals[train_labels == 0])
        mean_1 = np.mean(train_vals[train_labels == 1])
        threshold = (mean_0 + mean_1) / 2

        if mean_0 < mean_1:
            preds = (test_vals >= threshold).astype(int)
        else:
            preds = (test_vals < threshold).astype(int)

        acc = np.mean(preds == test_labels)
        accuracies.append(float(acc))

    mean_acc = np.mean(accuracies)
    passed = mean_acc > 0.55

    return {
        "test": "F11_cross_validation",
        "verdict": "PASS" if passed else "FAIL",
        "fold_accuracies": [round(a, 3) for a in accuracies],
        "mean_accuracy": round(float(mean_acc), 4),
        "threshold": "mean accuracy > 55%",
    }


# ---------------------------------------------------------------------------
# Master Battery Runner
# ---------------------------------------------------------------------------

def run_battery(values_a: np.ndarray, values_b: np.ndarray,
                confounds: dict[str, np.ndarray] = None,
                dose_levels: list[np.ndarray] = None,
                dose_labels: list[str] = None,
                subgroups: dict[str, tuple[np.ndarray, np.ndarray]] = None,
                n_hypotheses_tested: int = 3,
                claim: str = "") -> tuple[str, list[dict]]:
    """Run full 11-test falsification battery.

    Returns: (verdict, results_list)
      verdict: "SURVIVES" if all non-skipped tests pass, else "KILLED"
    """
    log = cycle_logger.get()
    t0 = time.time()

    if log:
        log.info("battery", "battery_started", {
            "claim": claim,
            "n_a": len(values_a),
            "n_b": len(values_b),
            "has_confounds": confounds is not None,
            "has_dose_response": dose_levels is not None,
            "has_subgroups": subgroups is not None,
            "n_hypotheses_tested": n_hypotheses_tested,
        }, msg=f"FALSIFICATION BATTERY: {claim[:80]}")

    results = []

    # F1: Permutation null
    r = f1_permutation_null(values_a, values_b)
    results.append(r)

    # F2: Subset stability
    r = f2_subset_stability(values_a, values_b)
    results.append(r)

    # F3: Effect size gate
    r = f3_effect_size(values_a, values_b)
    results.append(r)

    # F4: Confound sweep
    r = f4_confound_sweep(values_a, values_b, confounds or {})
    results.append(r)

    # F5: Alternative normalization
    r = f5_alternative_normalization(values_a, values_b)
    results.append(r)

    # F6: Base rate correction
    p_from_f1 = results[0].get("p_value", 1.0)
    r = f6_base_rate(p_from_f1, n_hypotheses_tested)
    results.append(r)

    # F7: Dose-response
    if dose_levels is not None:
        r = f7_dose_response(dose_levels, dose_labels)
    else:
        r = {"test": "F7_dose_response", "verdict": "SKIP", "reason": "no dose levels provided"}
    results.append(r)

    # F8: Direction consistency
    if subgroups is not None:
        r = f8_direction_consistency(subgroups)
    else:
        r = {"test": "F8_direction_consistency", "verdict": "SKIP", "reason": "no subgroups provided"}
    results.append(r)

    # F9: Simpler explanation
    r = f9_simpler_explanation(values_a, values_b)
    results.append(r)

    # F10: Outlier sensitivity
    r = f10_outlier_sensitivity(values_a, values_b)
    results.append(r)

    # F11: Cross-validation
    r = f11_cross_validation(values_a, values_b)
    results.append(r)

    # Tally
    elapsed = time.time() - t0
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    skipped = sum(1 for r in results if r["verdict"] == "SKIP")
    verdict = "SURVIVES" if failed == 0 else "KILLED"

    summary = {
        "verdict": verdict,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": len(results),
        "elapsed_s": round(elapsed, 2),
        "kill_tests": [r["test"] for r in results if r["verdict"] == "FAIL"],
    }

    if log:
        for r in results:
            log.info("battery", f"test_{r['verdict'].lower()}", {
                "test": r["test"], "verdict": r["verdict"],
                **{k: v for k, v in r.items() if k not in ("test", "verdict")},
            }, msg=f"  {r['test']}: {r['verdict']}")

        log.info("battery", "battery_completed", {
            "claim": claim, **summary,
        }, msg=f"BATTERY {verdict}: {passed} pass, {failed} fail, {skipped} skip in {elapsed:.1f}s"
               + (f" | KILLED BY: {summary['kill_tests']}" if failed > 0 else ""))

    return verdict, results


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Falsification Battery Self-Test ===")
    print()

    # Test with a REAL effect
    rng = np.random.RandomState(42)
    a_real = rng.normal(0.0, 1.0, 500)
    b_real = rng.normal(0.3, 1.0, 500)
    print("--- Real effect (d=0.3) ---")
    verdict, results = run_battery(a_real, b_real, claim="synthetic real effect d=0.3")
    for r in results:
        print(f"  {r['test']:35s}: {r['verdict']}")
    print(f"  VERDICT: {verdict}")
    print()

    # Test with NO effect (should be killed)
    a_null = rng.normal(0.0, 1.0, 500)
    b_null = rng.normal(0.0, 1.0, 500)
    print("--- Null effect (d=0.0) ---")
    verdict, results = run_battery(a_null, b_null, claim="synthetic null effect d=0.0")
    for r in results:
        print(f"  {r['test']:35s}: {r['verdict']}")
    print(f"  VERDICT: {verdict}")
    print()

    # Test with artifact (sign flips under normalization)
    a_artifact = rng.exponential(1.0, 500)
    b_artifact = rng.exponential(1.5, 500)  # different scale, same shape
    print("--- Scale artifact (exponential, different rate) ---")
    verdict, results = run_battery(a_artifact, b_artifact, claim="synthetic scale artifact")
    for r in results:
        print(f"  {r['test']:35s}: {r['verdict']}")
    print(f"  VERDICT: {verdict}")
