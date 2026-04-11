"""
Genus-2 Interference Tensor Rank (List1 #19)

Construct the interference tensor I(ell_1, ell_2) across primes for genus-2
curves and compute its matrix rank under SVD thresholding.

For each curve, the mod-ell fingerprint is the pair (a1_p mod ell, a2_p mod ell)
at a fixed set of probe primes. This approximates the mod-ell Galois
representation rho_{ell}: Gal(Q-bar/Q) -> GSp_4(F_ell).

For each pair (ell_1, ell_2), the interference is:
    I(ell_1, ell_2) = P(same joint fp) / (P(same fp_ell1) * P(same fp_ell2)) - 1

The SVD rank under threshold sigma > sigma_max/100 reveals the intrinsic
dimensionality of mod-ell correlations.
"""

import json
import ast
import numpy as np
from collections import Counter
from pathlib import Path
import time

DATA_FILE = Path("F:/Prometheus/cartography/genus2/data/g2c-data/gce_1000000_lmfdb.txt")
OUT_DIR = Path("F:/Prometheus/cartography/v2")

ELLS = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# Two large probe primes: traces at p=41,43 have |a1_p| up to ~25 (genus-2)
# and |a2_p| up to ~200, giving nontrivial mod-ell structure for all ell.
# Using (a1, a2) at 2 primes => 4 coordinates per fingerprint.
# Fingerprint space: ell^4 (16 for ell=2, 707281 for ell=29).
# For ell <= 7: ell^4 <= 2401, giving rich collision structure in 66K curves.
# For ell >= 11: ell^4 >= 14641, sparser but still meaningful.
PROBE_PRIMES = [41, 43]


def parse_curves(max_curves=None):
    """Parse genus-2 curve data, extracting good_lfactors."""
    curves = []
    with open(DATA_FILE, "r") as f:
        for i, line in enumerate(f):
            if max_curves and i >= max_curves:
                break
            line = line.strip()
            if not line:
                continue
            fields = line.split(":")
            if len(fields) < 17:
                continue
            try:
                conductor = int(fields[0])
                lfactors = ast.literal_eval(fields[-1])
                traces = {}
                for entry in lfactors:
                    if len(entry) >= 3:
                        traces[entry[0]] = (entry[1], entry[2])
                if traces:
                    curves.append({
                        "conductor": conductor,
                        "label": fields[0] + ":" + fields[1],
                        "traces": traces,
                    })
            except (ValueError, SyntaxError):
                continue
    return curves


def compute_mod_ell_fingerprint(curve, ell):
    """
    Compute the mod-ell fingerprint: (a1_p mod ell, a2_p mod ell) at each probe prime.

    For genus-2 curves, the local L-factor at a good prime p is:
        L_p(s) = 1 - a1_p*p^{-s} + a2_p*p^{-2s} - a1_p*p^{1-3s} + p^{2-4s}

    Both a1_p and a2_p are invariants of the mod-ell Galois representation,
    as they determine the characteristic polynomial of Frobenius mod ell.
    """
    fp = []
    for p in PROBE_PRIMES:
        if p in curve["traces"]:
            a1, a2 = curve["traces"][p]
            fp.append((a1 % ell, a2 % ell))
        else:
            return None  # require all probe primes
    return tuple(fp)


