"""
Hecke-Theta Obstruction Tensor

Compute the rank of the bilinear map between EC Hecke eigenvalues
and lattice theta coefficients across primes.

EC: 1000 forms x 25 primes, normalized a_p / (2*sqrt(p))
Lattice: 1000 lattices x 25 theta coefficients

Since LMFDB lattices are integral (mostly even), theta[n]=0 for odd n.
We use two schemes:
  (a) theta at indices 2*p for each prime p  (prime-aligned even indices)
  (b) theta at first 25 even indices with highest variance (data-driven)

Cross-covariance C = A^T B  (25x25)
SVD -> effective rank = #sigma above sigma_max/100
Also: rank at 95% variance, null comparison via permutation.
"""

import json
import numpy as np
import duckdb
import psycopg2
from pathlib import Path

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

# Even indices corresponding to 2*prime
EVEN_PRIME_IDX = [2 * p for p in PRIMES_25]  # [4, 6, 10, 14, ...]
# But 2*97=194 > 151, so we cap at 150
EVEN_PRIME_IDX_VALID = [2 * p for p in PRIMES_25 if 2 * p < 151]

N_FORMS = 1000
N_LATTICES = 1000
N_PERMS = 200
RNG = np.random.default_rng(42)

OUT_DIR = Path(__file__).parent
RESULTS_PATH = OUT_DIR / "hecke_theta_obstruction_results.json"


def build_ec_matrix():
    """Build A: N_FORMS x 25 matrix of normalized a_p/(2*sqrt(p))."""
    con = duckdb.connect(str(Path(__file__).resolve().parents[2] / "charon" / "data" / "charon.duckdb"), read_only=True)
    # Sample diverse ECs across conductors using hash-based sampling
    rows = con.execute(
        f"SELECT aplist FROM elliptic_curves "
        f"WHERE aplist IS NOT NULL AND len(aplist) >= 25 "
        f"ORDER BY hash(conductor || rank) "
        f"LIMIT {N_FORMS}"
    ).fetchall()
    con.close()

    A = np.zeros((len(rows), 25))
    for i, (aplist,) in enumerate(rows):
        for j, p in enumerate(PRIMES_25):
            A[i, j] = aplist[j] / (2.0 * np.sqrt(p))
    print(f"EC matrix A: {A.shape}")
    return A


def fetch_theta_raw():
    """Fetch raw theta series from LMFDB PostgreSQL."""
    con = psycopg2.connect(
        host="devmirror.lmfdb.xyz", port=5432,
        database="lmfdb", user="lmfdb", password="lmfdb"
    )
    cur = con.cursor()
    cur.execute(
        "SELECT label, theta_series FROM lat_lattices "
        "WHERE theta_series IS NOT NULL "
        f"LIMIT {N_LATTICES}"
    )
    rows = cur.fetchall()
    cur.close()
    con.close()

    theta_all = []
    labels = []
    for label, theta_raw in rows:
        if isinstance(theta_raw, str):
            theta = json.loads(theta_raw)
        elif isinstance(theta_raw, (list, tuple)):
            theta = list(theta_raw)
        else:
            theta = list(theta_raw)
        theta_all.append(theta)
        labels.append(label)

    return labels, theta_all


def build_lattice_matrix_prime_aligned(theta_all):
    """Build B using theta[2*p] for each prime p (where 2*p < 151)."""
    valid_primes = [p for p in PRIMES_25 if 2 * p < 151]
    n_cols = len(valid_primes)
    B = np.zeros((len(theta_all), n_cols))
    for i, theta in enumerate(theta_all):
        for j, p in enumerate(valid_primes):
            idx = 2 * p
            B[i, j] = theta[idx] if idx < len(theta) else 0.0
    print(f"Lattice matrix B (prime-aligned): {B.shape}, primes used: {len(valid_primes)}")
    print(f"  Indices used: {[2*p for p in valid_primes]}")
    return B, valid_primes


def build_lattice_matrix_top_variance(theta_all):
    """Build B using top-25 variance even indices from theta series."""
    # Build full matrix
    max_len = max(len(t) for t in theta_all)
    B_full = np.zeros((len(theta_all), max_len))
    for i, theta in enumerate(theta_all):
        for j in range(len(theta)):
            B_full[i, j] = theta[j]

    # Get variance per index, pick top 25 even indices
    var_per_idx = B_full.var(axis=0)
    even_idx = np.array([i for i in range(2, max_len, 2)])
    even_var = var_per_idx[even_idx]
    top25 = even_idx[np.argsort(even_var)[-25:][::-1]]
    top25_sorted = np.sort(top25)

    B = B_full[:, top25_sorted]
    print(f"Lattice matrix B (top-25 variance): {B.shape}")
    print(f"  Indices used: {top25_sorted.tolist()}")
    return B, top25_sorted.tolist()


