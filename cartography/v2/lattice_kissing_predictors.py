"""
Lattice Kissing Number Predictors: det, class_number, and combinations
Compare simpler invariants to theta-series k-NN (96.6%) and mod-p entropy (85.9%)
"""
import json
import numpy as np
from collections import defaultdict
from pathlib import Path

DATA = Path("F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json")
OUT = Path("F:/Prometheus/cartography/v2/lattice_kissing_predictors_results.json")


def load_lattices():
    """Load lattice data, extract relevant fields."""
    with open(DATA, "r") as f:
        raw = json.load(f)

    records = raw["records"]
    lattices = []
    for r in records:
        dim = r.get("dim")
        det = r.get("det")
        class_number = r.get("class_number")
        kissing = r.get("kissing")
        theta = r.get("theta_series")
        if dim is not None and det is not None and kissing is not None:
            lattices.append({
                "dim": int(dim),
                "det": float(det),
                "class_number": int(class_number) if class_number is not None else None,
                "kissing": int(kissing),
                "has_theta": theta is not None and len(theta) > 0,
                "theta_len": len(theta) if theta else 0,
            })
    return lattices


def ols_r2(X, y):
    """OLS regression, return R², coefficients, and predictions."""
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    # Add intercept
    ones = np.ones((X.shape[0], 1))
    X_aug = np.hstack([ones, X])
    # Solve normal equations
    try:
        beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    except np.linalg.LinAlgError:
        return {"r2": 0.0, "beta": [], "n": len(y)}
    y_hat = X_aug @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"r2": float(r2), "beta": beta.tolist(), "n": len(y)}


def analyze_dimension(lattices, dim):
    """Run all predictor models within a single dimension."""
    subset = [l for l in lattices if l["dim"] == dim]
    n = len(subset)
    if n < 20:
        return None

    kissing = np.array([l["kissing"] for l in subset])
    det = np.array([l["det"] for l in subset])

    # Check class_number availability
    has_cn = [l for l in subset if l["class_number"] is not None]
    n_cn = len(has_cn)

    results = {
        "dim": dim,
        "n_lattices": n,
        "kissing_stats": {
            "mean": float(np.mean(kissing)),
            "std": float(np.std(kissing)),
            "min": int(np.min(kissing)),
            "max": int(np.max(kissing)),
            "n_unique": int(len(np.unique(kissing))),
        },
    }

    # Log-transform det (determinants span orders of magnitude)
    log_det = np.log1p(det)

    # Model 1: det -> kissing
    r1 = ols_r2(det, kissing)
    results["det_linear"] = {"r2": r1["r2"], "n": r1["n"]}

    # Model 1b: log(det) -> kissing
    r1b = ols_r2(log_det, kissing)
    results["log_det_linear"] = {"r2": r1b["r2"], "n": r1b["n"]}

    # Model 1c: det + det^2 (quadratic)
    X_quad = np.column_stack([det, det**2])
    r1c = ols_r2(X_quad, kissing)
    results["det_quadratic"] = {"r2": r1c["r2"], "n": r1c["n"]}

    # Model 1d: log(det) + log(det)^2
    X_logquad = np.column_stack([log_det, log_det**2])
    r1d = ols_r2(X_logquad, kissing)
    results["log_det_quadratic"] = {"r2": r1d["r2"], "n": r1d["n"]}

    if n_cn >= 20:
        cn_kissing = np.array([l["kissing"] for l in has_cn])
        cn_det = np.array([l["det"] for l in has_cn])
        cn_log_det = np.log1p(cn_det)
        cn = np.array([l["class_number"] for l in has_cn])
        log_cn = np.log1p(cn)

        # Model 2: class_number -> kissing
        r2 = ols_r2(cn, cn_kissing)
        results["class_number_linear"] = {"r2": r2["r2"], "n": r2["n"]}

        # Model 2b: log(class_number)
        r2b = ols_r2(log_cn, cn_kissing)
        results["log_class_number_linear"] = {"r2": r2b["r2"], "n": r2b["n"]}

        # Model 3: det + class_number
        X_both = np.column_stack([cn_det, cn])
        r3 = ols_r2(X_both, cn_kissing)
        results["det_plus_class"] = {"r2": r3["r2"], "n": r3["n"]}

        # Model 3b: log(det) + log(class_number)
        X_both_log = np.column_stack([cn_log_det, log_cn])
        r3b = ols_r2(X_both_log, cn_kissing)
        results["log_det_plus_log_class"] = {"r2": r3b["r2"], "n": r3b["n"]}

        # Model 3c: log(det) + log(det)^2 + log(cn) + log(cn)^2
        X_full_quad = np.column_stack([cn_log_det, cn_log_det**2, log_cn, log_cn**2])
        r3c = ols_r2(X_full_quad, cn_kissing)
        results["full_quadratic"] = {"r2": r3c["r2"], "n": r3c["n"]}

        # Model 3d: det + det^2 + cn + cn^2 + det*cn (interaction)
        X_interact = np.column_stack([cn_det, cn_det**2, cn, cn**2, cn_det * cn])
        r3d = ols_r2(X_interact, cn_kissing)
        results["full_interaction"] = {"r2": r3d["r2"], "n": r3d["n"]}

        results["n_with_class_number"] = n_cn
    else:
        results["n_with_class_number"] = n_cn
        results["class_number_note"] = "too few records with class_number"

    # Correlation matrix
    corr_det_kiss = float(np.corrcoef(det, kissing)[0, 1]) if np.std(det) > 0 and np.std(kissing) > 0 else 0.0
    results["pearson_det_kissing"] = corr_det_kiss
    results["pearson_logdet_kissing"] = float(np.corrcoef(log_det, kissing)[0, 1]) if np.std(log_det) > 0 and np.std(kissing) > 0 else 0.0

    # Spearman rank correlation (more robust)
    from scipy.stats import spearmanr
    sp_det, _ = spearmanr(det, kissing)
    results["spearman_det_kissing"] = float(sp_det)

    if n_cn >= 20:
        sp_cn, _ = spearmanr(cn, cn_kissing)
        results["spearman_class_kissing"] = float(sp_cn)

    return results


