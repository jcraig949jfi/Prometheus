"""
Falsification Battery — Computational kill tests for cross-domain claims.
==========================================================================
NO LLM IN THE LOOP. Every test is pure computation with hard thresholds.

Adapted from Charon's murder board (11-test battery that caught the
mean-spacing normalization artifact). The lesson: LLMs build narratives.
Only code catches artifacts.

The battery runs 14 tests on any claimed correlation between two datasets.
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
  F12. Partial correlation (does the correlation survive after removing obvious confounds?)
  F13. Growth rate filter (is the correlation with the target or just with polynomial growth?)
  F14. Phase-shift test (does correlation decay when index is shifted? Gemini April 7)

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
# F12: Partial Correlation Against Obvious Confounds
# ---------------------------------------------------------------------------

def f12_partial_correlation(values_a: np.ndarray, values_b: np.ndarray,
                            index_values: np.ndarray = None) -> dict:
    """Remove obvious confounds (index/size scaling) and retest correlation.

    The April 5 lesson: two quantities that both scale with p will always
    correlate. Remove p and the signal vanishes. This test catches that
    automatically instead of requiring manual investigation.

    Logic:
      1. Identify confound: if index_values provided, use those; otherwise
         use integer indices (0..N-1) as the confound (catches anything that
         scales with position/size).
      2. Compute raw Spearman correlation between a and b.
      3. Residualize both a and b against the confound (OLS, subtract predicted).
      4. Compute partial Spearman correlation on the residuals.
      5. FAIL if raw correlation is significant (p < 0.05) BUT partial
         correlation is not (p > 0.05). This means the confound explained
         the entire relationship.

    SKIP if either array has fewer than 20 elements.
    """
    n = min(len(values_a), len(values_b))

    if n < 20:
        return {"test": "F12_partial_correlation", "verdict": "SKIP",
                "reason": f"Need >= 20 elements, got {n}"}

    # Truncate to equal length if needed
    a = np.asarray(values_a[:n], dtype=float)
    b = np.asarray(values_b[:n], dtype=float)

    # Determine confound
    if index_values is not None:
        confound = np.asarray(index_values[:n], dtype=float)
        confound_name = "provided_index"
    else:
        # Auto-detect: use integer index as confound.
        # This catches anything that scales linearly with position/size/prime.
        confound = np.arange(n, dtype=float)
        confound_name = "integer_index"

    # Check whether both arrays actually scale with the confound
    # (if neither correlates with confound, partial correlation is moot)
    rho_a_conf, p_a_conf = stats.spearmanr(a, confound)
    rho_b_conf, p_b_conf = stats.spearmanr(b, confound)

    both_scale = (p_a_conf < 0.05) and (p_b_conf < 0.05)

    if not both_scale:
        return {
            "test": "F12_partial_correlation",
            "verdict": "PASS",
            "reason": "confound does not correlate with both arrays — no shared scaling to remove",
            "confound": confound_name,
            "rho_a_confound": round(float(rho_a_conf), 4),
            "p_a_confound": float(p_a_conf),
            "rho_b_confound": round(float(rho_b_conf), 4),
            "p_b_confound": float(p_b_conf),
        }

    # Raw Spearman correlation
    rho_raw, p_raw = stats.spearmanr(a, b)

    # Residualize: linear regression of each array against confound, take residuals
    slope_a, intercept_a = np.polyfit(confound, a, 1)
    resid_a = a - (slope_a * confound + intercept_a)

    slope_b, intercept_b = np.polyfit(confound, b, 1)
    resid_b = b - (slope_b * confound + intercept_b)

    # Partial Spearman correlation on residuals
    rho_partial, p_partial = stats.spearmanr(resid_a, resid_b)

    # FAIL condition: raw is significant, partial is not.
    # This means the confound explained the entire correlation.
    raw_significant = p_raw < 0.05
    partial_significant = p_partial < 0.05

    if raw_significant and not partial_significant:
        passed = False
        explanation = (f"Raw Spearman rho={rho_raw:.4f} (p={p_raw:.2e}) is significant, "
                       f"but after removing '{confound_name}', partial rho={rho_partial:.4f} "
                       f"(p={p_partial:.2e}) is NOT significant. "
                       f"The correlation was entirely explained by the confound. "
                       f"Scale kills narratives.")
    else:
        passed = True
        explanation = (f"Correlation survives confound removal. "
                       f"Raw rho={rho_raw:.4f}, partial rho={rho_partial:.4f}."
                       if raw_significant else
                       f"Raw correlation not significant (p={p_raw:.2e}), "
                       f"nothing to partial out.")

    return {
        "test": "F12_partial_correlation",
        "verdict": "PASS" if passed else "FAIL",
        "confound": confound_name,
        "rho_raw": round(float(rho_raw), 4),
        "p_raw": float(p_raw),
        "rho_partial": round(float(rho_partial), 4),
        "p_partial": float(p_partial),
        "rho_a_confound": round(float(rho_a_conf), 4),
        "rho_b_confound": round(float(rho_b_conf), 4),
        "raw_significant": raw_significant,
        "partial_significant": partial_significant,
        "explanation": explanation,
        "threshold": "if raw p < 0.05 then partial p must also be < 0.05",
    }


def f13_growth_rate_filter(values_a: np.ndarray, values_b: np.ndarray) -> dict:
    """The April 7 lesson: polynomial growth mimics structural coupling.

    If two sequences both grow quadratically, they'll correlate at r>0.9
    even with no structural connection. This test compares the claimed
    correlation against simple growth baselines (n, n^2, 2^n).

    Logic:
      1. Compute partial correlation of a vs b (controlling for index)
      2. Compute partial correlation of a vs n^2 (controlling for index)
      3. Compute partial correlation of a vs 2^n (controlling for index)
      4. FAIL if correlation with a growth baseline EXCEEDS correlation with b
         This means b isn't special — any sequence with similar growth matches.
    """
    a = np.array(values_a, dtype=float)
    b = np.array(values_b, dtype=float)
    n = min(len(a), len(b))

    if n < 15:
        return {"test": "F13_growth_rate_filter", "verdict": "SKIP",
                "explanation": f"Need >= 15 elements, got {n}"}

    a, b = a[:n], b[:n]
    idx = np.arange(n, dtype=float)

    # Residualize against index
    a_resid = a - np.polyval(np.polyfit(idx, a, 1), idx)
    b_resid = b - np.polyval(np.polyfit(idx, b, 1), idx)

    if np.std(a_resid) < 1e-10 or np.std(b_resid) < 1e-10:
        return {"test": "F13_growth_rate_filter", "verdict": "SKIP",
                "explanation": "Constant residuals after detrending"}

    rho_target, _ = stats.spearmanr(a_resid, b_resid)

    # Growth baselines
    baselines = {}
    for bname, bvals in [("n_squared", idx ** 2), ("two_to_n", 2.0 ** np.minimum(idx, 50)),
                         ("n_cubed", idx ** 3)]:
        b_base = bvals[:n]
        b_base_resid = b_base - np.polyval(np.polyfit(idx, b_base, 1), idx)
        if np.std(b_base_resid) < 1e-10:
            continue
        rho_base, _ = stats.spearmanr(a_resid, b_base_resid)
        baselines[bname] = round(float(rho_base), 4)

    # FAIL if any baseline beats the target
    max_baseline = max(abs(v) for v in baselines.values()) if baselines else 0
    target_r = abs(float(rho_target))

    if max_baseline > target_r and max_baseline > 0.5:
        worst = max(baselines.items(), key=lambda x: abs(x[1]))
        passed = False
        explanation = (f"Growth rate mimic detected. Target r_partial={rho_target:.4f}, "
                       f"but baseline '{worst[0]}' achieves r={worst[1]:.4f}. "
                       f"The correlation is with polynomial/exponential growth, "
                       f"not with the specific target. April 7 lesson: growth kills narratives.")
    else:
        passed = True
        explanation = (f"Target r_partial={rho_target:.4f} exceeds all growth baselines "
                       f"({baselines}). The correlation is target-specific, not growth-rate.")

    return {
        "test": "F13_growth_rate_filter",
        "verdict": "PASS" if passed else "FAIL",
        "rho_target": round(float(rho_target), 4),
        "baselines": baselines,
        "max_baseline": round(max_baseline, 4),
        "explanation": explanation,
        "threshold": "target r_partial must exceed all growth baselines",
    }


def f14_phase_shift(values_a: np.ndarray, values_b: np.ndarray,
                    max_shift: int = 5) -> dict:
    """Phase-shift test: true structural bridges decay under index offset.

    From Gemini session April 7. If two sequences are structurally coupled,
    shifting one by k positions should WEAKEN the correlation (phase decay).
    If they merely share a growth rate, shifting doesn't matter — the
    correlation persists at any offset.

    The "A123648 Signature": a genuine bridge (Hecke eigenform ↔ primes)
    shows phase decay. A growth mimic (quadratic ↔ primes) does not.

    Logic:
      1. Compute correlation at shift=0
      2. Compute correlation at shifts 1..max_shift
      3. PASS if correlation decays (monotonically or on average)
      4. FAIL if shifted correlations are as strong as unshifted
    """
    a = np.array(values_a, dtype=float)
    b = np.array(values_b, dtype=float)
    n = min(len(a), len(b))

    if n < 30:
        return {"test": "F14_phase_shift", "verdict": "SKIP",
                "explanation": f"Need >= 30 elements, got {n}"}

    a, b = a[:n], b[:n]

    # Correlation at shift=0
    rho_0 = abs(float(stats.spearmanr(a, b)[0]))
    if rho_0 < 0.1:
        return {"test": "F14_phase_shift", "verdict": "SKIP",
                "explanation": f"Base correlation too weak (rho={rho_0:.4f})"}

    # Correlations at shifted offsets
    shifted_rhos = []
    for k in range(1, max_shift + 1):
        if n - k < 15:
            break
        rho_k = abs(float(stats.spearmanr(a[k:], b[:n-k])[0]))
        shifted_rhos.append(rho_k)

    if not shifted_rhos:
        return {"test": "F14_phase_shift", "verdict": "SKIP",
                "explanation": "Not enough data for shifted correlations"}

    mean_shifted = np.mean(shifted_rhos)
    decay_ratio = mean_shifted / rho_0 if rho_0 > 0 else 1.0

    # FAIL if shifted correlations maintain >90% of unshifted strength
    # (indicates growth artifact, not structural coupling)
    if decay_ratio > 0.90 and rho_0 > 0.5:
        passed = False
        explanation = (f"No phase decay. rho_0={rho_0:.4f}, mean_shifted={mean_shifted:.4f} "
                       f"(decay ratio={decay_ratio:.4f} > 0.90). "
                       f"The correlation persists at arbitrary offsets — likely a growth rate artifact, "
                       f"not structural coupling. Gemini lesson: only phase-decaying bridges are real.")
    else:
        passed = True
        explanation = (f"Phase decay detected. rho_0={rho_0:.4f}, mean_shifted={mean_shifted:.4f} "
                       f"(decay ratio={decay_ratio:.4f}). "
                       f"Correlation weakens with index shift — consistent with structural coupling.")

    return {
        "test": "F14_phase_shift",
        "verdict": "PASS" if passed else "FAIL",
        "rho_0": round(rho_0, 4),
        "shifted_rhos": [round(r, 4) for r in shifted_rhos],
        "mean_shifted": round(mean_shifted, 4),
        "decay_ratio": round(decay_ratio, 4),
        "explanation": explanation,
        "threshold": "decay_ratio must be < 0.90 (or rho_0 < 0.5)",
    }


# ---------------------------------------------------------------------------
# Master Battery Runner
# ---------------------------------------------------------------------------

def classify_kill(results: list[dict], kill_tests: list[str]) -> dict:
    """Diagnose WHY the battery killed a hypothesis.

    Returns a dict with:
      - category: genuine_null | data_problem | resolution_limit | normalization_artifact | borderline
      - confidence: how sure we are this classification is right
      - retry_recommended: should the hypothesis be retried with better data?
      - explanation: human-readable diagnosis

    Kill categories:
      genuine_null      — Effect genuinely doesn't exist. Multiple independent tests agree.
      data_problem      — Data quality or relevance issue, not a real test of the hypothesis.
      resolution_limit  — Effect might exist but is too small for our data to detect.
      normalization_artifact — Sign flips under normalization. Might be scale, not structure.
      borderline        — Close to thresholds. Could go either way with more data.
    """
    kill_set = set(kill_tests)
    test_map = {r["test"]: r for r in results}

    # Count how many tests actually ran (not skipped)
    ran = sum(1 for r in results if r["verdict"] != "SKIP")
    failed = len(kill_tests)
    passed = sum(1 for r in results if r["verdict"] == "PASS")

    # --- Genuine null: multiple independent failures, clear evidence of no effect ---
    if failed >= 4 and "F1_permutation_null" in kill_set and "F3_effect_size" in kill_set:
        return {
            "category": "genuine_null",
            "confidence": "high",
            "retry_recommended": False,
            "explanation": f"Strong null: {failed}/{ran} tests failed including permutation and effect size. "
                          f"The data shows no meaningful difference.",
        }

    # --- Confound artifact: partial correlation killed it (April 5 lesson) ---
    if "F12_partial_correlation" in kill_set:
        f12 = test_map.get("F12_partial_correlation", {})
        return {
            "category": "confound_artifact",
            "confidence": "high",
            "retry_recommended": True,
            "explanation": f"Correlation vanishes after removing shared confound "
                          f"({f12.get('confound', '?')}). "
                          f"Raw rho={f12.get('rho_raw', '?')}, partial rho={f12.get('rho_partial', '?')}. "
                          f"Two quantities that both scale with the same variable will always correlate "
                          f"— remove it and the signal vanishes. "
                          f"Retry with residualized data or a confound-free comparison.",
        }

    # --- Growth rate mimic: correlation is with polynomial growth, not target ---
    if "F13_growth_rate_filter" in kill_set:
        f13 = test_map.get("F13_growth_rate_filter", {})
        return {
            "category": "growth_rate_mimic",
            "confidence": "high",
            "retry_recommended": False,
            "explanation": f"Growth rate mimic — the correlation is with polynomial/exponential growth, "
                          f"not with the specific target. Baselines: {f13.get('baselines', {})}. "
                          f"April 7 lesson: growth kills narratives.",
        }

    # --- Phase artifact: correlation doesn't decay under index shift ---
    if "F14_phase_shift" in kill_set:
        f14 = test_map.get("F14_phase_shift", {})
        return {
            "category": "phase_artifact",
            "confidence": "high",
            "retry_recommended": False,
            "explanation": f"No phase decay — correlation persists at arbitrary index offsets "
                          f"(decay ratio={f14.get('decay_ratio', '?')}). "
                          f"True structural bridges weaken when shifted; growth artifacts don't. "
                          f"Gemini April 7: only phase-decaying bridges are real.",
        }

    # --- Normalization artifact: sign flips under different normalization ---
    if "F5_alternative_normalization" in kill_set:
        f5 = test_map.get("F5_alternative_normalization", {})
        return {
            "category": "normalization_artifact",
            "confidence": "high",
            "retry_recommended": True,
            "explanation": f"Sign flips under normalization — this is likely a scale effect, not structure. "
                          f"Retry with log-transformed or rank-transformed data. "
                          f"d_by_normalization: {f5.get('d_by_normalization', {})}",
        }

    # --- Resolution limit: effect too small but direction is consistent ---
    if kill_set == {"F3_effect_size"} or kill_set == {"F11_cross_validation"}:
        f3 = test_map.get("F3_effect_size", {})
        d = abs(f3.get("cohens_d", 0))
        return {
            "category": "resolution_limit",
            "confidence": "medium",
            "retry_recommended": True,
            "explanation": f"Effect exists (passed permutation) but too small to be meaningful "
                          f"(d={d:.3f} < 0.2). Try finer binning, larger sample, or subpopulation.",
        }

    if kill_set == {"F3_effect_size", "F11_cross_validation"}:
        f3 = test_map.get("F3_effect_size", {})
        f11 = test_map.get("F11_cross_validation", {})
        d = abs(f3.get("cohens_d", 0))
        acc = f11.get("mean_accuracy", 0)
        return {
            "category": "resolution_limit",
            "confidence": "medium",
            "retry_recommended": True,
            "explanation": f"Effect too small (d={d:.3f}) and not predictive (CV acc={acc:.1%}). "
                          f"But passed permutation and normalization — the direction may be real. "
                          f"Try finer resolution or a different parameter.",
        }

    # --- Data problem: only failed on base rate or simpler explanation ---
    if kill_set <= {"F6_base_rate", "F9_simpler_explanation"}:
        return {
            "category": "data_problem",
            "confidence": "low",
            "retry_recommended": True,
            "explanation": f"Failed on statistical correction or baseline comparison, not on the core signal. "
                          f"The effect might be real but our test isn't distinguishing it from noise. "
                          f"Try with more specific data or fewer simultaneous hypotheses.",
        }

    # --- Borderline: passed most tests, failed 1-2 ---
    if failed <= 2 and passed >= 5:
        return {
            "category": "borderline",
            "confidence": "low",
            "retry_recommended": True,
            "explanation": f"Near-miss: {passed}/{ran} passed, only {failed} failed ({kill_tests}). "
                          f"Could be real with better data. Worth retrying with refined search.",
        }

    # --- Default: mixed signals ---
    return {
        "category": "mixed",
        "confidence": "medium",
        "retry_recommended": failed < ran // 2,
        "explanation": f"{failed}/{ran} tests failed: {kill_tests}. "
                      f"No clear pattern — could be data quality or genuine null.",
    }


def run_battery(values_a: np.ndarray, values_b: np.ndarray,
                confounds: dict[str, np.ndarray] = None,
                dose_levels: list[np.ndarray] = None,
                dose_labels: list[str] = None,
                subgroups: dict[str, tuple[np.ndarray, np.ndarray]] = None,
                n_hypotheses_tested: int = 3,
                index_values: np.ndarray = None,
                claim: str = "") -> tuple[str, list[dict]]:
    """Run full 14-test falsification battery.

    Args:
        index_values: Optional array of index/confound values for F12 partial
            correlation test (e.g., prime values if data is indexed by primes).
            If None, F12 uses integer indices as the confound.

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

    # F12: Partial correlation against obvious confounds (April 5 lesson)
    # Skip if either array has fewer than 20 elements
    if len(values_a) >= 20 and len(values_b) >= 20:
        r = f12_partial_correlation(values_a, values_b, index_values=index_values)
    else:
        r = {"test": "F12_partial_correlation", "verdict": "SKIP",
             "reason": f"Need >= 20 elements per group, got {len(values_a)} and {len(values_b)}"}
    results.append(r)

    # F13: Growth rate filter (April 7 lesson)
    # Polynomial/exponential growth mimics structural coupling.
    if len(values_a) >= 15 and len(values_b) >= 15:
        r = f13_growth_rate_filter(values_a, values_b)
    else:
        r = {"test": "F13_growth_rate_filter", "verdict": "SKIP",
             "reason": f"Need >= 15 elements per group, got {len(values_a)} and {len(values_b)}"}
    results.append(r)

    # F14: Phase-shift test (Gemini April 7 lesson)
    # True structural bridges show phase decay; growth artifacts don't.
    if len(values_a) >= 30 and len(values_b) >= 30:
        r = f14_phase_shift(values_a, values_b)
    else:
        r = {"test": "F14_phase_shift", "verdict": "SKIP",
             "reason": f"Need >= 30 elements per group, got {len(values_a)} and {len(values_b)}"}
    results.append(r)

    # Tally
    elapsed = time.time() - t0
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    skipped = sum(1 for r in results if r["verdict"] == "SKIP")
    kill_tests = [r["test"] for r in results if r["verdict"] == "FAIL"]
    verdict = "SURVIVES" if failed == 0 else "KILLED"

    # Diagnose the kill: genuine falsification vs data/methodology problem?
    kill_diagnosis = classify_kill(results, kill_tests) if failed > 0 else "N/A"

    summary = {
        "verdict": verdict,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": len(results),
        "elapsed_s": round(elapsed, 2),
        "kill_tests": kill_tests,
        "kill_diagnosis": kill_diagnosis,
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
    print()

    # Test F12: confound artifact (both quantities scale with index)
    # Simulates the R6 genocide finding: two things that correlate only
    # because they both grow with p (prime). Remove p, signal vanishes.
    p_vals = np.arange(100, 600)  # "primes" (stand-in for any shared index)
    a_confound = 0.5 * p_vals + rng.normal(0, 10, 500)  # scales with p
    b_confound = 0.3 * p_vals + rng.normal(0, 10, 500)  # also scales with p
    print("--- Confound artifact (both scale with index, F12 should kill) ---")
    verdict, results = run_battery(a_confound, b_confound,
                                   index_values=p_vals,
                                   claim="synthetic confound artifact (both scale with p)")
    for r in results:
        print(f"  {r['test']:35s}: {r['verdict']}")
    f12_result = [r for r in results if r["test"] == "F12_partial_correlation"][0]
    print(f"  F12 detail: {f12_result.get('explanation', '')}")
    print(f"  VERDICT: {verdict}")