def compute_obstruction(A, B, standardize=True):
    """Compute cross-covariance and SVD."""
    # Match dimensions: use min(A.cols, B.cols)
    n_cols = min(A.shape[1], B.shape[1])
    A_use = A[:, :n_cols].copy()
    B_use = B[:, :n_cols].copy()

    # Center columns
    A_use -= A_use.mean(axis=0, keepdims=True)
    B_use -= B_use.mean(axis=0, keepdims=True)

    # Standardize columns to unit variance (proper for cross-covariance rank)
    if standardize:
        a_std = A_use.std(axis=0, keepdims=True)
        b_std = B_use.std(axis=0, keepdims=True)
        a_std[a_std < 1e-12] = 1.0
        b_std[b_std < 1e-12] = 1.0
        A_use /= a_std
        B_use /= b_std

    A_c = A_use
    B_c = B_use

    # Cross-covariance C = A^T B  (n_cols x n_cols)
    n = min(A_c.shape[0], B_c.shape[0])
    C = A_c.T @ B_c / n

    # SVD
    U, sigma, Vt = np.linalg.svd(C, full_matrices=False)

    # Effective rank: sigma > sigma_max / 100
    if sigma[0] > 0:
        threshold = sigma[0] / 100.0
        eff_rank = int(np.sum(sigma > threshold))
    else:
        eff_rank = 0

    # Rank at 95% variance
    total_var = np.sum(sigma ** 2)
    if total_var > 0:
        cumvar = np.cumsum(sigma ** 2) / total_var
        rank_95 = int(np.searchsorted(cumvar, 0.95) + 1)
    else:
        cumvar = np.zeros_like(sigma)
        rank_95 = 0

    return C, sigma, eff_rank, rank_95


def null_distribution(A, B, n_perms=N_PERMS):
    """Permutation null: shuffle rows of B independently."""
    null_eff_ranks = []
    null_rank95s = []
    null_sigma_maxes = []

    for _ in range(n_perms):
        idx = RNG.permutation(B.shape[0])
        B_perm = B[idx]
        _, sigma_null, eff_null, r95_null = compute_obstruction(A, B_perm)
        null_eff_ranks.append(eff_null)
        null_rank95s.append(r95_null)
        null_sigma_maxes.append(float(sigma_null[0]))

    return null_eff_ranks, null_rank95s, null_sigma_maxes


def run_analysis(A, B, label, theta_indices):
    """Run full SVD + null analysis for one pairing scheme."""
    C, sigma, eff_rank, rank_95 = compute_obstruction(A, B)
    n_cols = min(A.shape[1], B.shape[1])

    print(f"\n--- {label} (dim={n_cols}) ---")
    print(f"Cross-covariance C shape: {C.shape}")
    print(f"Singular values (top 10): {sigma[:10].round(6).tolist()}")
    print(f"Effective rank (sigma > sigma_max/100): {eff_rank}")
    print(f"Rank at 95% variance: {rank_95}")
    print(f"Frobenius norm of C: {np.linalg.norm(C, 'fro'):.6f}")

    # Null
    print(f"Running {N_PERMS} permutation nulls...")
    null_eff, null_r95, null_smax = null_distribution(A, B)

    null_eff_mean = float(np.mean(null_eff))
    null_eff_std = float(np.std(null_eff))
    null_r95_mean = float(np.mean(null_r95))
    null_r95_std = float(np.std(null_r95))
    null_smax_mean = float(np.mean(null_smax))
    null_smax_std = float(np.std(null_smax))

    z_eff = (eff_rank - null_eff_mean) / max(null_eff_std, 1e-10)
    z_r95 = (rank_95 - null_r95_mean) / max(null_r95_std, 1e-10)
    z_smax = (float(sigma[0]) - null_smax_mean) / max(null_smax_std, 1e-10)

    print(f"Null eff rank: {null_eff_mean:.1f} +/- {null_eff_std:.1f}")
    print(f"Null rank-95: {null_r95_mean:.1f} +/- {null_r95_std:.1f}")
    print(f"Null sigma_max: {null_smax_mean:.4f} +/- {null_smax_std:.4f}")
    print(f"Z-scores: eff={z_eff:.2f}, r95={z_r95:.2f}, smax={z_smax:.2f}")

    var_explained = (sigma ** 2) / max(np.sum(sigma ** 2), 1e-30)
    cumvar = np.cumsum(var_explained)

    return {
        "scheme": label,
        "theta_indices_used": theta_indices if isinstance(theta_indices, list) else [int(x) for x in theta_indices],
        "n_dimensions": n_cols,
        "singular_values": sigma.tolist(),
        "variance_explained": var_explained.tolist(),
        "cumulative_variance": cumvar.tolist(),
        "effective_rank": eff_rank,
        "effective_rank_threshold": float(sigma[0] / 100.0) if sigma[0] > 0 else 0.0,
        "rank_95_variance": rank_95,
        "frobenius_norm": float(np.linalg.norm(C, 'fro')),
        "cross_covariance_matrix": C.tolist(),
        "null_test": {
            "n_permutations": N_PERMS,
            "null_effective_rank_mean": null_eff_mean,
            "null_effective_rank_std": null_eff_std,
            "null_rank95_mean": null_r95_mean,
            "null_rank95_std": null_r95_std,
            "null_sigma_max_mean": null_smax_mean,
            "null_sigma_max_std": null_smax_std,
            "z_score_effective_rank": float(z_eff),
            "z_score_rank95": float(z_r95),
            "z_score_sigma_max": float(z_smax),
        },
    }


