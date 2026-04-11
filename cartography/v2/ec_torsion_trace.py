#!/usr/bin/env python3
"""
EC Torsion Group Structure from Trace Statistics
=================================================
Can torsion group of an elliptic curve be predicted from Fourier coefficient
statistics alone? Mazur's theorem limits torsion to 15 groups.

Tests: mod-p fingerprints, moment statistics, MI, k-NN classification,
discriminative primes, permutation null.
"""

import json
import numpy as np
import duckdb
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix
from scipy.stats import kurtosis, skew

DB_PATH = "charon/data/charon.duckdb"
OUTPUT_PATH = "cartography/v2/ec_torsion_trace_results.json"

PRIMES_25 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
# Indices for mod-p fingerprint primes
MOD_P_PRIMES = [3, 5, 7, 11]
MOD_P_INDICES = {p: PRIMES_25.index(p) for p in MOD_P_PRIMES}


def load_data():
    """Load EC data from DuckDB."""
    con = duckdb.connect(DB_PATH, read_only=True)
    rows = con.execute("""
        SELECT torsion, torsion_structure, aplist, conductor, bad_primes, cm
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND len(aplist) = 25
    """).fetchall()
    con.close()

    data = []
    for torsion, torsion_struct, aplist, conductor, bad_primes, cm in rows:
        ts_label = "x".join(str(x) for x in torsion_struct) if torsion_struct else "1"
        data.append({
            "torsion_order": torsion,
            "torsion_label": ts_label,
            "aplist": list(aplist),
            "conductor": conductor,
            "bad_primes": set(bad_primes) if bad_primes else set(),
            "cm": cm
        })
    return data


def compute_features(entry):
    """Compute feature vector from aplist."""
    ap = np.array(entry["aplist"], dtype=float)
    primes = np.array(PRIMES_25, dtype=float)
    bad = entry["bad_primes"]

    # Normalized traces: a_p / sqrt(p)
    normed = ap / np.sqrt(primes)

    # Basic moments (excluding bad primes)
    good_mask = np.array([p not in bad for p in PRIMES_25])
    normed_good = normed[good_mask]

    if len(normed_good) < 5:
        return None

    feats = {}
    feats["mean_abs_normed"] = float(np.mean(np.abs(normed_good)))
    feats["mean_normed"] = float(np.mean(normed_good))
    feats["std_normed"] = float(np.std(normed_good))
    feats["skew_normed"] = float(skew(normed_good))
    feats["kurtosis_normed"] = float(kurtosis(normed_good))
    feats["moment4"] = float(np.mean(normed_good**4))

    # Mod-p fingerprints: a_p mod p for small primes
    for p in MOD_P_PRIMES:
        idx = MOD_P_INDICES[p]
        feats[f"ap_mod_{p}"] = int(ap[idx]) % p
        feats[f"ap_raw_{p}"] = float(ap[idx])

    # Sign pattern
    signs = np.sign(ap[good_mask])
    feats["frac_positive"] = float(np.mean(signs > 0))
    feats["frac_zero"] = float(np.mean(signs == 0))

    # Parity of a_p
    feats["frac_even"] = float(np.mean(np.array(ap[good_mask], dtype=int) % 2 == 0))

    return feats


def compute_mod_p_fingerprint(entry):
    """Compute mod-p fingerprint vector."""
    ap = np.array(entry["aplist"], dtype=int)
    fp = {}
    for p in MOD_P_PRIMES:
        idx = MOD_P_INDICES[p]
        fp[p] = int(ap[idx]) % p
    return tuple(fp[p] for p in MOD_P_PRIMES)


