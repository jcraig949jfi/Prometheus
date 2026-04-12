"""
ALL-040: Deformation Paths in a_p Space
==========================================
For forms at the same level (parametric families), trace how the
a_p vector changes across the family. Questions:
1. Are deformation paths smooth or discontinuous?
2. Do paths cluster by ST group?
3. What is the typical "distance" between forms at the same level?
4. Is there a preferred direction of deformation?
"""
import json, time, math
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from collections import defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "all040_deformation_paths_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def main():
    t0 = time.time()
    print("=== ALL-040: Deformation Paths in a_p Space ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms loaded")

    ap_primes = sieve(50)
    N_AP = 15  # Use first 15 a_p values

    # Group by level
    by_level = defaultdict(list)
    for label, level, ap_json, is_cm in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap[:N_AP]]
        if len(ap_vals) >= N_AP:
            by_level[level].append({
                "label": label, "ap": np.array(ap_vals, dtype=float),
                "is_cm": bool(is_cm)
            })

    # Levels with ≥2 forms
    multi_levels = {k: v for k, v in by_level.items() if len(v) >= 2}
    print(f"  Levels with ≥2 forms: {len(multi_levels)}")

    # Compute pairwise distances within each level
    all_dists = []
    cm_dists = []; non_cm_dists = []; mixed_dists = []
    level_stats = []

    for level in sorted(multi_levels.keys())[:2000]:
        group = multi_levels[level]
        n = len(group)
        dists = []
        for i in range(n):
            for j in range(i+1, n):
                d = float(np.linalg.norm(group[i]["ap"] - group[j]["ap"]))
                dists.append(d)
                all_dists.append(d)
                if group[i]["is_cm"] and group[j]["is_cm"]:
                    cm_dists.append(d)
                elif not group[i]["is_cm"] and not group[j]["is_cm"]:
                    non_cm_dists.append(d)
                else:
                    mixed_dists.append(d)

        if dists:
            level_stats.append({
                "level": level, "n_forms": n,
                "mean_dist": round(float(np.mean(dists)), 2),
                "std_dist": round(float(np.std(dists)), 2),
                "min_dist": round(float(min(dists)), 2),
                "max_dist": round(float(max(dists)), 2),
            })

    arr = np.array(all_dists)
    print(f"\n  Total pairwise distances: {len(all_dists)}")
    print(f"  Mean: {arr.mean():.2f}, Std: {arr.std():.2f}")
    print(f"  Range: [{arr.min():.2f}, {arr.max():.2f}]")

    # CM vs non-CM distance comparison
    if cm_dists and non_cm_dists:
        cm_arr = np.array(cm_dists)
        nc_arr = np.array(non_cm_dists)
        stat, pval = stats.mannwhitneyu(cm_arr, nc_arr, alternative='two-sided')
        print(f"\n  CM-CM distances: mean={cm_arr.mean():.2f} ({len(cm_dists)} pairs)")
        print(f"  non-CM-non-CM: mean={nc_arr.mean():.2f} ({len(non_cm_dists)} pairs)")
        print(f"  MWU p-value: {pval:.4e}")
    else:
        pval = 1.0

    # Path smoothness: for levels with ≥5 forms, compute PCA direction
    print("\n  PCA of deformation directions...")
    pca_results = []
    for level in sorted(multi_levels.keys()):
        group = multi_levels[level]
        if len(group) < 5: continue
        X = np.array([g["ap"] for g in group])
        X_centered = X - X.mean(axis=0)
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        explained_1 = float(S[0]**2 / np.sum(S**2))
        pca_results.append({"level": level, "n_forms": len(group),
                           "pc1_explained": round(explained_1, 4)})
    if pca_results:
        mean_pc1 = float(np.mean([p["pc1_explained"] for p in pca_results]))
        print(f"  {len(pca_results)} levels with ≥5 forms")
        print(f"  Mean PC1 explained variance: {mean_pc1:.1%}")
    else:
        mean_pc1 = 0

    # Level dimension vs family size
    if pca_results:
        sizes = [p["n_forms"] for p in pca_results]
        pc1s = [p["pc1_explained"] for p in pca_results]
        slope, _, r, p_corr, _ = stats.linregress(np.log(sizes), pc1s)
        print(f"  PC1 vs log(family_size): slope={slope:.4f}, R²={r**2:.4f}")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-040", "title": "Deformation Paths in a_p Space",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(rows),
        "n_multi_levels": len(multi_levels),
        "distance_stats": {
            "n_pairs": len(all_dists),
            "mean": round(float(arr.mean()), 2),
            "std": round(float(arr.std()), 2),
            "median": round(float(np.median(arr)), 2),
        },
        "cm_comparison": {
            "cm_mean": round(float(np.mean(cm_dists)), 2) if cm_dists else None,
            "non_cm_mean": round(float(np.mean(non_cm_dists)), 2) if non_cm_dists else None,
            "mixed_mean": round(float(np.mean(mixed_dists)), 2) if mixed_dists else None,
            "mwu_pvalue": float(pval),
        },
        "pca": {
            "n_families_ge5": len(pca_results),
            "mean_pc1_explained": round(mean_pc1, 4),
            "top_families": sorted(pca_results, key=lambda x: -x["pc1_explained"])[:10],
        },
        "level_stats_top20": sorted(level_stats, key=lambda x: -x["n_forms"])[:20],
        "assessment": None,
    }

    if mean_pc1 > 0.7:
        output["assessment"] = f"LINEAR DEFORMATION: PC1 explains {mean_pc1:.0%} — families deform along a single direction in a_p space"
    elif mean_pc1 > 0.4:
        output["assessment"] = f"PARTIALLY LINEAR: PC1={mean_pc1:.0%}. Deformation has a dominant direction but is not purely 1D"
    else:
        output["assessment"] = f"MULTI-DIRECTIONAL: PC1 only {mean_pc1:.0%}. Deformations are spread across multiple independent directions"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
