"""
M43: Tensor rank of moonshine enrichment matrix
==================================================
Build the matrix M[partition, prime] = enrichment. Compute SVD.
If low rank: moonshine enrichment is a simple function of (partition, prime).
If high rank: each partition-prime pair is genuinely independent.
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
MOON = V2 / "moonshine_scaling_results.json"
OUT = V2 / "m43_tensor_rank_moonshine_results.json"

def main():
    t0 = time.time()
    print("=== M43: Tensor rank of moonshine enrichment matrix ===\n")

    with open(MOON) as f:
        data = json.load(f)

    partitions = data.get("enrichment_by_partition", {})
    print(f"  {len(partitions)} partitions")

    # Build enrichment matrix
    all_primes = set()
    for name, info in partitions.items():
        ep = info.get("enrichments_by_prime", {})
        all_primes.update(int(p) for p in ep.keys())
    primes = sorted(all_primes)
    part_names = sorted(partitions.keys())

    M = np.zeros((len(part_names), len(primes)))
    for i, name in enumerate(part_names):
        ep = partitions[name].get("enrichments_by_prime", {})
        for j, p in enumerate(primes):
            M[i, j] = ep.get(str(p), 0)

    print(f"  Matrix shape: {M.shape} ({len(part_names)} partitions × {len(primes)} primes)")
    print(f"  Non-zero entries: {np.count_nonzero(M)}/{M.size}")

    # SVD
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    total_var = np.sum(S**2)
    cum_var = np.cumsum(S**2) / total_var

    print(f"\n  Singular values: {[round(float(s), 2) for s in S]}")
    print(f"  Cumulative variance: {[round(float(c), 4) for c in cum_var]}")

    rank_90 = int(np.searchsorted(cum_var, 0.90) + 1)
    rank_95 = int(np.searchsorted(cum_var, 0.95) + 1)
    rank_99 = int(np.searchsorted(cum_var, 0.99) + 1)

    print(f"\n  Effective rank (90%): {rank_90}/{min(M.shape)}")
    print(f"  Effective rank (95%): {rank_95}/{min(M.shape)}")
    print(f"  Effective rank (99%): {rank_99}/{min(M.shape)}")

    # Spectral gap
    spectral_gap = float(S[0] / S[1]) if len(S) > 1 and S[1] > 0 else float('inf')
    print(f"  Spectral gap (σ₁/σ₂): {spectral_gap:.2f}")

    # First singular vector: which partitions and primes dominate?
    print(f"\n  First left singular vector (partition loadings):")
    for i, name in enumerate(part_names):
        print(f"    {name}: {U[i, 0]:.4f}")
    print(f"  First right singular vector (prime loadings):")
    for j, p in enumerate(primes):
        print(f"    p={p}: {Vt[0, j]:.4f}")

    # Rank-1 approximation quality
    M_rank1 = S[0] * np.outer(U[:, 0], Vt[0])
    residual = np.linalg.norm(M - M_rank1) / np.linalg.norm(M)
    print(f"\n  Rank-1 residual: {residual:.4f} ({1-residual**2:.1%} explained)")

    # NMF-like: is M approximately a * b^T?
    # Check if all entries in first SV are same sign
    u_sign = np.sign(U[:, 0])
    v_sign = np.sign(Vt[0])
    same_sign_u = float(np.sum(u_sign == u_sign[0]) / len(u_sign))
    same_sign_v = float(np.sum(v_sign == v_sign[0]) / len(v_sign))

    elapsed = time.time() - t0
    output = {
        "probe": "M43", "title": "Tensor rank of moonshine enrichment",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "matrix_shape": list(M.shape),
        "singular_values": [round(float(s), 4) for s in S],
        "cumulative_variance": [round(float(c), 4) for c in cum_var],
        "effective_rank_90": rank_90,
        "effective_rank_95": rank_95,
        "spectral_gap": round(spectral_gap, 2),
        "rank1_residual": round(float(residual), 4),
        "partition_loadings": {name: round(float(U[i, 0]), 4) for i, name in enumerate(part_names)},
        "prime_loadings": {str(p): round(float(Vt[0, j]), 4) for j, p in enumerate(primes)},
        "assessment": None,
    }

    if rank_90 == 1:
        output["assessment"] = f"RANK-1: moonshine enrichment ≈ partition_strength × prime_sensitivity. Spectral gap={spectral_gap:.1f}. Single factor explains 90%+"
    elif rank_90 == 2:
        output["assessment"] = f"RANK-2: two independent enrichment modes. Gap={spectral_gap:.1f}. First mode explains {cum_var[0]:.0%}"
    else:
        output["assessment"] = f"HIGH RANK ({rank_90}): each partition-prime pair is partially independent. No simple factorization"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
