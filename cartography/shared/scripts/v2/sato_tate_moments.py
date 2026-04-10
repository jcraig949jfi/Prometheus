"""
Sato-Tate Moment Classification of 66K Genus-2 Curves
======================================================
Classify genus-2 curves by their Sato-Tate group using normalized moment
centroids computed from Euler factor coefficients (a_p and b_p).

For genus-2 curves, the Euler factor at a good prime p is:
    L_p(s) = 1 - a_p*p^{-s} + b_p*p^{-2s} - a_p*p^{1-3s} + p^{2-4s}

We normalize:
    x_p = a_p / (2*sqrt(p))    (trace Sato-Tate variable)
    y_p = (b_p - 1) / p         (second coefficient, shifted & scaled)

and compute moments M_k(x) and M_k(y) for k=1..8, plus mixed moments.
This gives a 20-dimensional feature vector per curve.

Data source: gce_1000000_lmfdb.txt (good Euler factor coefficients)
"""

import ast
import json
import math
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
import time

DATA_DIR = Path("F:/Prometheus/cartography/genus2/data/g2c-data")
LMFDB_FILE = DATA_DIR / "gce_1000000_lmfdb.txt"
OUTPUT_FILE = Path("F:/Prometheus/cartography/shared/scripts/v2/sato_tate_moments_results.json")

MAX_K = 8  # moments up to order 8


def parse_lmfdb_line(line):
    """Parse a line from gce_1000000_lmfdb.txt."""
    parts = line.strip().split(":")
    if len(parts) < 17:
        return None
    disc = parts[0]
    cond = parts[1]
    lhash = parts[2]
    st_group = parts[8].strip()
    label_key = f"{disc}:{cond}:{lhash}"
    gf_str = parts[16]
    try:
        gf = ast.literal_eval(gf_str)
    except Exception:
        return None
    return label_key, st_group, gf


def compute_features(good_lfactors):
    """Compute feature vector from Euler factor coefficients.

    Features (20-dim):
    - M_k(x) for k=1..8 where x = a_p / (2*sqrt(p))
    - M_k(y) for k=1..8 where y = (b_p - 1) / p
    - Mixed: mean(x*y), mean(x^2*y), mean(x*y^2), mean(x^2*y^2)
    """
    xs, ys = [], []
    for entry in good_lfactors:
        p, a_p, b_p = entry[0], entry[1], entry[2]
        if p < 2:
            continue
        x = a_p / (2.0 * math.sqrt(p))
        y = (b_p - 1.0) / p
        xs.append(x)
        ys.append(y)

    if len(xs) < 5:
        return None

    xs = np.array(xs)
    ys = np.array(ys)

    features = []
    # x moments 1..8
    for k in range(1, MAX_K + 1):
        features.append(float(np.mean(xs ** k)))
    # y moments 1..8
    for k in range(1, MAX_K + 1):
        features.append(float(np.mean(ys ** k)))
    # Mixed moments
    features.append(float(np.mean(xs * ys)))
    features.append(float(np.mean(xs**2 * ys)))
    features.append(float(np.mean(xs * ys**2)))
    features.append(float(np.mean(xs**2 * ys**2)))

    return features


def classify_nearest_centroid(features_matrix, labels, centroids_dict, group_names,
                              centroid_matrix, use_mahalanobis=False, cov_inv=None):
    """Classify each curve by nearest centroid. Returns predictions."""
    if use_mahalanobis and cov_inv is not None:
        # Mahalanobis distance
        preds = []
        for m in features_matrix:
            diffs = centroid_matrix - m
            dists = np.array([diff @ cov_inv @ diff for diff in diffs])
            preds.append(group_names[np.argmin(dists)])
        return preds
    else:
        # Euclidean
        preds = []
        for m in features_matrix:
            dists = np.linalg.norm(centroid_matrix - m, axis=1)
            preds.append(group_names[np.argmin(dists)])
        return preds


def evaluate(true_labels, pred_labels, st_groups, tag=""):
    """Compute and print accuracy metrics."""
    correct = sum(t == p for t, p in zip(true_labels, pred_labels))
    total = len(true_labels)
    overall_acc = correct / total if total > 0 else 0

    per_group_correct = Counter()
    per_group_total = Counter()
    confusion = defaultdict(Counter)

    for t, p in zip(true_labels, pred_labels):
        per_group_total[t] += 1
        confusion[t][p] += 1
        if t == p:
            per_group_correct[t] += 1

    print(f"\n{'='*60}")
    print(f"CLASSIFICATION RESULTS {tag}")
    print(f"{'='*60}")
    print(f"Overall accuracy: {correct}/{total} = {overall_acc:.4%}")

    print(f"\nPer-group accuracy:")
    per_group_acc = {}
    for g in sorted(per_group_total.keys(), key=lambda g: -per_group_total[g]):
        n = per_group_total[g]
        c = per_group_correct[g]
        acc = c / n if n > 0 else 0
        per_group_acc[g] = {"correct": c, "total": n, "accuracy": round(acc, 6)}
        print(f"  {g:25s}: {c:5d}/{n:5d} = {acc:.4%}")

    return overall_acc, correct, per_group_acc, dict(confusion)