def compute_interference_matrix(curves):
    """
    Compute the 10x10 interference matrix.
    """
    N = len(curves)
    n_pairs = N * (N - 1) / 2.0

    print(f"Computing fingerprints for {N} curves...")

    # Precompute fingerprints
    fingerprints = {}
    for ell in ELLS:
        fps = []
        for c in curves:
            fp = compute_mod_ell_fingerprint(c, ell)
            fps.append(fp)
        fingerprints[ell] = fps

    # Single-ell collision probabilities
    print("Computing single-ell collision probabilities...")
    collision_prob = {}
    fp_stats = {}
    for ell in ELLS:
        valid_fps = [fp for fp in fingerprints[ell] if fp is not None]
        counts = Counter(valid_fps)
        n_valid = len(valid_fps)
        collisions = sum(n * (n - 1) / 2.0 for n in counts.values())
        n_valid_pairs = n_valid * (n_valid - 1) / 2.0
        cp = collisions / n_valid_pairs if n_valid_pairs > 0 else 0
        collision_prob[ell] = cp
        fp_stats[ell] = {
            "unique_fps": len(counts),
            "max_bucket": max(counts.values()) if counts else 0,
            "collision_prob": cp,
            "n_valid": n_valid,
            "theoretical_fp_space": ell ** (2 * len(PROBE_PRIMES)),
        }
        print(f"  ell={ell:2d}: coll_prob = {cp:.6f} "
              f"(n_valid={n_valid}, unique={len(counts)}/{ell**(2*len(PROBE_PRIMES))}, "
              f"max_bucket={max(counts.values()) if counts else 0})")

    # Joint collision probabilities
    print("Computing joint collision probabilities...")
    interference = np.zeros((len(ELLS), len(ELLS)))
    joint_prob_mat = np.zeros((len(ELLS), len(ELLS)))

    for i, ell1 in enumerate(ELLS):
        for j, ell2 in enumerate(ELLS):
            if i <= j:
                # Joint fingerprint: only count curves with both valid
                joint_fps = []
                for k in range(N):
                    fp1 = fingerprints[ell1][k]
                    fp2 = fingerprints[ell2][k]
                    if fp1 is not None and fp2 is not None:
                        joint_fps.append((fp1, fp2))

                n_joint = len(joint_fps)
                n_joint_pairs = n_joint * (n_joint - 1) / 2.0
                counts = Counter(joint_fps)
                collisions = sum(n * (n - 1) / 2.0 for n in counts.values())
                p_joint = collisions / n_joint_pairs if n_joint_pairs > 0 else 0

                p_indep = collision_prob[ell1] * collision_prob[ell2]

                joint_prob_mat[i, j] = p_joint
                joint_prob_mat[j, i] = p_joint

                I_val = (p_joint / p_indep - 1.0) if p_indep > 0 else 0.0
                interference[i, j] = I_val
                interference[j, i] = I_val

    return interference, collision_prob, joint_prob_mat, fp_stats


def normalize_interference(interference):
    """
    Compute normalized interference (correlation matrix):
        R(i,j) = I(i,j) / sqrt(I(i,i) * I(j,j))
    """
    diag = np.diag(interference).copy()
    diag[diag <= 0] = 1.0
    D_inv_sqrt = np.diag(1.0 / np.sqrt(diag))
    R = D_inv_sqrt @ interference @ D_inv_sqrt
    return R


def analyze_svd(matrix, label=""):
    """Compute SVD and determine effective rank."""
    U, sigma, Vt = np.linalg.svd(matrix)

    sigma_max = sigma[0]
    threshold = sigma_max / 100.0
    rank = int(np.sum(sigma > threshold))

    total_var = np.sum(sigma ** 2)
    cumulative_var = np.cumsum(sigma ** 2) / total_var if total_var > 0 else sigma * 0

    # Also compute rank at various variance thresholds
    rank_90 = int(np.searchsorted(cumulative_var, 0.90)) + 1
    rank_95 = int(np.searchsorted(cumulative_var, 0.95)) + 1
    rank_99 = int(np.searchsorted(cumulative_var, 0.99)) + 1

    return {
        "label": label,
        "singular_values": sigma.tolist(),
        "threshold": float(threshold),
        "sigma_max": float(sigma_max),
        "rank_svd_threshold": rank,
        "rank_90pct_variance": int(rank_90),
        "rank_95pct_variance": int(rank_95),
        "rank_99pct_variance": int(rank_99),
        "explained_variance_cumulative": cumulative_var.tolist(),
    }


def print_matrix(matrix, label, ells, fmt=".4f"):
    """Pretty-print a matrix."""
    print(f"\n--- {label} ---")
    print(f"{'':>4s}", end="")
    for ell in ells:
        print(f"{ell:>10d}", end="")
    print()
    for i, ell1 in enumerate(ells):
        print(f"{ell1:>4d}", end="")
        for j in range(len(ells)):
            print(f"{matrix[i, j]:>10{fmt}}", end="")
        print()


def print_svd(svd_result):
    """Print SVD results."""
    print(f"\n--- SVD: {svd_result['label']} ---")
    sv = svd_result['singular_values']
    print(f"Singular values: {[f'{s:.6f}' for s in sv]}")
    print(f"Sigma_max = {svd_result['sigma_max']:.6f}")
    print(f"Threshold (sigma_max/100) = {svd_result['threshold']:.6f}")
    print(f"Rank (SVD threshold):   {svd_result['rank_svd_threshold']}")
    print(f"Rank (90% variance):    {svd_result['rank_90pct_variance']}")
    print(f"Rank (95% variance):    {svd_result['rank_95pct_variance']}")
    print(f"Rank (99% variance):    {svd_result['rank_99pct_variance']}")
    print(f"Cumulative explained variance:")
    for k, cv in enumerate(svd_result["explained_variance_cumulative"]):
        marker = " <-- rank" if k + 1 == svd_result["rank_svd_threshold"] else ""
        print(f"  dim {k+1}: {cv:.6f}{marker}")


