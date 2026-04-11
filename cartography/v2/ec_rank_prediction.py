#!/usr/bin/env python3
"""
EC Rank Prediction from a_p Statistics
=======================================
Can simple Fourier coefficient statistics predict elliptic curve rank?

Uses: logistic regression, k-NN, random forest on features derived from aplist.
Binary (rank=0 vs rank>=1) and 3-class (rank 0 vs 1 vs 2+) classification.
"""

import json
import numpy as np
import duckdb
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, make_scorer, f1_score

# ── Config ──────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "ec_rank_prediction_results.json"

# First 25 primes (aplist indices)
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
             53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def load_data():
    """Load EC data from DuckDB."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(
        "SELECT rank, aplist, conductor FROM elliptic_curves WHERE aplist IS NOT NULL AND rank IS NOT NULL"
    ).fetchdf()
    con.close()
    return df


def compute_features(df):
    """Compute statistical features from aplist."""
    primes = np.array(PRIMES_25, dtype=float)
    sqrt_p = np.sqrt(primes)

    records = []
    for _, row in df.iterrows():
        ap = np.array(row["aplist"], dtype=float)
        if len(ap) < 25:
            continue

        ap = ap[:25]
        ap_norm = ap / sqrt_p  # Sato-Tate normalized

        # (a) mean |a_p| / sqrt(p)
        mean_abs_norm = np.mean(np.abs(ap_norm))

        # (b) variance of a_p / sqrt(p)
        var_norm = np.var(ap_norm)

        # (c) fraction of a_p = 0 (supersingular primes)
        frac_zero = np.mean(ap == 0)

        # (d) mean sign(a_p)
        mean_sign = np.mean(np.sign(ap))

        # (e) median |a_p|
        median_abs = np.median(np.abs(ap))

        # (f) Moments M2-M6 of a_p/sqrt(p)
        m2 = np.mean(ap_norm**2)
        m3 = np.mean(ap_norm**3)
        m4 = np.mean(ap_norm**4)
        m5 = np.mean(ap_norm**5)
        m6 = np.mean(ap_norm**6)

        # (g) Phase coherence R (mean resultant length of phases)
        # theta_p = arccos(a_p / (2*sqrt(p))), clipped to valid range
        cos_theta = np.clip(ap / (2.0 * sqrt_p), -1, 1)
        theta = np.arccos(cos_theta)
        # R = |mean(e^{i*theta})|
        z = np.exp(1j * theta)
        R = np.abs(np.mean(z))

        # (h) Skewness and kurtosis
        std_norm = np.std(ap_norm)
        if std_norm > 0:
            skew = np.mean(((ap_norm - np.mean(ap_norm)) / std_norm)**3)
            kurt = np.mean(((ap_norm - np.mean(ap_norm)) / std_norm)**4) - 3
        else:
            skew = 0.0
            kurt = 0.0

        # (i) log conductor
        log_cond = np.log(float(row["conductor"]) + 1)

        records.append({
            "rank": int(row["rank"]),
            "mean_abs_norm": mean_abs_norm,
            "var_norm": var_norm,
            "frac_zero": frac_zero,
            "mean_sign": mean_sign,
            "median_abs": median_abs,
            "m2": m2, "m3": m3, "m4": m4, "m5": m5, "m6": m6,
            "phase_coherence_R": R,
            "skewness": skew,
            "kurtosis": kurt,
            "log_conductor": log_cond,
        })

    return records


def run_classification(X, y, label, class_names):
    """Run 3 classifiers with stratified 5-fold CV."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, random_state=42))
        ]),
        "knn_k5": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(n_neighbors=5))
        ]),
        "random_forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1))
        ]),
    }

    scoring = {
        "accuracy": "accuracy",
        "f1_macro": "f1_macro",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
    }

    results = {}
    for name, pipe in models.items():
        cv_results = cross_validate(pipe, X, y, cv=cv, scoring=scoring, return_train_score=False)
        results[name] = {
            "accuracy": float(np.mean(cv_results["test_accuracy"])),
            "accuracy_std": float(np.std(cv_results["test_accuracy"])),
            "f1_macro": float(np.mean(cv_results["test_f1_macro"])),
            "precision_macro": float(np.mean(cv_results["test_precision_macro"])),
            "recall_macro": float(np.mean(cv_results["test_recall_macro"])),
        }
        print(f"  {name}: acc={results[name]['accuracy']:.4f}±{results[name]['accuracy_std']:.4f}  "
              f"F1={results[name]['f1_macro']:.4f}")

    return results


def get_feature_importance(X, y, feature_names):
    """Fit random forest and extract feature importances."""
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1))
    ])
    pipe.fit(X, y)
    importances = pipe.named_steps["clf"].feature_importances_
    ranked = sorted(zip(feature_names, importances), key=lambda x: -x[1])
    return {name: float(imp) for name, imp in ranked}


