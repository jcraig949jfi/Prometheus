"""
constant_manifold_analysis.py — Spectral geometry of mathematical constant-space.

Builds the 74x74 normalization manifold (ratio matrix) of mathematical constants,
computes its spectral decomposition, checks eigenvalues against known constants
(self-referential structure), performs PCA on log-ratio space, and clusters
constants by their normalization profiles.

Key question: Is constant-space low-dimensional? If 74 constants collapse onto
a rank-5 manifold, there are only ~5 independent degrees of freedom generating
all of mathematics' fundamental constants.

Part of the Prometheus / Cartography convergence analysis pipeline.
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy import linalg
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform

# ---------------------------------------------------------------------------
# Imports from sibling modules
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from constant_base_explorer import _define_constants  # noqa: E402
from constant_matcher import check_against_constants   # noqa: E402

# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "constant_manifold_results.json"


def load_constants():
    """Load constants from constant_base_explorer, filter to finite positive values."""
    raw = _define_constants()
    # Convert mpf to float, keep only finite positive values (ratios need > 0)
    constants = {}
    for name, val in raw.items():
        try:
            fval = float(val)
        except (ValueError, TypeError):
            continue
        if np.isfinite(fval) and fval > 0:
            constants[name] = fval
    # Sort by value for consistent ordering
    constants = dict(sorted(constants.items(), key=lambda kv: kv[1]))
    return constants


def build_normalization_manifold(values):
    """Build NxN matrix where M[i,j] = c_j / c_i."""
    n = len(values)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            M[i, j] = values[j] / values[i]
    return M


def build_fractional_part_manifold(values):
    """
    Build a richer manifold that captures non-trivial structure.

    The raw ratio matrix is rank-1 by construction (outer product structure).
    Instead, build a manifold from the *fractional parts* of log-ratios:
        F[i,j] = frac(log(c_j / c_i))
    This captures how "close" each ratio is to an integer power relationship.
    A matrix of fractional parts is NOT rank-1 and encodes genuine structure
    about which constants are near-integer-power multiples of each other.

    Also build a matrix from fractional parts of ratios themselves:
        G[i,j] = frac(c_j / c_i)
    """
    n = len(values)
    log_vals = np.log(values)

    # Fractional parts of log-ratios
    log_ratio_matrix = np.subtract.outer(log_vals, log_vals)  # log(c_i/c_j)
    F = log_ratio_matrix - np.floor(log_ratio_matrix)

    # Fractional parts of raw ratios
    ratio_matrix = np.divide.outer(values, values)
    G = ratio_matrix - np.floor(ratio_matrix)

    return F, G


def spectral_analysis(M, names):
    """Compute eigenvalues, singular values, condition number, determinant, rank."""
    n = M.shape[0]

    # Eigenvalues
    eigenvalues = linalg.eigvals(M)
    # Sort by magnitude (descending)
    idx = np.argsort(np.abs(eigenvalues))[::-1]
    eigenvalues = eigenvalues[idx]

    # Singular values
    singular_values = linalg.svdvals(M)

    # Condition number
    condition_number = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float('inf')

    # Determinant (may overflow; use log det)
    sign, logdet = np.linalg.slogdet(M)
    determinant_sign = float(sign)
    determinant_logabs = float(logdet)

    # Rank (numerical)
    rank = int(np.linalg.matrix_rank(M))

    return {
        "eigenvalues": eigenvalues,
        "singular_values": singular_values,
        "condition_number": condition_number,
        "determinant_sign": determinant_sign,
        "determinant_log_abs": determinant_logabs,
        "rank": rank,
        "n": n,
    }


def match_eigenvalues(eigenvalues, singular_values, tolerance=1e-4):
    """Check if eigenvalues or their ratios match known mathematical constants."""
    results = {"eigenvalue_matches": [], "eigenvalue_ratio_matches": [],
               "singular_value_matches": []}

    # Check real parts of top eigenvalues
    print("\n--- Eigenvalue constant matching ---")
    for i, ev in enumerate(eigenvalues[:20]):
        val = float(np.real(ev))
        if abs(val) < 1e-12:
            continue
        matches = check_against_constants(abs(val), tolerance=tolerance)
        if matches:
            best = matches[0]
            entry = {
                "eigenvalue_index": i,
                "eigenvalue": val,
                "match_name": best.name,
                "match_expression": best.expression,
                "match_value": best.matched_value,
                "residual": best.residual,
                "confidence": best.confidence,
            }
            results["eigenvalue_matches"].append(entry)
            print(f"  EV[{i}] = {val:.10f} ~ {best.expression} (residual={best.residual:.2e})")

    # Check ratios of consecutive eigenvalues (by magnitude)
    print("\n--- Consecutive eigenvalue ratio matching ---")
    magnitudes = np.abs(eigenvalues[:20])
    for i in range(len(magnitudes) - 1):
        if magnitudes[i + 1] < 1e-12:
            continue
        ratio = float(magnitudes[i] / magnitudes[i + 1])
        matches = check_against_constants(ratio, tolerance=tolerance)
        if matches:
            best = matches[0]
            entry = {
                "ratio_indices": [i, i + 1],
                "ratio_value": ratio,
                "match_name": best.name,
                "match_expression": best.expression,
                "match_value": best.matched_value,
                "residual": best.residual,
                "confidence": best.confidence,
            }
            results["eigenvalue_ratio_matches"].append(entry)
            print(f"  |EV[{i}]|/|EV[{i+1}]| = {ratio:.10f} ~ {best.expression} (residual={best.residual:.2e})")

    # Check top singular values
    print("\n--- Singular value constant matching ---")
    for i, sv in enumerate(singular_values[:15]):
        val = float(sv)
        if val < 1e-12:
            continue
        matches = check_against_constants(val, tolerance=tolerance)
        if matches:
            best = matches[0]
            entry = {
                "sv_index": i,
                "sv_value": val,
                "match_name": best.name,
                "match_expression": best.expression,
                "match_value": best.matched_value,
                "residual": best.residual,
                "confidence": best.confidence,
            }
            results["singular_value_matches"].append(entry)
            print(f"  SV[{i}] = {val:.10f} ~ {best.expression} (residual={best.residual:.2e})")

    return results


def _svd_analysis(matrix, names, label="matrix"):
    """Run SVD on a matrix and return dimensionality analysis."""
    # Center the matrix
    centered = matrix - matrix.mean(axis=0, keepdims=True)

    U, S, Vt = linalg.svd(centered, full_matrices=False)

    variance = S ** 2
    total_variance = variance.sum()
    if total_variance < 1e-30:
        return {
            "label": label,
            "n_components_90pct": 0,
            "n_components_95pct": 0,
            "n_components_99pct": 0,
            "effective_dimensionality": 0.0,
            "singular_values_top20": [float(s) for s in S[:20]],
            "variance_explained_top20": [],
            "cumulative_variance_top20": [],
            "top_loadings": [],
        }

    cumulative = np.cumsum(variance) / total_variance

    n_90 = int(np.searchsorted(cumulative, 0.90) + 1)
    n_95 = int(np.searchsorted(cumulative, 0.95) + 1)
    n_99 = int(np.searchsorted(cumulative, 0.99) + 1)

    # Effective dimensionality (participation ratio)
    d_eff = float((variance.sum()) ** 2 / (variance ** 2).sum())

    top_loadings = []
    for comp in range(min(5, len(S))):
        loading = Vt[comp]
        top_idx = np.argsort(np.abs(loading))[::-1][:5]
        contributors = [(names[idx], float(loading[idx])) for idx in top_idx]
        top_loadings.append({
            "component": comp,
            "singular_value": float(S[comp]),
            "variance_explained_pct": float(variance[comp] / total_variance * 100),
            "cumulative_pct": float(cumulative[comp] * 100),
            "top_contributors": contributors,
        })

    return {
        "label": label,
        "n_components_90pct": n_90,
        "n_components_95pct": n_95,
        "n_components_99pct": n_99,
        "effective_dimensionality": d_eff,
        "singular_values_top20": [float(s) for s in S[:20]],
        "variance_explained_top20": [float(v / total_variance * 100) for v in variance[:20]],
        "cumulative_variance_top20": [float(c * 100) for c in cumulative[:20]],
        "top_loadings": top_loadings,
    }


def pca_analysis(M, names, frac_log=None, frac_ratio=None):
    """
    PCA on multiple representations of the ratio manifold.

    The raw log-ratio matrix is rank-1 by construction (log(c_j/c_i) = log(c_j) - log(c_i)),
    so we also analyze:
      1. Fractional-part-of-log-ratio matrix: captures near-integer-power relationships
      2. Fractional-part-of-ratio matrix: captures non-trivial ratio structure
    These are NOT rank-1 and encode genuine geometric structure.
    """
    results = {}

    # --- Raw log-ratio (will be rank-1, included for completeness) ---
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        log_M = np.log(M)
    results["log_ratio"] = _svd_analysis(log_M, names, label="log_ratio (rank-1 baseline)")

    # --- Fractional part of log-ratios ---
    if frac_log is not None:
        results["frac_log_ratio"] = _svd_analysis(frac_log, names,
                                                    label="frac(log(c_j/c_i)) manifold")

    # --- Fractional part of raw ratios ---
    if frac_ratio is not None:
        results["frac_ratio"] = _svd_analysis(frac_ratio, names,
                                               label="frac(c_j/c_i) manifold")

    return results


def cluster_analysis_on_matrix(matrix, names, n_clusters=10):
    """Hierarchical clustering on a pre-computed matrix (rows = constant profiles)."""
    dist_matrix = pdist(matrix, metric="euclidean")

    linkage = hierarchy.ward(dist_matrix)
    labels = hierarchy.fcluster(linkage, t=n_clusters, criterion="maxclust")

    clusters = {}
    for i, label in enumerate(labels):
        label_str = str(int(label))
        if label_str not in clusters:
            clusters[label_str] = []
        clusters[label_str].append(names[i])

    sorted_clusters = sorted(clusters.items(), key=lambda kv: len(kv[1]), reverse=True)
    coph_corr, _ = hierarchy.cophenet(linkage, dist_matrix)

    return {
        "n_clusters": n_clusters,
        "cophenetic_correlation": float(coph_corr),
        "clusters": [{"cluster_id": cid, "size": len(members), "members": members}
                      for cid, members in sorted_clusters],
        "linkage_distances_top10": [float(d) for d in linkage[-10:, 2]],
    }


def cluster_analysis(M, names, n_clusters=10):
    """Hierarchical clustering on log-ratio profiles."""
    log_M = np.log(M)

    # Distance matrix: euclidean distance between log-ratio profiles (rows)
    dist_matrix = pdist(log_M, metric="euclidean")

    # Hierarchical clustering (Ward's method)
    linkage = hierarchy.ward(dist_matrix)

    # Cut to get n_clusters
    labels = hierarchy.fcluster(linkage, t=n_clusters, criterion="maxclust")

    # Build cluster membership
    clusters = {}
    for i, label in enumerate(labels):
        label_str = str(int(label))
        if label_str not in clusters:
            clusters[label_str] = []
        clusters[label_str].append(names[i])

    # Sort clusters by size (descending)
    sorted_clusters = sorted(clusters.items(), key=lambda kv: len(kv[1]), reverse=True)

    # Also compute cophenetic correlation (quality of clustering)
    coph_corr, _ = hierarchy.cophenet(linkage, dist_matrix)

    return {
        "n_clusters": n_clusters,
        "cophenetic_correlation": float(coph_corr),
        "clusters": [{"cluster_id": cid, "size": len(members), "members": members}
                      for cid, members in sorted_clusters],
        "linkage_distances_top10": [float(d) for d in linkage[-10:, 2]],
    }


def save_results(results, output_file):
    """Save results to JSON, converting numpy types."""
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, complex):
            return {"real": float(obj.real), "imag": float(obj.imag)}
        if isinstance(obj, np.complexfloating):
            return {"real": float(obj.real), "imag": float(obj.imag)}
        raise TypeError(f"Not serializable: {type(obj)}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=convert)
    print(f"\nResults saved to {output_file}")


def main():
    print("=" * 70)
    print("CONSTANT MANIFOLD ANALYSIS")
    print("Spectral geometry of mathematical constant-space")
    print("=" * 70)

    # 1. Load constants
    constants = load_constants()
    names = list(constants.keys())
    values = np.array(list(constants.values()))
    n = len(names)
    print(f"\nLoaded {n} positive finite constants.")
    print(f"Range: [{values.min():.6e}, {values.max():.6e}]")

    # 2. Build normalization manifold
    print("\n--- Building normalization manifold ---")
    M = build_normalization_manifold(values)
    print(f"Manifold shape: {M.shape}")
    print(f"Entry [0,0] = {M[0,0]:.6f} (should be 1.0)")
    print(f"Diagonal check: all 1s? {np.allclose(np.diag(M), 1.0)}")

    # Build fractional-part manifolds (non-trivial structure)
    frac_log, frac_ratio = build_fractional_part_manifold(values)
    print(f"Fractional-part manifolds built: frac(log-ratio) and frac(ratio)")

    # 3. Spectral properties of the raw ratio matrix
    print("\n--- Spectral analysis of ratio matrix ---")
    print("NOTE: M[i,j] = c_j/c_i is rank-1 by construction (outer product of 1/c and c).")
    spectral = spectral_analysis(M, names)
    print(f"Matrix size: {spectral['n']}x{spectral['n']}")
    print(f"Rank: {spectral['rank']} (expected: 1)")
    print(f"Condition number: {spectral['condition_number']:.6e}")
    print(f"Determinant: sign={spectral['determinant_sign']}, log|det|={spectral['determinant_log_abs']:.4f}")

    ev_mags = np.abs(spectral["eigenvalues"])
    print(f"Top 5 |eigenvalues|: {[f'{x:.6f}' for x in ev_mags[:5]]}")

    # Spectral analysis of fractional-part manifolds (these have genuine structure)
    print("\n--- Spectral analysis of frac(log-ratio) manifold ---")
    spectral_frac_log = spectral_analysis(frac_log, names)
    print(f"Rank: {spectral_frac_log['rank']} / {n}")
    ev_frac = np.abs(spectral_frac_log["eigenvalues"])
    print(f"Top 10 |eigenvalues|: {[f'{x:.6f}' for x in ev_frac[:10]]}")
    threshold_frac = ev_frac[0] * 1e-10
    n_sig_frac = int(np.sum(ev_frac > threshold_frac))
    print(f"Significant eigenvalues: {n_sig_frac} / {n}")

    print("\n--- Spectral analysis of frac(ratio) manifold ---")
    spectral_frac_ratio = spectral_analysis(frac_ratio, names)
    print(f"Rank: {spectral_frac_ratio['rank']} / {n}")
    ev_fr = np.abs(spectral_frac_ratio["eigenvalues"])
    print(f"Top 10 |eigenvalues|: {[f'{x:.6f}' for x in ev_fr[:10]]}")

    # 4. Self-referential check on the fractional-part manifold eigenvalues
    print("\n--- Self-referential structure check ---")
    print("Checking frac(log-ratio) manifold eigenvalues against known constants...")
    matching_frac_log = match_eigenvalues(
        spectral_frac_log["eigenvalues"], spectral_frac_log["singular_values"])
    print("\nChecking frac(ratio) manifold eigenvalues against known constants...")
    matching_frac_ratio = match_eigenvalues(
        spectral_frac_ratio["eigenvalues"], spectral_frac_ratio["singular_values"])

    # Also check the raw ratio matrix (trace = n, sole eigenvalue = n)
    print("\nChecking raw ratio manifold eigenvalues...")
    matching_raw = match_eigenvalues(spectral["eigenvalues"], spectral["singular_values"])

    total_self_ref = (
        len(matching_frac_log["eigenvalue_matches"])
        + len(matching_frac_log["eigenvalue_ratio_matches"])
        + len(matching_frac_log["singular_value_matches"])
        + len(matching_frac_ratio["eigenvalue_matches"])
        + len(matching_frac_ratio["eigenvalue_ratio_matches"])
        + len(matching_frac_ratio["singular_value_matches"])
        + len(matching_raw["eigenvalue_matches"])
        + len(matching_raw["eigenvalue_ratio_matches"])
        + len(matching_raw["singular_value_matches"])
    )
    print(f"\nTotal self-referential hits across all manifolds: {total_self_ref}")
    if total_self_ref > 0:
        print(">>> SELF-REFERENTIAL STRUCTURE DETECTED: constant-space geometry encodes constants!")

    # 5. PCA of manifolds
    print("\n--- PCA / SVD dimensionality analysis ---")
    pca = pca_analysis(M, names, frac_log=frac_log, frac_ratio=frac_ratio)

    for key, analysis in pca.items():
        print(f"\n  [{analysis['label']}]")
        print(f"    Components for 90% variance: {analysis['n_components_90pct']}")
        print(f"    Components for 95% variance: {analysis['n_components_95pct']}")
        print(f"    Components for 99% variance: {analysis['n_components_99pct']}")
        print(f"    Effective dimensionality: {analysis['effective_dimensionality']:.2f}")

        if analysis["top_loadings"]:
            print(f"    Top 3 principal components:")
            for comp in analysis["top_loadings"][:3]:
                print(f"      PC{comp['component']}: {comp['variance_explained_pct']:.2f}% variance, "
                      f"cumulative {comp['cumulative_pct']:.2f}%")
                for cname, loading in comp["top_contributors"][:3]:
                    print(f"        {cname}: {loading:+.4f}")

    # The key result: dimensionality of the fractional-part manifold
    frac_log_pca = pca.get("frac_log_ratio", pca["log_ratio"])
    d_eff_key = frac_log_pca["effective_dimensionality"]
    n90_key = frac_log_pca["n_components_90pct"]

    if d_eff_key < 10:
        print(f"\n>>> CONSTANT-SPACE IS LOW-DIMENSIONAL: D_eff = {d_eff_key:.2f}")
        print("    Fractional-part manifold shows genuine low-rank structure.")
    elif d_eff_key < 20:
        print(f"\n>>> CONSTANT-SPACE IS MODERATELY STRUCTURED: D_eff = {d_eff_key:.2f}")
    else:
        print(f"\n>>> CONSTANT-SPACE APPEARS HIGH-DIMENSIONAL: D_eff = {d_eff_key:.2f}")
        print("    Constants may be fundamentally independent (no hidden generating set).")

    # 6. Hierarchical clustering on the fractional-part manifold
    print("\n--- Hierarchical clustering of constants ---")
    print("(Using frac(log-ratio) profiles for clustering)")
    clustering = cluster_analysis_on_matrix(frac_log, names, n_clusters=10)
    print(f"Cophenetic correlation: {clustering['cophenetic_correlation']:.4f}")
    print(f"\nTop {clustering['n_clusters']} clusters:")
    for cl in clustering["clusters"]:
        print(f"  Cluster {cl['cluster_id']} (size {cl['size']}): {', '.join(cl['members'])}")

    # Also cluster on log-ratios (groups by magnitude)
    print("\n--- Clustering by magnitude (log-ratio profiles) ---")
    clustering_mag = cluster_analysis(M, names, n_clusters=10)
    print(f"Cophenetic correlation: {clustering_mag['cophenetic_correlation']:.4f}")
    for cl in clustering_mag["clusters"]:
        print(f"  Cluster {cl['cluster_id']} (size {cl['size']}): {', '.join(cl['members'])}")

    # 7. Save everything
    results = {
        "metadata": {
            "n_constants": n,
            "constant_names": names,
            "constant_values": values.tolist(),
        },
        "spectral_raw_ratio": {
            "note": "Rank-1 by construction (outer product). Included for completeness.",
            "rank": spectral["rank"],
            "condition_number": spectral["condition_number"],
            "determinant_sign": spectral["determinant_sign"],
            "determinant_log_abs": spectral["determinant_log_abs"],
            "eigenvalues_top20": [{"real": float(np.real(e)), "imag": float(np.imag(e)),
                                    "magnitude": float(np.abs(e))}
                                   for e in spectral["eigenvalues"][:20]],
            "singular_values_top20": [float(s) for s in spectral["singular_values"][:20]],
        },
        "spectral_frac_log_ratio": {
            "note": "Fractional part of log(c_j/c_i). Genuine non-trivial structure.",
            "rank": spectral_frac_log["rank"],
            "condition_number": spectral_frac_log["condition_number"],
            "eigenvalues_top20": [{"real": float(np.real(e)), "imag": float(np.imag(e)),
                                    "magnitude": float(np.abs(e))}
                                   for e in spectral_frac_log["eigenvalues"][:20]],
            "singular_values_top20": [float(s) for s in spectral_frac_log["singular_values"][:20]],
            "n_significant_eigenvalues": n_sig_frac,
        },
        "spectral_frac_ratio": {
            "note": "Fractional part of c_j/c_i. Genuine non-trivial structure.",
            "rank": spectral_frac_ratio["rank"],
            "eigenvalues_top20": [{"real": float(np.real(e)), "imag": float(np.imag(e)),
                                    "magnitude": float(np.abs(e))}
                                   for e in spectral_frac_ratio["eigenvalues"][:20]],
        },
        "self_referential": {
            "frac_log_ratio_manifold": matching_frac_log,
            "frac_ratio_manifold": matching_frac_ratio,
            "raw_ratio_manifold": matching_raw,
            "total_hits": total_self_ref,
        },
        "pca": {k: v for k, v in pca.items()},
        "clustering_frac_log": clustering,
        "clustering_magnitude": clustering_mag,
        "summary": {
            "effective_dimensionality_frac_log": frac_log_pca["effective_dimensionality"],
            "effective_dimensionality_frac_ratio": pca.get("frac_ratio", {}).get("effective_dimensionality", None),
            "components_90pct_frac_log": frac_log_pca["n_components_90pct"],
            "components_95pct_frac_log": frac_log_pca["n_components_95pct"],
            "components_99pct_frac_log": frac_log_pca["n_components_99pct"],
            "is_low_dimensional": d_eff_key < 10,
            "self_referential_hits": total_self_ref,
            "raw_matrix_rank": spectral["rank"],
            "frac_log_matrix_rank": spectral_frac_log["rank"],
        },
    }

    save_results(results, OUTPUT_FILE)

    # 8. Final summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Constants analyzed: {n}")
    print(f"Raw ratio matrix rank: {spectral['rank']} / {n} (rank-1 by construction)")
    print(f"Frac(log-ratio) matrix rank: {spectral_frac_log['rank']} / {n}")
    print(f"Frac(ratio) matrix rank: {spectral_frac_ratio['rank']} / {n}")
    print(f"Effective dimensionality (frac-log): {frac_log_pca['effective_dimensionality']:.2f}")
    frac_ratio_pca = pca.get("frac_ratio")
    if frac_ratio_pca:
        print(f"Effective dimensionality (frac-ratio): {frac_ratio_pca['effective_dimensionality']:.2f}")
    print(f"Components for 90% variance (frac-log): {frac_log_pca['n_components_90pct']}")
    print(f"Components for 95% variance (frac-log): {frac_log_pca['n_components_95pct']}")
    print(f"Components for 99% variance (frac-log): {frac_log_pca['n_components_99pct']}")
    print(f"Self-referential hits: {total_self_ref}")
    print(f"Clustering quality (frac-log): {clustering['cophenetic_correlation']:.4f}")
    print(f"Results: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