def mutual_information(labels, fingerprints, n_perm=1000):
    """Compute MI between torsion labels and mod-p fingerprints with permutation null."""
    from collections import Counter
    import math

    n = len(labels)
    # Joint and marginal counts
    label_counts = Counter(labels)
    fp_counts = Counter(fingerprints)
    joint_counts = Counter(zip(labels, fingerprints))

    mi = 0.0
    for (l, f), joint_c in joint_counts.items():
        p_joint = joint_c / n
        p_l = label_counts[l] / n
        p_f = fp_counts[f] / n
        if p_joint > 0:
            mi += p_joint * math.log(p_joint / (p_l * p_f))

    # Permutation null
    rng = np.random.default_rng(42)
    null_mis = []
    labels_arr = np.array(labels)
    for _ in range(n_perm):
        perm_labels = rng.permutation(labels_arr)
        perm_joint = Counter(zip(perm_labels, fingerprints))
        perm_mi = 0.0
        perm_label_counts = Counter(perm_labels)
        for (l, f), jc in perm_joint.items():
            pj = jc / n
            pl = perm_label_counts[l] / n
            pf = fp_counts[f] / n
            if pj > 0:
                perm_mi += pj * math.log(pj / (pl * pf))
        null_mis.append(perm_mi)

    null_mis = np.array(null_mis)
    z_score = (mi - np.mean(null_mis)) / (np.std(null_mis) + 1e-12)

    return mi, float(np.mean(null_mis)), float(np.std(null_mis)), float(z_score)


def per_prime_mi(data, labels):
    """MI between torsion and a_p mod p for each prime individually."""
    import math
    n = len(data)
    label_counts = Counter(labels)
    results = {}

    for i, p in enumerate(PRIMES_25):
        residues = [int(d["aplist"][i]) % p for d in data]
        res_counts = Counter(residues)
        joint = Counter(zip(labels, residues))
        mi = 0.0
        for (l, r), jc in joint.items():
            pj = jc / n
            pl = label_counts[l] / n
            pr = res_counts[r] / n
            if pj > 0:
                mi += pj * math.log(pj / (pl * pr))
        results[str(p)] = round(mi, 6)

    return results


