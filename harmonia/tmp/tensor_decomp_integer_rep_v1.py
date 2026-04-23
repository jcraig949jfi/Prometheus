"""
CANONICALIZER:tensor_decomp_integer_rep@v1 — Type B (preferred representative).

Takes a tensor_decomp_identity output (currently v1, since v2 is OPEN after
Strategy 1 falsification) and searches the T-stabilizer orbit for the
orbit element maximizing integer_fraction.

For 2x2 matmul, the T-stabilizer is the subgroup of GL(2)^3 that preserves
T under the matmul-covariant action. This can be coordinated via:
  (A, B, C) -> (P A, B Q, R C)
  with compatibility constraints that preserve T.

For the 2x2 matmul tensor, the matmul-covariant action under
(P, Q, R) in GL(2)^3 is:
  matrix_A -> P matrix_A Q^{-1}
  matrix_B -> Q matrix_B R^{-1}
  matrix_C -> P matrix_C R^{-1}
Which on the flattened 4-dim factor vectors u (for A), v (for B), w (for C)
induces specific linear transforms.

Implementing the full T-stabilizer is subtle. For this MVP Type B instance,
we use a simpler approach that searches a tractable subset of the orbit:
  (A, B, C) -> (A L, M B, C N) where L, M, N are invertible 7x7 "rank-term
  mixing" matrices. This is actually LARGER than the T-stabilizer (it's the
  full non-uniqueness of CP decomposition, which includes all orbit elements
  plus some). We score each candidate by its reconstruction residual (must
  stay near 0) AND its integer_fraction.

MVP strategy: local search in the rank-term mixing space via random
orthogonal perturbations, keeping the best-scoring candidate.

Calibration: starting from each of the 4 ALS-converged seeds, after some
number of mixing steps, can we reach a representative with integer_fraction
>= 0.9 (approaching Strassen's 1.0)?

This may fail honestly — the search space is high-dimensional and the
integer basin is a measure-zero subset. A failure here tells us that
this specific Type B search primitive is not strong enough; alternative
search primitives (simulated annealing with integer snapping, L-BFGS with
integer-distance penalty, etc.) could be tried next session.
"""

import numpy as np
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import (
    make_matmul_tensor, run_als, reconstruct, residual
)
from canonicalize_test import canonicalize_v1, known_strassen


def integer_fraction(A, B, C, atol=0.01):
    e = np.concatenate([A.flatten(), B.flatten(), C.flatten()])
    return float(np.mean(np.abs(e - np.round(e)) < atol))


def rank_term_mix(A, B, C, M):
    """Apply a rank-term mixing: (A, B, C) -> (A @ M, B @ M, C @ M^{-T}).
    This preserves T iff the mixing is appropriate. For CP decomposition
    with the scale-gauge symmetry, this matches the natural action.

    Actually this is NOT the T-stabilizer — it's a mixing that changes the
    reconstruction unless M has a specific form. For pure scale+permutation,
    M should be diagonal + permutation. For the full T-stabilizer, M needs
    to come from the matmul-covariant GL action.

    For this MVP, we'll use the simpler approach: allow M to be in GL(r),
    but PROJECT back to exact reconstruction via a residual-gradient step
    after each mixing move. The search is "find (A,B,C) with low residual
    AND high integer_fraction."
    """
    # Apply to B and C columns but not A — changes rank-term basis
    # Note: for (u_i, v_i, w_i) rank-1 structure, a rank-term re-basis
    # makes sense only if we jointly transform so product is preserved.
    r = A.shape[1]
    if M.shape != (r, r):
        raise ValueError(f"M must be {r}x{r}")
    A_new = A @ M
    B_new = B @ M
    # For tensor T = sum a_i o b_i o c_i, we need sum (A M)_i o (B M)_i o (c transformed)_i = T
    # This is not generally a symmetry. Use a different approach: see gradient_refine below.
    return A_new, B_new, C @ np.linalg.inv(M.T @ M) @ M.T  # projection attempt


def gradient_refine(A, B, C, T, n_steps=20, lr=0.01):
    """After perturbation, re-optimize (A, B, C) to minimize ||T - reconstruct||^2.
    Keeps the representative near exact reconstruction."""
    from tensor_pilot_2x2_matmul import als_step
    for _ in range(n_steps):
        A, B, C = als_step(A, B, C, T)
    return A, B, C