def main():
    print("Loading lattices...")
    lattices = load_lattices()
    print(f"Loaded {len(lattices)} lattices with dim/det/kissing")

    # Dimension distribution
    dim_counts = defaultdict(int)
    for l in lattices:
        dim_counts[l["dim"]] += 1
    print("\nDimension distribution:")
    for d in sorted(dim_counts):
        print(f"  dim={d}: {dim_counts[d]} lattices")

    # Analyze each dimension with enough data
    results = {
        "description": "Kissing number prediction from simpler invariants (det, class_number)",
        "baselines": {
            "theta_series_knn": 0.966,
            "mod_p_entropy": 0.859,
        },
        "dimension_counts": {str(k): v for k, v in sorted(dim_counts.items())},
        "by_dimension": {},
    }

    for dim in sorted(dim_counts):
        if dim_counts[dim] >= 20:
            print(f"\n--- Dimension {dim} (n={dim_counts[dim]}) ---")
            res = analyze_dimension(lattices, dim)
            if res:
                results["by_dimension"][str(dim)] = res
                # Print summary
                print(f"  det linear R²:     {res['det_linear']['r2']:.4f}")
                print(f"  log(det) linear R²: {res['log_det_linear']['r2']:.4f}")
                print(f"  det quadratic R²:  {res['det_quadratic']['r2']:.4f}")
                if "class_number_linear" in res:
                    print(f"  class_num linear R²: {res['class_number_linear']['r2']:.4f}")
                    print(f"  det+class R²:      {res['det_plus_class']['r2']:.4f}")
                    print(f"  full quadratic R²: {res['full_quadratic']['r2']:.4f}")
                    print(f"  full interaction R²: {res['full_interaction']['r2']:.4f}")

    # Build diminishing returns summary for dim=3 (largest)
    if "3" in results["by_dimension"]:
        d3 = results["by_dimension"]["3"]
        chain = []
        chain.append({"predictor": "det (linear)", "r2": d3["det_linear"]["r2"]})
        chain.append({"predictor": "log(det) (linear)", "r2": d3["log_det_linear"]["r2"]})
        chain.append({"predictor": "det (quadratic)", "r2": d3["det_quadratic"]["r2"]})
        if "class_number_linear" in d3:
            chain.append({"predictor": "class_number (linear)", "r2": d3["class_number_linear"]["r2"]})
            chain.append({"predictor": "det + class_number", "r2": d3["det_plus_class"]["r2"]})
            chain.append({"predictor": "log(det) + log(class) quadratic", "r2": d3["full_quadratic"]["r2"]})
            chain.append({"predictor": "full interaction (det+cn+cross)", "r2": d3["full_interaction"]["r2"]})
        chain.append({"predictor": "mod-p entropy (baseline)", "r2": 0.859})
        chain.append({"predictor": "theta-series k-NN (baseline)", "r2": 0.966})
        chain.sort(key=lambda x: x["r2"])
        results["diminishing_returns_chain"] = chain

        print("\n=== Diminishing Returns Chain (dim=3) ===")
        for c in chain:
            print(f"  {c['predictor']:45s} R² = {c['r2']:.4f}")

    # Summary
    print("\n=== Key Finding ===")
    if "3" in results["by_dimension"]:
        d3 = results["by_dimension"]["3"]
        best_simple = max(
            d3.get("det_linear", {}).get("r2", 0),
            d3.get("log_det_linear", {}).get("r2", 0),
            d3.get("det_quadratic", {}).get("r2", 0),
        )
        best_combined = d3.get("full_interaction", {}).get("r2", best_simple)
        print(f"  Best det-only R²:         {best_simple:.4f}")
        print(f"  Best det+class R²:        {best_combined:.4f}")
        print(f"  Mod-p entropy baseline:   0.8590")
        print(f"  Theta k-NN baseline:      0.9660")
        gap_to_entropy = 0.859 - best_combined
        gap_to_theta = 0.966 - best_combined
        print(f"  Gap to entropy:           {gap_to_entropy:.4f}")
        print(f"  Gap to theta:             {gap_to_theta:.4f}")
        results["summary"] = {
            "best_det_only_r2": best_simple,
            "best_det_plus_class_r2": best_combined,
            "mod_p_entropy_r2": 0.859,
            "theta_knn_r2": 0.966,
            "gap_simple_to_entropy": gap_to_entropy,
            "gap_simple_to_theta": gap_to_theta,
        }

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
