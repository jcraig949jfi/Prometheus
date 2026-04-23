"""
Pilot: 2x2 matrix multiplication tensor decomposition via ALS + multi-restart.

Question (one bit): does a dumb search stack rediscover Strassen's rank-7
decomposition of the 2x2 matmul tensor (shape 4x4x4) over R within a
modest budget?

Calibration anchors:
  - Rank 8 decomposition: trivial (naive algorithm).
  - Rank 7 decomposition: Strassen 1969. Exact, integer-valued factors.
  - Rank 6: Winograd 1971 lower bound says impossible over R.

Budget: 20 seeds x 500 ALS iters each + small outer mutation loop.
  Expected runtime: <= 60 seconds total.

MAP-Elites proxy: archive best-per-cell where cells are
  (max_abs_entry_bucket, integer_like_fraction_bucket).

Not a full GA (a full GA over factor-matrix genomes isn't where the 2x2
bottleneck lives); ALS + multi-restart is the standard baseline and the
cheapest honest answer to the pilot question.
"""

import numpy as np
import time
import json
from pathlib import Path


def make_matmul_tensor(n=2):
    """2x2 matmul tensor at n=2 in (ij, jk, ik) flattening -> shape (4, 4, 4).
    T[ij, jk, ik] = 1 iff middle indices match, else 0.
    """
    T = np.zeros((n * n, n * n, n * n))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                ij = i * n + j
                jk = j * n + k
                ik = i * n + k
                T[ij, jk, ik] = 1.0
    return T


def reconstruct(A, B, C):
    """T_hat[i,j,k] = sum_r A[i,r] B[j,r] C[k,r]."""
    return np.einsum("ir,jr,kr->ijk", A, B, C)


def residual(A, B, C, T):
    return float(np.linalg.norm(reconstruct(A, B, C) - T))


def khatri_rao(X, Y):
    """Column-wise Kronecker product. Shapes (a, r) and (b, r) -> (a*b, r)."""
    a, r = X.shape
    b, _ = Y.shape
    return (X[:, None, :] * Y[None, :, :]).reshape(a * b, r)


def als_step(A, B, C, T, reg=1e-10):
    """One round of alternating least squares.

    For T[i,j,k] = sum_r A[i,r] B[j,r] C[k,r]:
      mode-0: T_(0)[i, j*n+k] = T[i,j,k] = A @ khatri_rao(B,C).T
      mode-1: T_(1)[j, i*n+k] = T[i,j,k] = B @ khatri_rao(A,C).T
      mode-2: T_(2)[k, i*n+j] = T[i,j,k] = C @ khatri_rao(A,B).T

    (my khatri_rao(X,Y) gives [first_idx*b + second_idx, r] = X[first,r]*Y[second,r])
    """
    n = T.shape[0]

    # Mode-0: solve for A given B, C
    T0 = T.reshape(n, n * n)                        # (i, j*n+k)
    KR = khatri_rao(B, C)                           # [j*n+k, r] = B[j,r]*C[k,r]
    A = np.linalg.lstsq(KR, T0.T, rcond=None)[0].T

    # Mode-1: solve for B given A, C
    T1 = T.transpose(1, 0, 2).reshape(n, n * n)     # (j, i*n+k)
    KR = khatri_rao(A, C)
    B = np.linalg.lstsq(KR, T1.T, rcond=None)[0].T

    # Mode-2: solve for C given A, B
    T2 = T.transpose(2, 0, 1).reshape(n, n * n)     # (k, i*n+j)
    KR = khatri_rao(A, B)
    C = np.linalg.lstsq(KR, T2.T, rcond=None)[0].T

    return A, B, C


def run_als(T, rank, max_iters=500, tol=1e-12, seed=0, init_scale=1.0):
    """Random init + ALS until residual below tol or max_iters hit."""
    rng = np.random.default_rng(seed)
    n = T.shape[0]
    A = rng.standard_normal((n, rank)) * init_scale
    B = rng.standard_normal((n, rank)) * init_scale
    C = rng.standard_normal((n, rank)) * init_scale

    prev_res = np.inf
    for it in range(max_iters):
        A, B, C = als_step(A, B, C, T)
        res = residual(A, B, C, T)
        if res < tol:
            return A, B, C, res, it
        # early stopping on stagnation
        if it > 20 and abs(prev_res - res) < tol * 1e-2:
            break
        prev_res = res
    return A, B, C, res, it


def integer_like_fraction(A, B, C, atol=0.1):
    """Fraction of entries within atol of an integer."""
    all_e = np.concatenate([A.flatten(), B.flatten(), C.flatten()])
    near_int = np.sum(np.abs(all_e - np.round(all_e)) < atol)
    return near_int / len(all_e)