def main():
    t0 = time.time()
    print("=" * 60)
    print("Genus-2 Interference Tensor Rank Analysis")
    print("=" * 60)

    # Load data
    print("\nLoading genus-2 curves...")
    curves = parse_curves()
    print(f"Loaded {len(curves)} curves with trace data.")

    # Filter to curves with all probe primes
    valid_curves = [c for c in curves
                    if all(p in c["traces"] for p in PROBE_PRIMES)]
    print(f"Curves with traces at probes {PROBE_PRIMES}: {len(valid_curves)}")
    curves_used = valid_curves

    # Compute interference matrix
    interference, collision_prob, joint_prob, fp_stats = \
        compute_interference_matrix(curves_used)

    # Print raw interference
    print_matrix(interference, "Raw Interference I(ell_1, ell_2)", ELLS)

    # Normalized interference
    R = normalize_interference(interference)
    print_matrix(R, "Normalized Interference R(ell_1, ell_2)", ELLS)

    # SVD on raw
    svd_raw = analyze_svd(interference, "Raw Interference")
    print_svd(svd_raw)

    # SVD on normalized
    svd_norm = analyze_svd(R, "Normalized Interference")
    print_svd(svd_norm)

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Curves used:                   {len(curves_used)}")
    print(f"Probe primes:                  {PROBE_PRIMES}")
    print(f"Fingerprint:                   (a1_p mod ell, a2_p mod ell) at each probe")
    print(f"Raw interference rank (SVD):    {svd_raw['rank_svd_threshold']}")
    print(f"Raw interference rank (99%):   {svd_raw['rank_99pct_variance']}")
    print(f"Normalized rank (SVD):         {svd_norm['rank_svd_threshold']}")
    print(f"Normalized rank (99%):         {svd_norm['rank_99pct_variance']}")
    print(f"Elapsed: {elapsed:.1f}s")

    # Build results
    results = {
        "analysis": "Genus-2 Interference Tensor Rank",
        "challenge": "List1 #19",
        "data_source": str(DATA_FILE),
        "num_curves_total": len(curves),
        "num_curves_used": len(curves_used),
        "probe_primes": PROBE_PRIMES,
        "ells": ELLS,
        "fingerprint_method": "(a1_p mod ell, a2_p mod ell) at probe primes p",
        "fingerprint_stats": {str(ell): fp_stats[ell] for ell in ELLS},
        "collision_probabilities": {str(ell): float(collision_prob[ell]) for ell in ELLS},
        "interference_matrix_raw": interference.tolist(),
        "interference_matrix_normalized": R.tolist(),
        "svd_raw": svd_raw,
        "svd_normalized": svd_norm,
        "effective_rank_svd": svd_raw["rank_svd_threshold"],
        "effective_rank_99pct": svd_raw["rank_99pct_variance"],
        "effective_rank_normalized_svd": svd_norm["rank_svd_threshold"],
        "interpretation": (
            f"The 10x10 genus-2 interference matrix measures how mod-ell fingerprint "
            f"sharing between pairs of curves deviates from independence. Using "
            f"{len(curves_used)} genus-2 curves from LMFDB with Hecke traces at "
            f"probes {PROBE_PRIMES}, the raw interference matrix has SVD rank "
            f"{svd_raw['rank_svd_threshold']} (threshold sigma > sigma_max/100) "
            f"and 99%-variance rank {svd_raw['rank_99pct_variance']}. "
            f"The first {svd_raw['rank_99pct_variance']} singular dimensions capture "
            f"over 99% of the interference structure, indicating that mod-ell Galois "
            f"representation correlations in genus-2 arithmetic are governed by "
            f"~{svd_raw['rank_99pct_variance']} independent dimensions."
        ),
        "elapsed_seconds": round(elapsed, 2),
    }

    out_json = OUT_DIR / "genus2_interference_tensor_results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_json}")

    return results


if __name__ == "__main__":
    main()