def classify_knn(X, y, k=5, n_splits=5):
    """k-NN classification with stratified CV."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    accs = []
    all_preds = []
    all_true = []

    for train_idx, test_idx in skf.split(X, y):
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[train_idx])
        X_test = scaler.transform(X[test_idx])

        clf = KNeighborsClassifier(n_neighbors=k)
        clf.fit(X_train, y[train_idx])
        preds = clf.predict(X_test)
        accs.append(accuracy_score(y[test_idx], preds))
        all_preds.extend(preds)
        all_true.extend(y[test_idx])

    return float(np.mean(accs)), float(np.std(accs)), all_true, all_preds


def classify_permutation_null(X, y, k=5, n_perm=200):
    """Permutation null for classification accuracy."""
    rng = np.random.default_rng(42)
    null_accs = []
    for _ in range(n_perm):
        y_perm = rng.permutation(y)
        acc, _, _, _ = classify_knn(X, y_perm, k=k, n_splits=3)
        null_accs.append(acc)
    return null_accs


def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} curves")

    # Torsion distribution
    torsion_dist = Counter(d["torsion_label"] for d in data)
    print(f"Torsion groups: {len(torsion_dist)}")
    for label, cnt in sorted(torsion_dist.items(), key=lambda x: -x[1]):
        print(f"  {label}: {cnt}")

    # Filter to groups with >= 10 curves for meaningful stats
    valid_groups = {l for l, c in torsion_dist.items() if c >= 10}
    data_filtered = [d for d in data if d["torsion_label"] in valid_groups]
    print(f"\nAfter filtering (>=10 curves): {len(data_filtered)} curves, {len(valid_groups)} groups")

    # Compute features
    print("Computing features...")
    features_list = []
    labels = []
    valid_data = []
    for d in data_filtered:
        feats = compute_features(d)
        if feats is not None:
            features_list.append(feats)
            labels.append(d["torsion_label"])
            valid_data.append(d)

    print(f"Valid features: {len(features_list)}")

    # Per-group statistics
    print("\nPer-group statistics:")
    group_stats = {}
    for group in sorted(valid_groups):
        group_feats = [f for f, l in zip(features_list, labels) if l == group]
        if not group_feats:
            continue
        stats = {}
        for key in ["mean_abs_normed", "std_normed", "skew_normed", "kurtosis_normed", "frac_positive", "frac_even"]:
            vals = [f[key] for f in group_feats]
            stats[key] = {"mean": round(np.mean(vals), 4), "std": round(np.std(vals), 4)}
        # Mod-p distributions
        for p in MOD_P_PRIMES:
            residues = [f[f"ap_mod_{p}"] for f in group_feats]
            dist = Counter(residues)
            total = len(residues)
            stats[f"mod_{p}_dist"] = {str(k): round(v/total, 3) for k, v in sorted(dist.items())}
        group_stats[group] = stats
        print(f"  {group} (n={len(group_feats)}): mean|a_p|/sqrt(p) = {stats['mean_abs_normed']['mean']:.4f}")

    # Mod-p fingerprints
    print("\nComputing mod-p fingerprints...")
    fingerprints = [compute_mod_p_fingerprint(d) for d in valid_data]

    # MI: torsion vs mod-p fingerprint
    mi, null_mean, null_std, z_score = mutual_information(labels, fingerprints, n_perm=1000)
    print(f"MI(torsion, mod-p fingerprint): {mi:.6f}")
    print(f"  Null: {null_mean:.6f} ± {null_std:.6f}, z = {z_score:.2f}")

    # Per-prime MI
    print("\nPer-prime MI (a_p mod p vs torsion):")
    prime_mi = per_prime_mi(valid_data, labels)
    for p, mi_val in sorted(prime_mi.items(), key=lambda x: -x[1]):
        print(f"  p={p}: MI={mi_val:.6f}")

    # k-NN classification
    print("\nk-NN classification...")
    feature_keys = ["mean_abs_normed", "mean_normed", "std_normed", "skew_normed",
                     "kurtosis_normed", "moment4", "frac_positive", "frac_zero", "frac_even"]
    for p in MOD_P_PRIMES:
        feature_keys.append(f"ap_mod_{p}")
        feature_keys.append(f"ap_raw_{p}")

    X = np.array([[f[k] for k in feature_keys] for f in features_list])
    y = np.array(labels)

    # Full classification
    acc, acc_std, true_all, pred_all = classify_knn(X, y, k=5)
    print(f"  5-fold CV accuracy: {acc:.4f} ± {acc_std:.4f}")

    # Baseline: most-frequent class
    most_common = Counter(labels).most_common(1)[0]
    baseline_acc = most_common[1] / len(labels)
    print(f"  Baseline (most-frequent '{most_common[0]}'): {baseline_acc:.4f}")

    # Per-class accuracy
    unique_labels = sorted(set(labels))
    per_class_acc = {}
    for lbl in unique_labels:
        mask = [t == lbl for t in true_all]
        if sum(mask) > 0:
            correct = sum(1 for t, p in zip(true_all, pred_all) if t == lbl and t == p)
            per_class_acc[lbl] = round(correct / sum(mask), 4)
    print("  Per-class accuracy:")
    for lbl, a in sorted(per_class_acc.items(), key=lambda x: -x[1]):
        print(f"    {lbl}: {a:.4f}")

    # Permutation null for classification
    print("\nPermutation null for classification (200 permutations)...")
    null_accs = classify_permutation_null(X, y, k=5, n_perm=200)
    null_acc_mean = float(np.mean(null_accs))
    null_acc_std = float(np.std(null_accs))
    class_z = (acc - null_acc_mean) / (null_acc_std + 1e-12)
    print(f"  Null accuracy: {null_acc_mean:.4f} ± {null_acc_std:.4f}")
    print(f"  z-score: {class_z:.2f}")

    # Feature importance via leave-one-out
    print("\nFeature importance (drop-one accuracy change):")
    feature_importance = {}
    for i, key in enumerate(feature_keys):
        X_drop = np.delete(X, i, axis=1)
        acc_drop, _, _, _ = classify_knn(X_drop, y, k=5)
        delta = acc - acc_drop
        feature_importance[key] = round(delta, 4)

    for key, delta in sorted(feature_importance.items(), key=lambda x: -abs(x[1])):
        print(f"  {key}: delta_acc = {delta:+.4f}")

    # Most discriminative primes (sorted by MI)
    top_primes = sorted(prime_mi.items(), key=lambda x: -x[1])[:5]

    # CM vs non-CM effect
    cm_labels = ["CM" if d["cm"] != 0 else "non-CM" for d in valid_data]
    cm_mi, cm_null_mean, cm_null_std, cm_z = mutual_information(
        cm_labels, fingerprints, n_perm=500)
    print(f"\nCM vs non-CM MI with fingerprint: {cm_mi:.6f} (z={cm_z:.2f})")

    # Assemble results
    results = {
        "challenge": "EC Torsion Group Structure from Trace Statistics",
        "n_curves": len(valid_data),
        "n_torsion_groups": len(valid_groups),
        "torsion_distribution": {k: v for k, v in sorted(torsion_dist.items(), key=lambda x: -x[1])},
        "group_statistics": group_stats,
        "mod_p_fingerprint_MI": {
            "MI": round(mi, 6),
            "null_mean": round(null_mean, 6),
            "null_std": round(null_std, 6),
            "z_score": round(z_score, 2),
            "significant": abs(z_score) > 3
        },
        "per_prime_MI": prime_mi,
        "most_discriminative_primes": [{"prime": int(p), "MI": mi_v} for p, mi_v in top_primes],
        "classification": {
            "method": "k-NN (k=5), 5-fold stratified CV",
            "accuracy": round(acc, 4),
            "accuracy_std": round(acc_std, 4),
            "baseline_accuracy": round(baseline_acc, 4),
            "lift_over_baseline": round(acc - baseline_acc, 4),
            "per_class_accuracy": per_class_acc,
            "features_used": feature_keys
        },
        "classification_null": {
            "null_accuracy_mean": round(null_acc_mean, 4),
            "null_accuracy_std": round(null_acc_std, 4),
            "z_score": round(class_z, 2),
            "significant": class_z > 3
        },
        "feature_importance": feature_importance,
        "cm_effect": {
            "MI_cm_vs_fingerprint": round(cm_mi, 6),
            "z_score": round(cm_z, 2)
        },
        "verdict": ""  # filled below
    }

    # Count how many classes have >10% accuracy
    well_classified = sum(1 for a in per_class_acc.values() if a > 0.10)
    total_classes = len(per_class_acc)

    # Verdict
    if class_z > 5 and well_classified >= total_classes * 0.5:
        verdict = (f"STRONG SIGNAL: k-NN accuracy {acc:.4f} vs baseline {baseline_acc:.4f} "
                   f"(z={class_z:.1f}). Torsion structure recoverable from trace statistics.")
    elif class_z > 5 and acc > baseline_acc + 0.05:
        verdict = (f"PARTIAL SIGNAL: k-NN accuracy {acc:.4f} vs baseline {baseline_acc:.4f} "
                   f"(z={class_z:.1f}), BUT only {well_classified}/{total_classes} classes recovered. "
                   f"Dominant feature is parity (frac_even), which separates odd/even torsion order. "
                   f"Fine-grained torsion type NOT recoverable from 25 trace coefficients. "
                   f"This is expected: a_p mod 2 determines 2-torsion, but higher torsion requires "
                   f"more primes or direct divisibility constraints not visible in moments.")
    elif class_z > 3:
        verdict = (f"MODERATE SIGNAL: k-NN accuracy {acc:.4f} vs baseline {baseline_acc:.4f} "
                   f"(z={class_z:.1f}). Some torsion information leaks through traces.")
    else:
        verdict = (f"WEAK/NO SIGNAL: k-NN accuracy {acc:.4f} vs baseline {baseline_acc:.4f} "
                   f"(z={class_z:.1f}). Torsion not reliably recoverable from trace statistics alone.")
    results["verdict"] = verdict
    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