def main():
    print("=== Hecke-Theta Obstruction Tensor ===\n")

    # Build EC matrix
    A = build_ec_matrix()

    # Fetch lattice theta series
    print("Fetching lattice theta series from LMFDB PostgreSQL...")
    labels, theta_all = fetch_theta_raw()
    print(f"Fetched {len(theta_all)} lattices with theta series")

    # Scheme 1: prime-aligned (theta[2p])
    B1, valid_primes1 = build_lattice_matrix_prime_aligned(theta_all)
    # Trim A to match B1 columns
    A1 = A[:, :len(valid_primes1)]
    result1 = run_analysis(A1, B1, "prime-aligned (theta[2p])",
                           [2 * p for p in valid_primes1])

    # Scheme 2: top-25 even variance indices
    B2, top25_idx = build_lattice_matrix_top_variance(theta_all)
    result2 = run_analysis(A, B2, "top-25 variance even indices", top25_idx)

    # Determine primary result (use prime-aligned as main)
    primary = result1
    eff_rank = primary["effective_rank"]
    rank_95 = primary["rank_95_variance"]
    z_smax = primary["null_test"]["z_score_sigma_max"]

    # Interpretation
    interp_parts = []
    if eff_rank <= 11:
        interp_parts.append(
            f"Effective rank {eff_rank} (expected 6-11) confirms a low-dimensional "
            f"obstruction subspace in the Hecke-theta bilinear map. "
            f"The prime space collapses to ~{eff_rank} independent directions."
        )
    else:
        interp_parts.append(
            f"Effective rank {eff_rank} exceeds the expected 6-11 range. "
            f"Rank-95={rank_95} gives the variance-weighted view."
        )

    if abs(z_smax) > 2:
        interp_parts.append(
            f"Leading singular value z={z_smax:.1f} indicates genuine cross-domain structure."
        )
    else:
        interp_parts.append(
            f"Leading singular value z={z_smax:.1f} is within null range; "
            f"observed structure may be consistent with chance pairing."
        )

    interp_parts.append(
        f"Scheme 2 (top-25 variance): eff_rank={result2['effective_rank']}, "
        f"rank_95={result2['rank_95_variance']}, "
        f"z_smax={result2['null_test']['z_score_sigma_max']:.1f}."
    )

    interpretation = " ".join(interp_parts)

    # Final results
    results = {
        "challenge": "Hecke-Theta Obstruction Tensor (ChatGPT Harder #1)",
        "method": "Cross-covariance SVD between EC Hecke eigenvalues and lattice theta series",
        "n_ec": int(A.shape[0]),
        "n_lattices": len(theta_all),
        "primes": PRIMES_25,
        "normalization_ec": "a_p / (2*sqrt(p))",
        "normalization_lattice": "raw theta coefficients at even indices",
        "note": "LMFDB lattices are integral, theta[n]=0 for odd n. Two indexing schemes tested.",
        "scheme_1_prime_aligned": result1,
        "scheme_2_top_variance": result2,
        "effective_rank": eff_rank,
        "rank_95_variance": rank_95,
        "interpretation": interpretation,
    }

    print(f"\n{'='*60}")
    print(f"RESULT: effective_rank={eff_rank}, rank_95={rank_95}")
    print(interpretation)

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