def main():
    print("Loading data...")
    df = load_data()
    print(f"  {len(df)} curves loaded")

    print("Computing features...")
    records = compute_features(df)
    print(f"  {len(records)} curves with valid features")

    feature_names = [
        "mean_abs_norm", "var_norm", "frac_zero", "mean_sign", "median_abs",
        "m2", "m3", "m4", "m5", "m6",
        "phase_coherence_R", "skewness", "kurtosis", "log_conductor"
    ]

    X = np.array([[r[f] for f in feature_names] for r in records])
    ranks = np.array([r["rank"] for r in records])

    # ── Class distribution ──
    unique, counts = np.unique(ranks, return_counts=True)
    rank_dist = {int(u): int(c) for u, c in zip(unique, counts)}
    print(f"  Rank distribution: {rank_dist}")
    total = len(ranks)

    # ── Baselines ──
    majority_binary = max(np.sum(ranks == 0), np.sum(ranks >= 1)) / total
    majority_3class = max(counts) / total
    print(f"  Majority baseline (binary): {majority_binary:.4f}")
    print(f"  Majority baseline (3-class): {majority_3class:.4f}")

    # ── Binary classification: rank=0 vs rank>=1 ──
    print("\n=== Binary Classification (rank=0 vs rank>=1) ===")
    y_binary = (ranks >= 1).astype(int)
    binary_results = run_classification(X, y_binary, "binary", ["rank=0", "rank>=1"])

    # ── 3-class classification ──
    print("\n=== 3-Class Classification (rank 0 vs 1 vs 2+) ===")
    y_3class = np.where(ranks == 0, 0, np.where(ranks == 1, 1, 2))
    three_class_results = run_classification(X, y_3class, "3-class", ["rank=0", "rank=1", "rank=2+"])

    # ── Feature importance (binary) ──
    print("\n=== Feature Importance (binary, Random Forest) ===")
    fi_binary = get_feature_importance(X, y_binary, feature_names)
    for name, imp in fi_binary.items():
        print(f"  {name:25s}: {imp:.4f}")

    # ── Feature importance (3-class) ──
    print("\n=== Feature Importance (3-class, Random Forest) ===")
    fi_3class = get_feature_importance(X, y_3class, feature_names)
    for name, imp in fi_3class.items():
        print(f"  {name:25s}: {imp:.4f}")

    # ── Assemble results ──
    output = {
        "metadata": {
            "task": "EC rank prediction from a_p statistics",
            "n_curves": len(records),
            "n_features": len(feature_names),
            "features": feature_names,
            "primes_used": PRIMES_25,
            "rank_distribution": rank_dist,
        },
        "baselines": {
            "majority_binary": round(majority_binary, 4),
            "majority_3class": round(majority_3class, 4),
        },
        "binary_classification": binary_results,
        "three_class_classification": three_class_results,
        "feature_importance_binary": fi_binary,
        "feature_importance_3class": fi_3class,
        "summary": {},  # filled below
    }

    # ── Summary ──
    best_binary = max(binary_results.items(), key=lambda x: x[1]["accuracy"])
    best_3class = max(three_class_results.items(), key=lambda x: x[1]["accuracy"])
    output["summary"] = {
        "best_binary_model": best_binary[0],
        "best_binary_accuracy": best_binary[1]["accuracy"],
        "binary_lift_over_baseline": round(best_binary[1]["accuracy"] - majority_binary, 4),
        "best_3class_model": best_3class[0],
        "best_3class_accuracy": best_3class[1]["accuracy"],
        "3class_lift_over_baseline": round(best_3class[1]["accuracy"] - majority_3class, 4),
        "top_3_features_binary": list(fi_binary.keys())[:3],
        "top_3_features_3class": list(fi_3class.keys())[:3],
        "conclusion": "",  # filled after
    }

    # Conclusion
    lift_b = output["summary"]["binary_lift_over_baseline"]
    lift_3 = output["summary"]["3class_lift_over_baseline"]
    if lift_b > 0.15:
        verdict = "Strong: a_p statistics are highly predictive of rank"
    elif lift_b > 0.05:
        verdict = "Moderate: a_p statistics carry meaningful rank signal beyond baseline"
    elif lift_b > 0.01:
        verdict = "Weak: marginal signal in a_p statistics for rank prediction"
    else:
        verdict = "Negligible: a_p statistics from 25 primes cannot predict rank"
    output["summary"]["conclusion"] = verdict

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Binary best: {best_binary[0]} acc={best_binary[1]['accuracy']:.4f} "
          f"(baseline={majority_binary:.4f}, lift={lift_b:+.4f})")
    print(f"3-class best: {best_3class[0]} acc={best_3class[1]['accuracy']:.4f} "
          f"(baseline={majority_3class:.4f}, lift={lift_3:+.4f})")
    print(f"Top features (binary): {output['summary']['top_3_features_binary']}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
