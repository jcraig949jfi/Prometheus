"""
Orbit-membership test on the 4 machine-precision ALS seeds, per James's
decision tree:

  For each pair (i, j) of converged seeds, solve
    min_{(P, Q, R) in GL(2, F)^3} || v1_canonicalize(seed_j)
                                   - v1_canonicalize(apply_gl2(seed_i, P, Q, R)) ||

  over F = R (real) and F = C (complex).

Outcomes per James:
  (O1) Both R and C reach machine precision on all 6 pairs
       -> no splitting signal; v1-insufficiency claim stands; numerical
          slack ruled out.
  (O2) C reaches machine precision but R gets stuck on some pair
       -> real-orbit splitting on this specific problem; findings in
          its own right.
  (O3) Both get stuck
       -> seeds are not precisely in the orbit at claimed precision
          (possibility 2 from v1 critique).

Each outcome reshapes v2's declared_limitations differently. Run before
whitepaper revision.

Implementation:
  - Parameterize (P, Q, R) as 12 real variables (resp. 24 for complex).
  - Apply the verified matmul-covariant GL(2)^3 action.
  - Compute L2 distance after v1 canonicalization of both sides.
  - Use scipy L-BFGS-B with ~20 random restarts; report minimum per pair.
"""

import numpy as np
import sys
from pathlib import Path
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import make_matmul_tensor, run_als, residual
from canonicalize_test import canonicalize_v1
from tensor_gl2_action import apply_gl2_action


def get_converged_seeds(T, n_seeds=20, rank=7, tol=1e-10):
    seeds = []
    for seed in range(n_seeds):
        A, B, C, res, _ = run_als(T, rank=rank, max_iters=500, seed=seed)
        if res < tol:
            seeds.append({
                "seed": seed, "A": A, "B": B, "C": C, "residual": res,
            })
    return seeds


def v1_flatten(A, B, C):
    """v1-canonicalize and flatten to a 1D vector for L2 comparison."""
    A_c, B_c, C_c = canonicalize_v1(A, B, C)
    return np.concatenate([A_c.flatten(), B_c.flatten(), C_c.flatten()])


def objective_real(x, seed_i_ABC, seed_j_flat):
    """Apply real (P, Q, R) to seed_i, compute L2 distance to seed_j."""
    P = x[0:4].reshape(2, 2)
    Q = x[4:8].reshape(2, 2)
    R = x[8:12].reshape(2, 2)
    detP = np.linalg.det(P)
    detQ = np.linalg.det(Q)
    detR = np.linalg.det(R)
    # Penalize near-singular
    if abs(detP) < 0.01 or abs(detQ) < 0.01 or abs(detR) < 0.01:
        return 1e6
    try:
        A_t, B_t, C_t = apply_gl2_action(*seed_i_ABC, P, Q, R)
        flat = v1_flatten(A_t, B_t, C_t)
        diff = flat - seed_j_flat
        return float(np.linalg.norm(diff))
    except np.linalg.LinAlgError:
        return 1e6


def orbit_membership_real(seed_i_ABC, seed_j_ABC, n_restarts=20, seed=0):
    """Find min distance over real (P, Q, R) ∈ GL(2, R)^3."""
    seed_j_flat = v1_flatten(*seed_j_ABC)
    rng = np.random.default_rng(seed)
    best = np.inf
    best_x = None
    # Trial 0 uses identity
    for r in range(n_restarts):
        if r == 0:
            x0 = np.array([1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], dtype=float)
        else:
            # Random init near identity
            scale = 0.5 + 0.5 * rng.random()
            x0 = np.eye(2).flatten().tolist() * 3
            x0 = np.array(x0) + rng.standard_normal(12) * scale
        try:
            result = minimize(
                objective_real, x0,
                args=(seed_i_ABC, seed_j_flat),
                method="L-BFGS-B",
                options={"maxiter": 300, "ftol": 1e-14, "gtol": 1e-10},
            )
            if result.fun < best:
                best = result.fun
                best_x = result.x
        except Exception:
            continue
    return best, best_x


