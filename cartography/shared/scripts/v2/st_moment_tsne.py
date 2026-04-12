"""
ALL-044: Sato-Tate Moment Space t-SNE
=======================================
Compute 6-moment vectors for GL(2) modular forms from DuckDB a_p coefficients,
then project to 2D via t-SNE. Measure cluster separation by ST group (CM vs
non-CM) and by endomorphism type.

Since per-curve feature vectors weren't stored, we recompute moments from
a_p coefficients in DuckDB for all weight-2, dim-1 newforms.
"""

import json, time, math
import numpy as np
import duckdb
from pathlib import Path
from collections import defaultdict, Counter

V2 = Path(__file__).resolve().parent
DB_PATH = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT_PATH = V2 / "st_moment_tsne_results.json"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def compute_moments(ap_vals, level, max_k=6):
    """Compute normalized moments M1..M6 of a_p / 2*sqrt(p)."""
    bad = set()
    d = 2
    n = level
    while d * d <= n:
        while n % d == 0: bad.add(d); n //= d
        d += 1
    if n > 1: bad.add(n)

    normalized = []
    for i, p in enumerate(PRIMES):
        if i >= len(ap_vals) or p in bad:
            continue
        bound = 2 * math.sqrt(p)
        if bound > 0:
            normalized.append(ap_vals[i] / bound)
    if len(normalized) < 10:
        return None
    arr = np.array(normalized)
    return [float(np.mean(arr**k)) for k in range(1, max_k + 1)]


def main():
    t0 = time.time()
    print("=== ALL-044: ST Moment Space t-SNE ===\n")

    print("[1] Loading modular forms from DuckDB...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm, self_twist_type
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"    {len(rows)} forms loaded")

    # Compute moment vectors
    print("[2] Computing 6-moment vectors...")
    labels, features, cm_flags, levels = [], [], [], []
    for label, level, ap_json, is_cm, st_type in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap]
        m = compute_moments(ap_vals, level)
        if m is not None:
            labels.append(label)
            features.append(m)
            cm_flags.append(1 if is_cm else 0)
            levels.append(level)

    X = np.array(features)
    print(f"    {X.shape[0]} forms with valid moments, {X.shape[1]} dimensions")

    # Standardize
    mu, sigma = X.mean(axis=0), X.std(axis=0)
    sigma[sigma < 1e-12] = 1.0
    X_std = (X - mu) / sigma

    # t-SNE via simple Barnes-Hut approximation (sklearn)
    print("[3] Running t-SNE (perplexity=30)...")
    try:
        from sklearn.manifold import TSNE
        tsne = TSNE(n_components=2, perplexity=30, random_state=42,
                     max_iter=1000, init='pca')
        Y = tsne.fit_transform(X_std)
        tsne_method = "sklearn"
    except ImportError:
        # Fallback: PCA
        print("    sklearn not available, falling back to PCA")
        cov = np.cov(X_std.T)
        eigvals, eigvecs = np.linalg.eigh(cov)
        idx = np.argsort(eigvals)[::-1]
        Y = X_std @ eigvecs[:, idx[:2]]
        tsne_method = "PCA_fallback"

    print(f"    Projection complete ({tsne_method})")

    # Cluster analysis: CM vs non-CM separation
    print("[4] Measuring CM vs non-CM separation...")
    cm_arr = np.array(cm_flags)
    cm_mask = cm_arr == 1
    non_cm_mask = cm_arr == 0

    if cm_mask.sum() > 0 and non_cm_mask.sum() > 0:
        cm_center = Y[cm_mask].mean(axis=0)
        non_cm_center = Y[non_cm_mask].mean(axis=0)
        center_dist = float(np.linalg.norm(cm_center - non_cm_center))
        cm_spread = float(np.mean(np.linalg.norm(Y[cm_mask] - cm_center, axis=1)))
        non_cm_spread = float(np.mean(np.linalg.norm(Y[non_cm_mask] - non_cm_center, axis=1)))
        fisher_ratio = center_dist**2 / (cm_spread**2 + non_cm_spread**2 + 1e-10)
    else:
        center_dist, cm_spread, non_cm_spread, fisher_ratio = 0, 0, 0, 0

    print(f"    CM center distance: {center_dist:.3f}")
    print(f"    CM spread: {cm_spread:.3f}, non-CM spread: {non_cm_spread:.3f}")
    print(f"    Fisher discriminant ratio: {fisher_ratio:.4f}")

    # Silhouette on CM/non-CM labels
    try:
        from sklearn.metrics import silhouette_score
        if cm_mask.sum() >= 2 and non_cm_mask.sum() >= 2:
            sil = float(silhouette_score(Y, cm_arr))
        else:
            sil = None
    except ImportError:
        sil = None
    print(f"    Silhouette (CM vs non-CM): {sil}")

    # Moment centroids by CM status
    cm_centroids = X[cm_mask].mean(axis=0).tolist() if cm_mask.sum() > 0 else []
    non_cm_centroids = X[non_cm_mask].mean(axis=0).tolist() if non_cm_mask.sum() > 0 else []

    n_cm = int(cm_mask.sum())
    elapsed = time.time() - t0

    output = {
        "challenge": "ALL-044",
        "title": "ST Moment Space t-SNE",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_forms": len(labels),
        "n_cm": n_cm,
        "n_non_cm": len(labels) - n_cm,
        "projection_method": tsne_method,
        "cm_separation": {
            "center_distance": round(center_dist, 4),
            "cm_spread": round(cm_spread, 4),
            "non_cm_spread": round(non_cm_spread, 4),
            "fisher_ratio": round(fisher_ratio, 4),
            "silhouette": round(sil, 4) if sil is not None else None,
        },
        "moment_centroids": {
            "cm": [round(v, 6) for v in cm_centroids],
            "non_cm": [round(v, 6) for v in non_cm_centroids],
        },
        "embedding_stats": {
            "y_range_x": [float(Y[:, 0].min()), float(Y[:, 0].max())],
            "y_range_y": [float(Y[:, 1].min()), float(Y[:, 1].max())],
        },
        "assessment": None,
    }

    if fisher_ratio > 1.0:
        output["assessment"] = f"STRONG SEPARATION: Fisher ratio {fisher_ratio:.2f} — CM forms occupy distinct region in moment space"
    elif fisher_ratio > 0.1:
        output["assessment"] = f"MODERATE SEPARATION: Fisher ratio {fisher_ratio:.2f} — CM partially separable, clusters overlap"
    else:
        output["assessment"] = f"WEAK SEPARATION: Fisher ratio {fisher_ratio:.4f} — moment space does NOT cleanly separate CM"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