def map_elites_cell(A, B, C):
    """(max_abs_bucket in {0,1,2,3,4+}, int_frac_bucket in {0,1,2,3,4}).

    Serves as MAP-Elites behavior descriptor.
    """
    all_e = np.concatenate([A.flatten(), B.flatten(), C.flatten()])
    max_abs = float(np.max(np.abs(all_e)))
    max_abs_bucket = int(min(4, np.floor(max_abs)))
    int_frac = integer_like_fraction(A, B, C)
    int_bucket = int(min(4, np.floor(int_frac * 5)))
    return (max_abs_bucket, int_bucket)


def rescale_for_diversity(A, B, C):
    """Normalize columns of A and B to unit norm, absorb into C.

    Canonicalization for comparison — otherwise arbitrary scalings obscure
    whether solutions are equivalent. Not an orbit-equivalence check
    (that's harder); just a scale canonicalization.
    """
    r = A.shape[1]
    for ri in range(r):
        a_norm = np.linalg.norm(A[:, ri])
        b_norm = np.linalg.norm(B[:, ri])
        if a_norm > 1e-10 and b_norm > 1e-10:
            A[:, ri] /= a_norm
            B[:, ri] /= b_norm
            C[:, ri] *= a_norm * b_norm
    return A, B, C


def run_pilot(T, rank=7, n_seeds=20, max_iters=500, exact_tol=1e-8):
    """Outer loop: N restart seeds; for each, run ALS; archive MAP-Elites cells."""
    archive = {}  # cell -> (residual, seed, iters)
    per_seed = []
    best_res = np.inf
    best_iters = None
    t0 = time.time()
    for seed in range(n_seeds):
        A, B, C, res, iters = run_als(T, rank=rank, max_iters=max_iters, seed=seed)
        A, B, C = rescale_for_diversity(A, B, C)
        # recompute residual after rescaling (should be invariant; sanity check)
        res2 = residual(A, B, C, T)
        cell = map_elites_cell(A, B, C)
        int_frac = integer_like_fraction(A, B, C)
        per_seed.append({
            "seed": seed,
            "residual": res,
            "residual_after_rescale": res2,
            "iters": iters,
            "cell": cell,
            "integer_fraction": float(int_frac),
            "converged_exact": bool(res < exact_tol),
        })
        if cell not in archive or archive[cell]["residual"] > res2:
            archive[cell] = {"residual": res2, "seed": seed, "iters": iters}
        if res < best_res:
            best_res = res
            best_iters = iters
    elapsed = time.time() - t0

    successes = sum(1 for s in per_seed if s["converged_exact"])
    return {
        "rank": rank,
        "n_seeds": n_seeds,
        "exact_tol": exact_tol,
        "best_residual": best_res,
        "best_iters": best_iters,
        "successes": successes,
        "success_rate": successes / n_seeds,
        "archive_cells": len(archive),
        "elapsed_sec": round(elapsed, 2),
        "per_seed": per_seed,
        "archive": {str(k): v for k, v in archive.items()},
    }


def main():
    T = make_matmul_tensor(n=2)
    print(f"Tensor T shape={T.shape}, nonzero count={int(np.sum(T != 0))}")
    print(f"  ||T||_F = {np.linalg.norm(T):.6f}")

    results = {}

    # Run at rank 7 (Strassen) and rank 8 (naive/easy) for calibration
    for rank in [8, 7, 6]:
        print(f"\n=== rank = {rank} ===")
        r = run_pilot(T, rank=rank, n_seeds=20, max_iters=500, exact_tol=1e-8)
        print(
            f"  success_rate = {r['success_rate']:.2f}  "
            f"({r['successes']}/{r['n_seeds']} seeds reached residual<{r['exact_tol']})"
        )
        print(
            f"  best_residual = {r['best_residual']:.3e} at iter {r['best_iters']}"
        )
        print(f"  archive cells populated: {r['archive_cells']}")
        print(f"  elapsed: {r['elapsed_sec']}s")
        results[f"rank_{rank}"] = r

    out = Path(__file__).parent / "tensor_pilot_2x2_matmul_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults written to {out}")

    # Verdict
    r7 = results["rank_7"]
    r8 = results["rank_8"]
    r6 = results["rank_6"]
    print("\n=== VERDICT ===")
    print(f"  rank 8 (easy):     {r8['success_rate']:.2f} success rate")
    print(f"  rank 7 (Strassen): {r7['success_rate']:.2f} success rate")
    print(f"  rank 6 (impossible): {r6['success_rate']:.2f} success rate"
          f" (should be 0; best_residual={r6['best_residual']:.3e})")
    if r7["success_rate"] >= 0.3:
        print("  -> Search primitive reaches Strassen at useful rate. Direction viable.")
    elif r7["success_rate"] > 0:
        print("  -> Search primitive reaches Strassen but rarely. Needs upgrade.")
    else:
        print("  -> Search primitive does NOT reach Strassen. Primitive is bottleneck.")
    if r6["success_rate"] > 0:
        print("  WARNING: rank 6 'succeeded'. Residual tolerance may be too loose"
              " OR bug in reconstruction.")


if __name__ == "__main__":
    main()