def search_integer_rep(A0, B0, C0, T, n_trials=200, perturbation_scale=0.5, seed=0):
    """Search for a high-integer-fraction representative in the orbit.

    Strategy: random perturbations of the factor matrices + ALS re-refinement
    to stay on the reconstruction variety. Keep the best integer_fraction
    seen while residual stays below threshold.
    """
    rng = np.random.default_rng(seed)
    best_A, best_B, best_C = A0.copy(), B0.copy(), C0.copy()
    best_res = residual(A0, B0, C0, T)
    best_if = integer_fraction(best_A, best_B, best_C)
    r = A0.shape[1]

    history = [{"trial": -1, "residual": best_res, "integer_fraction": best_if}]

    for trial in range(n_trials):
        # Random perturbation (small)
        A_new = best_A + rng.standard_normal(best_A.shape) * perturbation_scale
        B_new = best_B + rng.standard_normal(best_B.shape) * perturbation_scale
        C_new = best_C + rng.standard_normal(best_C.shape) * perturbation_scale

        # ALS refinement to stay on reconstruction variety
        A_new, B_new, C_new = gradient_refine(A_new, B_new, C_new, T, n_steps=30)

        res_new = residual(A_new, B_new, C_new, T)
        if res_new > 1e-6:
            continue  # left the reconstruction variety; discard

        # Canonicalize and score
        A_c, B_c, C_c = canonicalize_v1(A_new, B_new, C_new)
        if_new = integer_fraction(A_c, B_c, C_c)

        if if_new > best_if:
            best_A, best_B, best_C = A_c, B_c, C_c
            best_res = res_new
            best_if = if_new
            history.append({"trial": trial, "residual": res_new, "integer_fraction": if_new})

    return best_A, best_B, best_C, best_res, best_if, history


def main():
    T = make_matmul_tensor(n=2)
    print("=== CANONICALIZER:tensor_decomp_integer_rep@v1 — Type B ===\n")
    print("Objective: maximize integer_fraction while staying on reconstruction variety.\n")

    # Strassen baseline
    US, VS, WS = known_strassen()
    if_strassen = integer_fraction(US, VS, WS)
    print(f"Strassen integer_fraction: {if_strassen:.3f}")

    # Collect ALS seeds
    print("\nCollecting ALS-converged seeds...")
    seeds = []
    for seed in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=seed)
        if res < 1e-10:
            A, B, C = canonicalize_v1(A, B, C)
            if_raw = integer_fraction(A, B, C)
            seeds.append({"seed": seed, "A": A, "B": B, "C": C, "residual": res, "integer_fraction_raw": if_raw})
    print(f"  {len(seeds)} machine-precision seeds collected.\n")

    # Run Type B search on each seed
    results = []
    for s in seeds:
        print(f"Seed {s['seed']}: raw if={s['integer_fraction_raw']:.3f}, searching...")
        A_out, B_out, C_out, res_out, if_out, history = search_integer_rep(
            s["A"], s["B"], s["C"], T,
            n_trials=100, perturbation_scale=0.3, seed=s["seed"]
        )
        print(f"   -> residual={res_out:.2e}, integer_fraction={if_out:.3f}  (improved: {if_out - s['integer_fraction_raw']:+.3f})")
        results.append({
            "seed": s["seed"],
            "initial_if": s["integer_fraction_raw"],
            "final_if": if_out,
            "final_residual": res_out,
            "improvement": if_out - s["integer_fraction_raw"],
            "n_history_entries": len(history),
        })

    print()
    print("=== VERDICT on tensor_decomp_integer_rep@v1 ===")
    best_if_reached = max(r["final_if"] for r in results) if results else 0
    reached_strassen = sum(1 for r in results if r["final_if"] >= 0.9)
    print(f"  Best integer_fraction reached: {best_if_reached:.3f}")
    print(f"  Seeds reaching if >= 0.9 (approaching Strassen): {reached_strassen} / {len(results)}")
    print(f"  Strassen reference:           {if_strassen:.3f}")

    if reached_strassen > 0:
        print("\n  PASS. Type B search recovers near-integer representative from at least one orbit entry.")
    elif best_if_reached > max(r["initial_if"] for r in results) + 0.1:
        print("\n  PARTIAL. Type B search improves integer_fraction but does not reach Strassen.")
        print("  Data: the random-perturbation + ALS refinement strategy moves toward integer")
        print("  basins but does not escape to them. Stronger search primitives needed.")
    else:
        print("\n  FAIL. Type B search does not improve integer_fraction meaningfully.")
        print("  Candidate diagnosis: perturbation + ALS refinement returns to nearby")
        print("  orbit points in the same basin; the integer basin is measure-zero and")
        print("  not reached by Gaussian perturbation. Next strategy candidates:")
        print("    - simulated annealing with integer-snap moves")
        print("    - L-BFGS with explicit integer-distance penalty added to loss")
        print("    - enumeration over GL(2)^3 action (exploits matmul-covariant symmetry)")

    # Save
    out = Path(__file__).parent / "tensor_decomp_integer_rep_v1_results.json"
    dump = {
        "strassen_reference": if_strassen,
        "results": results,
        "verdict": "PASS" if reached_strassen > 0 else ("PARTIAL" if best_if_reached > max((r["initial_if"] for r in results), default=0) + 0.1 else "FAIL"),
    }
    with open(out, "w") as f:
        json.dump(dump, f, indent=2, default=str)
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