def objective_complex(x_split, seed_i_ABC, seed_j_ABC):
    """Apply complex (P, Q, R) to seed_i. Work in split-real form (24 reals
    -> 3 complex 2x2 matrices).

    Since v1-canonicalize is defined for real, and the complex action
    applied to real inputs produces complex outputs, we compare the
    REAL+IMAG parts of the complex transformed seed against the real
    seed_j. For seeds to be equivalent over C, they must equal after
    real-projection (i.e., imag part vanishes).
    """
    # 24 reals = 12 real parts + 12 imag parts of (P, Q, R)
    P_re = x_split[0:4].reshape(2, 2)
    P_im = x_split[4:8].reshape(2, 2)
    Q_re = x_split[8:12].reshape(2, 2)
    Q_im = x_split[12:16].reshape(2, 2)
    R_re = x_split[16:20].reshape(2, 2)
    R_im = x_split[20:24].reshape(2, 2)
    P = P_re + 1j * P_im
    Q = Q_re + 1j * Q_im
    R = R_re + 1j * R_im

    try:
        detP = np.linalg.det(P)
        detQ = np.linalg.det(Q)
        detR = np.linalg.det(R)
        if abs(detP) < 0.01 or abs(detQ) < 0.01 or abs(detR) < 0.01:
            return 1e6

        # Convert seed factors to complex
        A_c = seed_i_ABC[0].astype(complex)
        B_c = seed_i_ABC[1].astype(complex)
        C_c = seed_i_ABC[2].astype(complex)
        # Apply action in complex arithmetic (reuse apply_gl2_action with complex inputs)
        A_t, B_t, C_t = apply_gl2_action(A_c, B_c, C_c, P, Q, R)

        # For orbit-equivalence, we want the REAL projection to match seed_j.
        # Full match requires A_t, B_t, C_t to have zero imag part.
        imag_penalty = (
            np.linalg.norm(A_t.imag) + np.linalg.norm(B_t.imag) + np.linalg.norm(C_t.imag)
        )

        # Real parts compared via v1 canonicalization
        A_t_re = A_t.real
        B_t_re = B_t.real
        C_t_re = C_t.real
        flat_t = v1_flatten(A_t_re, B_t_re, C_t_re)
        flat_j = v1_flatten(*seed_j_ABC)
        real_diff = float(np.linalg.norm(flat_t - flat_j))

        # Total: real-part distance + imag-penalty (imag should be zero at orbit match)
        return real_diff + imag_penalty
    except (np.linalg.LinAlgError, ValueError):
        return 1e6


def orbit_membership_complex(seed_i_ABC, seed_j_ABC, n_restarts=20, seed=0):
    """Find min distance over complex (P, Q, R) ∈ GL(2, C)^3."""
    rng = np.random.default_rng(seed)
    best = np.inf
    best_x = None
    for r in range(n_restarts):
        if r == 0:
            # Identity start (P = Q = R = I real)
            x0 = np.array([
                1, 0, 0, 1, 0, 0, 0, 0,  # P real + imag
                1, 0, 0, 1, 0, 0, 0, 0,  # Q real + imag
                1, 0, 0, 1, 0, 0, 0, 0,  # R real + imag
            ], dtype=float)
        else:
            scale = 0.5 + 0.5 * rng.random()
            x0 = np.concatenate([
                np.eye(2).flatten(), np.zeros(4),  # P = I + 0i
                np.eye(2).flatten(), np.zeros(4),
                np.eye(2).flatten(), np.zeros(4),
            ]).astype(float)
            x0 = x0 + rng.standard_normal(24) * scale
        try:
            result = minimize(
                objective_complex, x0,
                args=(seed_i_ABC, seed_j_ABC),
                method="L-BFGS-B",
                options={"maxiter": 500, "ftol": 1e-14, "gtol": 1e-10},
            )
            if result.fun < best:
                best = result.fun
                best_x = result.x
        except Exception:
            continue
    return best, best_x


