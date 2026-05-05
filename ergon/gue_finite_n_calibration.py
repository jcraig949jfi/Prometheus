#!/usr/bin/env python3
"""
Finite-N GUE calibration for the F011 rank-0 zero deficit.

Aporia 2026-04-15: var/Wigner = 0.60 matches the finite-N GUE correction exactly.
Large-N asymptotic spacing variance 0.107 / Wigner 0.178 = 0.60. If the rank-0
EC deficit is just the finite-N truncation, MF L-functions with the same number
of stored zeros should show the same deficit. They do not (MF gap1 ratio=0.986).

This script estimates the per-N finite-size correction by sampling GUE.
For each N, generate many N x N Hermitian Gaussian matrices, extract consecutive
unfolded eigenvalue gaps, and report gap1..gap4 variance vs the Wigner surmise.

Output: ergon/results/gue_finite_n_calibration.json
"""
import json
import time
from pathlib import Path

import numpy as np

OUT_PATH = Path(__file__).resolve().parent / "results" / "gue_finite_n_calibration.json"

GAUDIN_VAR = 3.0 * np.pi / 8.0 - 1.0  # Wigner-surmise NN var for GUE, ~0.1781


def sample_gue_gaps(N: int, n_matrices: int, rng: np.random.Generator):
    """Generate n_matrices GUE matrices of size N x N, return unfolded consecutive
    gap arrays (gap1 per matrix = eigenvalue[1]-eigenvalue[0] after normalization)."""
    gap_cols = [[] for _ in range(4)]  # gap1, gap2, gap3, gap4
    for _ in range(n_matrices):
        re = rng.standard_normal((N, N))
        im = rng.standard_normal((N, N))
        A = (re + 1j * im) / np.sqrt(2.0)
        H = (A + A.conj().T) / np.sqrt(2.0)  # GUE normalization
        w = np.sort(np.linalg.eigvalsh(H))  # ascending
        gaps = np.diff(w)
        mean_gap = gaps.mean()
        if mean_gap <= 0:
            continue
        norm_gaps = gaps / mean_gap
        # central-zero analog: take gaps[0..3] — matches "first 4 gaps of each
        # L-function", where each L-function delivers ~O(40) zeros. Pick the 4 gaps
        # closest to the center of the spectrum to stay in bulk.
        mid = N // 2 - 2
        for k in range(4):
            gap_cols[k].append(norm_gaps[mid + k])
    return [np.array(c) for c in gap_cols]


def main():
    rng = np.random.default_rng(42)
    # Match LMFDB: each L-function stores ~20-40 zeros -> N=20..40 bulk matrix
    # simulates comparable local gap statistics.
    Ns = [10, 20, 30, 40, 60, 100]
    # For each N, sample enough matrices to match LMFDB sample sizes.
    # 200K curves x 4 gaps = 800K gap values; here we sample 5000 matrices per N
    # which gives 5000 per gap (noisy but sufficient for variance).
    n_matrices = 5000

    rows = []
    t0 = time.time()
    print(f"Finite-N GUE calibration: N in {Ns}, {n_matrices} matrices each")
    print(f"Wigner surmise NN variance = {GAUDIN_VAR:.4f}\n")

    print(f"{'N':>4} {'gap1_var':>10} {'g1/Wigner':>10} {'gap2_var':>10} {'g2/Wigner':>10} "
          f"{'gap3_var':>10} {'g3/Wigner':>10} {'gap4_var':>10} {'g4/Wigner':>10}")
    print("-" * 90)

    for N in Ns:
        gaps = sample_gue_gaps(N, n_matrices, rng)
        variances = [float(np.var(g, ddof=1)) for g in gaps]
        ratios = [v / GAUDIN_VAR for v in variances]
        print(f"{N:>4} " + "".join(
            f"{v:>10.4f} {r:>10.4f}" for v, r in zip(variances, ratios)
        ))
        rows.append({
            "N": N,
            "n_matrices": n_matrices,
            "variances": variances,
            "ratios": ratios,
        })

    elapsed = time.time() - t0
    print(f"\nElapsed: {elapsed:.1f}s")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump({
            "wigner_surmise_var": GAUDIN_VAR,
            "n_matrices_per_N": n_matrices,
            "results": rows,
            "elapsed_seconds": round(elapsed, 1),
        }, f, indent=1)
    print(f"Saved {OUT_PATH}")

    # Interpretive summary
    print("\nINTERPRETATION:")
    print(f"Aporia's hypothesis: finite-N GUE correction explains ratio=0.60.")
    for row in rows:
        print(f"  N={row['N']:3d}: gap1 ratio = {row['ratios'][0]:.4f}")
    print("\nEC observed gap1 ratio: 0.6607 (200K rank-0 curves)")
    print("MF observed gap1 ratio: 0.9857 (100K modular forms)")
    print("If both families share the same finite-N correction, they should match.")
    print("They do not -> the deficit is arithmetic, not purely finite-N.")


if __name__ == "__main__":
    main()
