"""
Maass Coefficient-Lattice Theta Cross-Coherence

Test: do Maass Hecke eigenvalues at prime indices correlate with
lattice theta coefficients at the same primes?

Maass: 1000 forms x 25 primes -> matrix A  (c_p values)
Lattice: 1000 lattices x 25 primes -> matrix B (theta[2p] for even lattices)

Cross-covariance C = A^T B  (25x25)
SVD -> effective rank at 95% variance
Compare to EC-lattice obstruction result (rank_95=9, z=2.24)
Null: permuted pairings

Challenge 330.
"""

import json
import numpy as np
from pathlib import Path

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

N_FORMS = 1000
N_LATTICES = 1000
N_PERMS = 200
RNG = np.random.default_rng(42)

OUT_DIR = Path(__file__).parent
RESULTS_PATH = OUT_DIR / "maass_lattice_cross_coherence_results.json"

MAASS_PATH = Path(__file__).resolve().parents[1] / "maass" / "data" / "maass_with_coefficients.json"
LATTICE_PATH = Path(__file__).resolve().parents[1] / "lmfdb_dump" / "lat_lattices.json"


def build_maass_matrix():
    """Build A: N_FORMS x 25 matrix of Maass c_p at prime indices."""
    with open(MAASS_PATH) as f:
        maass_data = json.load(f)

    # Filter forms with enough coefficients (need index 97)
    valid = [m for m in maass_data if len(m["coefficients"]) > 97]
    print(f"Maass forms with >= 98 coefficients: {len(valid)} / {len(maass_data)}")

    # Sample N_FORMS diverse forms using hash-based selection
    # Sort by spectral parameter to get diversity, then subsample
    valid_sorted = sorted(valid, key=lambda m: float(m.get("spectral_parameter", 0)))
    step = max(1, len(valid_sorted) // N_FORMS)
    selected = valid_sorted[::step][:N_FORMS]

    A = np.zeros((len(selected), 25))
    spectral_params = []
    levels = []
    for i, m in enumerate(selected):
        coeffs = m["coefficients"]
        for j, p in enumerate(PRIMES_25):
            # Maass coefficients are 0-indexed: coefficients[n] = c(n+1)
            # So c_p is at index p-1
            A[i, j] = coeffs[p - 1] if (p - 1) < len(coeffs) else 0.0
        spectral_params.append(m.get("spectral_parameter", None))
        levels.append(m.get("level", None))

    print(f"Maass matrix A: {A.shape}")
    sp_floats = [float(s) for s in spectral_params if s]
    print(f"  Spectral param range: [{min(sp_floats):.4f}, {max(sp_floats):.4f}]")
    print(f"  Level range: [{min(l for l in levels if l)}, {max(l for l in levels if l)}]")
    return A, spectral_params, levels


def build_lattice_matrix_prime_aligned():
    """Build B using theta[2*p] for each prime p (where 2*p < 151)."""
    with open(LATTICE_PATH) as f:
        lat_data = json.load(f)
    records = lat_data["records"]

    # Filter lattices with theta series
    valid = [r for r in records if r.get("theta_series") and len(r["theta_series"]) > 0]
    print(f"Lattices with theta series: {len(valid)}")

    # Sample N_LATTICES diverse lattices
    step = max(1, len(valid) // N_LATTICES)
    selected = valid[::step][:N_LATTICES]

    valid_primes = [p for p in PRIMES_25 if 2 * p < 151]
    n_cols = len(valid_primes)
    B = np.zeros((len(selected), n_cols))
    dims = []
    for i, r in enumerate(selected):
        theta = r["theta_series"]
        for j, p in enumerate(valid_primes):
            idx = 2 * p
            B[i, j] = theta[idx] if idx < len(theta) else 0.0
        dims.append(r.get("dim", None))

    print(f"Lattice matrix B (prime-aligned): {B.shape}, primes used: {len(valid_primes)}")
    print(f"  Even indices used: {[2*p for p in valid_primes]}")
    print(f"  Dimension distribution: {dict(zip(*np.unique(dims, return_counts=True)))}")
    return B, valid_primes, dims


def build_lattice_matrix_top_variance():
    """Build B using top-25 variance even indices from theta series."""
    with open(LATTICE_PATH) as f:
        lat_data = json.load(f)
    records = lat_data["records"]
    valid = [r for r in records if r.get("theta_series") and len(r["theta_series"]) > 0]
    step = max(1, len(valid) // N_LATTICES)
    selected = valid[::step][:N_LATTICES]

    max_len = max(len(r["theta_series"]) for r in selected)
    B_full = np.zeros((len(selected), max_len))
    for i, r in enumerate(selected):
        theta = r["theta_series"]
        B_full[i, :len(theta)] = theta

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


def build_lattice_matrix_prime_squared():
    """Build B using theta[p^2] for each prime p (where p^2 < 151)."""
    with open(LATTICE_PATH) as f:
        lat_data = json.load(f)
    records = lat_data["records"]
    valid = [r for r in records if r.get("theta_series") and len(r["theta_series"]) > 0]
    step = max(1, len(valid) // N_LATTICES)
    selected = valid[::step][:N_LATTICES]

    valid_primes = [p for p in PRIMES_25 if p * p < 151]
    # p^2 < 151 means p <= 12, so primes: 2,3,5,7,11
    n_cols = len(valid_primes)
    B = np.zeros((len(selected), n_cols))
    for i, r in enumerate(selected):
        theta = r["theta_series"]
        for j, p in enumerate(valid_primes):
            idx = p * p
            B[i, j] = theta[idx] if idx < len(theta) else 0.0

    print(f"Lattice matrix B (p^2-indexed): {B.shape}, primes used: {valid_primes}")
    return B, valid_primes


def compute_obstruction(A, B, standardize=True):
    """Compute cross-covariance and SVD."""
    n_cols = min(A.shape[1], B.shape[1])
    A_use = A[:, :n_cols].copy()
    B_use = B[:, :n_cols].copy()

    # Center columns
    A_use -= A_use.mean(axis=0, keepdims=True)
    B_use -= B_use.mean(axis=0, keepdims=True)

    if standardize:
        a_std = A_use.std(axis=0, keepdims=True)
        b_std = B_use.std(axis=0, keepdims=True)
        a_std[a_std < 1e-12] = 1.0
        b_std[b_std < 1e-12] = 1.0
        A_use /= a_std
        B_use /= b_std

    n = min(A_use.shape[0], B_use.shape[0])
    C = A_use.T @ B_use / n

    U, sigma, Vt = np.linalg.svd(C, full_matrices=False)

    if sigma[0] > 0:
        threshold = sigma[0] / 100.0
        eff_rank = int(np.sum(sigma > threshold))
    else:
        eff_rank = 0

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
    print("=" * 60)
    print("Maass Coefficient-Lattice Theta Cross-Coherence")
    print("Challenge 330")
    print("=" * 60)

    # ---- Build Maass matrix ----
    A, spectral_params, levels = build_maass_matrix()

    # ---- Scheme 1: prime-aligned (theta[2p]) ----
    B1, valid_primes1, lat_dims = build_lattice_matrix_prime_aligned()
    A1 = A[:, :len(valid_primes1)]
    result1 = run_analysis(A1, B1, "prime-aligned (theta[2p])",
                           [2 * p for p in valid_primes1])

    # ---- Scheme 2: top-25 variance even indices ----
    B2, top25_idx = build_lattice_matrix_top_variance()
    result2 = run_analysis(A, B2, "top-25 variance even indices", top25_idx)

    # ---- Scheme 3: p^2-indexed (theta[p^2]) ----
    B3, valid_primes3 = build_lattice_matrix_prime_squared()
    A3 = A[:, :len(valid_primes3)]
    result3 = run_analysis(A3, B3, "p^2-indexed (theta[p^2])",
                           [p * p for p in valid_primes3])

    # ---- EC comparison baseline ----
    ec_baseline = {
        "source": "hecke_theta_obstruction_results.json",
        "ec_effective_rank": 21,
        "ec_rank_95_variance": 9,
        "ec_z_score_sigma_max": 2.24,
        "note": "EC a_p/(2*sqrt(p)) vs lattice theta[2p], same methodology"
    }

    # ---- Primary result (use prime-aligned as main) ----
    primary = result1
    eff_rank = primary["effective_rank"]
    rank_95 = primary["rank_95_variance"]
    z_smax = primary["null_test"]["z_score_sigma_max"]

    # ---- Interpretation ----
    interp_parts = []

    # Compare to EC
    ec_r95 = ec_baseline["ec_rank_95_variance"]
    ec_z = ec_baseline["ec_z_score_sigma_max"]

    interp_parts.append(
        f"Maass-lattice cross-coherence: effective_rank={eff_rank}, "
        f"rank_95={rank_95}, z_smax={z_smax:.2f}."
    )

    if rank_95 != ec_r95:
        interp_parts.append(
            f"EC-lattice rank_95={ec_r95} vs Maass-lattice rank_95={rank_95}: "
            f"{'Maass produces higher obstruction rank, suggesting richer cross-domain coupling.' if rank_95 > ec_r95 else 'Maass produces lower obstruction rank, suggesting weaker coupling than EC.'}"
        )
    else:
        interp_parts.append(
            f"Maass and EC produce identical rank_95={rank_95}, suggesting a universal obstruction dimension."
        )

    if abs(z_smax) > 2:
        interp_parts.append(
            f"Leading singular value z={z_smax:.2f} exceeds null (genuine cross-domain structure)."
        )
    elif abs(z_smax) > 1:
        interp_parts.append(
            f"Leading singular value z={z_smax:.2f} is marginal (weak signal above null)."
        )
    else:
        interp_parts.append(
            f"Leading singular value z={z_smax:.2f} is within null range (no genuine cross-domain signal)."
        )

    interp_parts.append(
        f"Scheme 2 (top-25 variance): eff_rank={result2['effective_rank']}, "
        f"rank_95={result2['rank_95_variance']}, z_smax={result2['null_test']['z_score_sigma_max']:.2f}. "
        f"Scheme 3 (p^2-indexed): eff_rank={result3['effective_rank']}, "
        f"rank_95={result3['rank_95_variance']}, z_smax={result3['null_test']['z_score_sigma_max']:.2f}."
    )

    interpretation = " ".join(interp_parts)

    # ---- Assemble results ----
    results = {
        "challenge": "Maass Coefficient-Lattice Theta Cross-Coherence (Challenge 330)",
        "method": "Cross-covariance SVD between Maass Hecke eigenvalues at prime indices and lattice theta series",
        "n_maass_forms": int(A.shape[0]),
        "n_lattices": N_LATTICES,
        "primes": PRIMES_25,
        "maass_data": {
            "source": str(MAASS_PATH),
            "total_forms_available": 14995,
            "forms_used": int(A.shape[0]),
            "coefficient_type": "c_p at prime index p (0-indexed: coefficients[p-1])",
            "spectral_param_range": [
                min(float(s) for s in spectral_params if s is not None),
                max(float(s) for s in spectral_params if s is not None),
            ],
        },
        "lattice_data": {
            "source": str(LATTICE_PATH),
            "total_lattices_available": 39293,
            "lattices_used": N_LATTICES,
            "theta_series_length": 151,
            "note": "LMFDB integral lattices; theta[n]=0 for odd n in even lattices",
        },
        "scheme_1_prime_aligned": result1,
        "scheme_2_top_variance": result2,
        "scheme_3_p_squared": result3,
        "ec_comparison_baseline": ec_baseline,
        "effective_rank": eff_rank,
        "rank_95_variance": rank_95,
        "interpretation": interpretation,
    }

    print(f"\n{'=' * 60}")
    print(f"RESULT: effective_rank={eff_rank}, rank_95={rank_95}, z_smax={z_smax:.2f}")
    print(f"EC baseline: rank_95={ec_r95}, z={ec_z:.2f}")
    print(interpretation)

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