def main():
    T = make_matmul_tensor(n=2)
    print("=== Orbit-membership test on 4 machine-precision ALS seeds ===\n")

    seeds = get_converged_seeds(T, n_seeds=20, rank=7, tol=1e-10)
    print(f"Collected {len(seeds)} machine-precision seeds.\n")

    n = len(seeds)
    # Pairs (i, j) with i < j
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    print(f"Testing {len(pairs)} pairs over R and C.\n")

    results = []
    for (i, j) in pairs:
        si = (seeds[i]["A"], seeds[i]["B"], seeds[i]["C"])
        sj = (seeds[j]["A"], seeds[j]["B"], seeds[j]["C"])
        label = f"seed{seeds[i]['seed']}_vs_seed{seeds[j]['seed']}"
        print(f"Pair {label}:")

        # Real test
        best_r, _ = orbit_membership_real(si, sj, n_restarts=20, seed=i * 10 + j)
        print(f"  R: min residual = {best_r:.4e}  {'PASS' if best_r < 1e-6 else 'FAIL' if best_r > 1e-3 else 'BORDERLINE'}")

        # Complex test
        best_c, _ = orbit_membership_complex(si, sj, n_restarts=20, seed=i * 10 + j + 100)
        print(f"  C: min residual = {best_c:.4e}  {'PASS' if best_c < 1e-6 else 'FAIL' if best_c > 1e-3 else 'BORDERLINE'}")

        # Per-pair outcome
        if best_r < 1e-6 and best_c < 1e-6:
            outcome = "O1_both_R_and_C_pass"
        elif best_c < 1e-6 and best_r > 1e-3:
            outcome = "O2_splitting_signal_R_stuck_C_ok"
        elif best_r > 1e-3 and best_c > 1e-3:
            outcome = "O3_both_stuck_numerical_slack"
        else:
            outcome = "borderline_inconclusive"
        print(f"  -> {outcome}")
        results.append({
            "pair": label,
            "R_residual": best_r,
            "C_residual": best_c,
            "outcome": outcome,
        })
        print()

    # Aggregate verdict
    print("=" * 60)
    print("AGGREGATE VERDICT")
    print("=" * 60)
    n_o1 = sum(1 for r in results if r["outcome"] == "O1_both_R_and_C_pass")
    n_o2 = sum(1 for r in results if r["outcome"] == "O2_splitting_signal_R_stuck_C_ok")
    n_o3 = sum(1 for r in results if r["outcome"] == "O3_both_stuck_numerical_slack")
    n_border = sum(1 for r in results if r["outcome"] == "borderline_inconclusive")
    print(f"  O1 (no splitting signal, R + C both pass): {n_o1} / {len(results)}")
    print(f"  O2 (real-orbit splitting signal):          {n_o2} / {len(results)}")
    print(f"  O3 (both stuck, numerical slack):          {n_o3} / {len(results)}")
    print(f"  borderline / inconclusive:                 {n_border} / {len(results)}")
    print()

    if n_o1 == len(results):
        print("INTERPRETATION: No splitting signal. All pairs connect over R.")
        print("  -> v1-insufficiency claim stands on its own (5-hash finding is orbit-coverage, not numerical slack).")
        print("  -> Whitepaper revision: tighten 'numerical slack ruled out' claim.")
    elif n_o2 > 0:
        print("INTERPRETATION: Real-orbit splitting detected on 2x2 matmul.")
        print("  -> v1 canonicalizer treats distinct real components of the complex orbit as equivalent.")
        print("  -> v2 may or may not — depends on whether inv1, inv2 discriminate real components.")
        print("  -> Whitepaper revision: add real-component limitation to v1 and/or v2 declared_limitations.")
    elif n_o3 > 0:
        print("INTERPRETATION: Seeds are not precisely in the orbit at claimed precision.")
        print("  -> 5-hash finding is partially numerical-slack, not pure v1 insufficiency.")
        print("  -> Whitepaper revision: reframe the pilot's 5-hash evidence.")
    else:
        print("INTERPRETATION: Mixed outcomes across pairs. Inconclusive.")
        print("  -> May need more restarts or alternative objective (v1-canonicalize non-differentiable).")

    # Save
    import json
    out = Path(__file__).parent / "orbit_membership_test_results.json"
    with open(out, "w") as f:
        json.dump({
            "n_pairs": len(results),
            "n_o1": n_o1, "n_o2": n_o2, "n_o3": n_o3, "n_borderline": n_border,
            "per_pair": results,
        }, f, indent=2, default=str)
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