def main():
    t0 = time.time()
    print("Loading genus-2 curves from lmfdb.txt ...")

    curves = {}  # label_key -> (st_group, features)
    skipped = 0
    duplicate = 0

    with open(LMFDB_FILE, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            result = parse_lmfdb_line(line)
            if result is None:
                skipped += 1
                continue
            label_key, st_group, gf = result
            if label_key in curves:
                duplicate += 1
                continue
            features = compute_features(gf)
            if features is None:
                skipped += 1
                continue
            curves[label_key] = (st_group, features)
            if (i + 1) % 10000 == 0:
                print(f"  Parsed {i+1} lines, {len(curves)} unique curves ...")

    print(f"Loaded {len(curves)} unique curves ({duplicate} duplicates, {skipped} skipped)")

    # Build arrays
    all_keys = list(curves.keys())
    all_labels = [curves[k][0] for k in all_keys]
    all_features = np.array([curves[k][1] for k in all_keys])

    # Group by ST group
    st_groups = defaultdict(list)
    for idx, k in enumerate(all_keys):
        st_groups[curves[k][0]].append(idx)

    print(f"\nST group distribution ({len(st_groups)} groups):")
    for g in sorted(st_groups.keys(), key=lambda g: -len(st_groups[g])):
        print(f"  {g}: {len(st_groups[g])}")

    # Compute centroids
    group_names = sorted(st_groups.keys(), key=lambda g: -len(st_groups[g]))
    centroids = {}
    for g in group_names:
        idxs = st_groups[g]
        centroids[g] = all_features[idxs].mean(axis=0)

    centroid_matrix = np.array([centroids[g] for g in group_names])

    # Print centroids (first 6 = a_p moments)
    print(f"\nST group centroids (first 6 a_p moments):")
    for g in group_names:
        c = centroids[g]
        mstr = ", ".join(f"{v:.6f}" for v in c[:6])
        print(f"  {g:25s} (n={len(st_groups[g]):5d}): [{mstr}]")

    # =========================================================================
    # Method 1: Euclidean nearest centroid (raw features)
    # =========================================================================
    print("\n--- Method 1: Euclidean nearest centroid (20-dim) ---")
    preds1 = classify_nearest_centroid(all_features, all_labels, centroids,
                                        group_names, centroid_matrix)
    acc1, corr1, pga1, conf1 = evaluate(all_labels, preds1, st_groups,
                                          tag="[Euclidean, 20-dim]")

    # =========================================================================
    # Method 2: Standardized Euclidean (z-score features)
    # =========================================================================
    print("\n--- Method 2: Standardized Euclidean ---")
    feat_mean = all_features.mean(axis=0)
    feat_std = all_features.std(axis=0)
    feat_std[feat_std < 1e-12] = 1.0
    all_features_z = (all_features - feat_mean) / feat_std

    centroids_z = {}
    for g in group_names:
        idxs = st_groups[g]
        centroids_z[g] = all_features_z[idxs].mean(axis=0)
    centroid_matrix_z = np.array([centroids_z[g] for g in group_names])

    preds2 = classify_nearest_centroid(all_features_z, all_labels, centroids_z,
                                        group_names, centroid_matrix_z)
    acc2, corr2, pga2, conf2 = evaluate(all_labels, preds2, st_groups,
                                          tag="[Standardized Euclidean, 20-dim]")

    # =========================================================================
    # Method 3: Mahalanobis distance (using pooled within-group covariance)
    # =========================================================================
    print("\n--- Method 3: Mahalanobis distance ---")
    # Pooled within-group covariance
    n_features = all_features.shape[1]
    S_w = np.zeros((n_features, n_features))
    for g in group_names:
        idxs = st_groups[g]
        if len(idxs) < 2:
            continue
        X_g = all_features[idxs]
        X_g_centered = X_g - X_g.mean(axis=0)
        S_w += X_g_centered.T @ X_g_centered
    S_w /= (len(all_keys) - len(group_names))
    # Regularize
    S_w += np.eye(n_features) * 1e-6
    try:
        cov_inv = np.linalg.inv(S_w)
        preds3 = classify_nearest_centroid(all_features, all_labels, centroids,
                                            group_names, centroid_matrix,
                                            use_mahalanobis=True, cov_inv=cov_inv)
        acc3, corr3, pga3, conf3 = evaluate(all_labels, preds3, st_groups,
                                              tag="[Mahalanobis, 20-dim]")
    except np.linalg.LinAlgError:
        print("  Covariance matrix singular, skipping Mahalanobis")
        acc3, corr3, pga3, conf3 = 0, 0, {}, {}
        preds3 = preds2

    # =========================================================================
    # Pick best method for detailed analysis
    # =========================================================================
    best_method = max([(acc1, "Euclidean", preds1, pga1, conf1),
                       (acc2, "Standardized", preds2, pga2, conf2),
                       (acc3, "Mahalanobis", preds3, pga3, conf3)],
                      key=lambda x: x[0])
    best_acc, best_name, best_preds, best_pga, best_conf = best_method
    print(f"\nBest method: {best_name} ({best_acc:.4%})")

    # Detailed confusion for best method
    confusion = defaultdict(Counter)
    misclassified = []
    for idx, (t, p) in enumerate(zip(all_labels, best_preds)):
        confusion[t][p] += 1
        if t != p:
            k = all_keys[idx]
            misclassified.append({
                "label": k,
                "true_group": t,
                "predicted_group": p,
                "moments_a": list(all_features[idx][:6]),
                "moments_b": list(all_features[idx][8:14]),
            })

    # Print confusion for non-generic groups
    non_generic = sorted([g for g in group_names if g != "USp(4)"],
                         key=lambda g: -len(st_groups[g]))

    print(f"\nConfusion highlights (non-generic, best method):")
    for true_g in non_generic:
        n = len(st_groups[true_g])
        correct = confusion[true_g][true_g]
        errors = [(pg, cnt) for pg, cnt in confusion[true_g].items()
                  if pg != true_g and cnt > 0]
        errors.sort(key=lambda x: -x[1])
        err_str = ", ".join(f"{pg}:{cnt}" for pg, cnt in errors[:5])
        print(f"  {true_g:25s} ({n:4d}): {correct:4d} correct | errors: {err_str}")

    # USp(4) leakage into non-generic
    print(f"\n  USp(4) misclassified as non-generic:")
    usp4_errors = [(pg, cnt) for pg, cnt in confusion["USp(4)"].items()
                   if pg != "USp(4)" and cnt > 0]
    usp4_errors.sort(key=lambda x: -x[1])
    for pg, cnt in usp4_errors[:10]:
        print(f"    -> {pg}: {cnt}")

    # Rare group analysis
    rare_groups = [g for g in group_names if len(st_groups[g]) <= 10]
    print(f"\nRare groups ({len(rare_groups)} groups):")
    for g in rare_groups:
        n = len(st_groups[g])
        correct = confusion[g][g]
        print(f"  {g:25s}: {correct}/{n} correct")

    # LOO for small groups with best method features
    print(f"\nLeave-one-out for small groups (n <= 50):")
    loo_results = {}
    for g in group_names:
        n = len(st_groups[g])
        if n < 2 or n > 50:
            continue
        idxs = st_groups[g]
        loo_correct = 0
        for i, test_idx in enumerate(idxs):
            # Recompute centroid for g without test point
            other_idxs = [j for j in idxs if j != test_idx]
            loo_centroid = all_features[other_idxs].mean(axis=0)

            test_feat = all_features[test_idx]
            best_dist = float("inf")
            best_g = None
            for g2 in group_names:
                if g2 == g:
                    c = loo_centroid
                else:
                    c = centroids[g2]
                d = np.linalg.norm(c - test_feat)
                if d < best_dist:
                    best_dist = d
                    best_g = g2
            if best_g == g:
                loo_correct += 1

        loo_acc = loo_correct / n
        loo_results[g] = {"correct": loo_correct, "total": n, "accuracy": round(loo_acc, 6)}
        print(f"  {g:25s}: {loo_correct:3d}/{n:3d} = {loo_acc:.4%}")

    # =========================================================================
    # Build and save results
    # =========================================================================
    results = {
        "summary": {
            "total_curves": len(all_keys),
            "unique_st_groups": len(st_groups),
            "num_features": int(all_features.shape[1]),
            "primes_per_curve": "~24 (primes up to 97)",
            "elapsed_seconds": round(time.time() - t0, 1),
        },
        "method_comparison": {
            "Euclidean_20dim": {"accuracy": round(acc1, 6), "correct": corr1},
            "Standardized_20dim": {"accuracy": round(acc2, 6), "correct": corr2},
            "Mahalanobis_20dim": {"accuracy": round(acc3, 6), "correct": int(corr3)},
            "best_method": best_name,
        },
        "st_group_distribution": {g: len(st_groups[g]) for g in group_names},
        "centroids_a_moments": {
            g: [round(v, 8) for v in centroids[g][:6]] for g in group_names
        },
        "centroids_b_moments": {
            g: [round(v, 8) for v in centroids[g][8:14]] for g in group_names
        },
        "per_group_accuracy": best_pga,
        "confusion_matrix": {
            tg: dict(pc) for tg, pc in confusion.items()
        },
        "loo_small_groups": loo_results,
        "misclassified_count": len(misclassified),
        "misclassified_examples": misclassified[:100],
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_FILE}")
    print(f"Elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
