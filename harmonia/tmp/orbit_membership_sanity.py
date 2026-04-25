"""Sanity check: can the orbit-membership optimizer recover a known GL(2)^3
action?

Take Strassen. Apply a known random (P0, Q0, R0). Call result S'. Then try
to recover some (P, Q, R) carrying Strassen to S'.

If yes, optimization is working and the failed 6-pair test (O3 outcome)
says the ALS seeds are not precisely in Strassen's orbit.
If no, the optimization is broken (non-differentiable v1 canonicalize) and
the 6-pair test result is not interpretable.
"""

import numpy as np
import sys
from pathlib import Path
from scipy.optimize import minimize, basinhopping

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import make_matmul_tensor, residual
from canonicalize_test import canonicalize_v1, known_strassen
from tensor_gl2_action import apply_gl2_action


def v1_flatten(A, B, C):
    A_c, B_c, C_c = canonicalize_v1(A, B, C)
    return np.concatenate([A_c.flatten(), B_c.flatten(), C_c.flatten()])


def hungarian_match_cost(A_t, B_t, C_t, A_ref, B_ref, C_ref):
    """Column-wise L2 after unit-norming A and B columns + sign gauge."""
    from scipy.optimize import linear_sum_assignment

    def gauge_normalize(A, B, C):
        A = A.copy(); B = B.copy(); C = C.copy()
        r = A.shape[1]
        for i in range(r):
            a_n = np.linalg.norm(A[:, i])
            b_n = np.linalg.norm(B[:, i])
            if a_n > 1e-12 and b_n > 1e-12:
                A[:, i] /= a_n; B[:, i] /= b_n; C[:, i] *= a_n * b_n
            # Sign gauge on A
            idx = np.argmax(np.abs(A[:, i]) > 1e-8)
            if A[idx, i] < 0:
                A[:, i] *= -1; C[:, i] *= -1
        return A, B, C

    A_t, B_t, C_t = gauge_normalize(A_t, B_t, C_t)
    A_ref, B_ref, C_ref = gauge_normalize(A_ref.copy(), B_ref.copy(), C_ref.copy())

    r = A_t.shape[1]
    cost = np.zeros((r, r))
    for i in range(r):
        for j in range(r):
            diff_A = A_t[:, i] - A_ref[:, j]
            diff_B = B_t[:, i] - B_ref[:, j]
            diff_C = C_t[:, i] - C_ref[:, j]
            cost[i, j] = np.linalg.norm(diff_A) ** 2 + np.linalg.norm(diff_B) ** 2 + np.linalg.norm(diff_C) ** 2

    row_ind, col_ind = linear_sum_assignment(cost)
    return np.sqrt(sum(cost[i, j] for i, j in zip(row_ind, col_ind)))


def objective_hungarian(x, seed_i_ABC, seed_j_ABC):
    P = x[0:4].reshape(2, 2)
    Q = x[4:8].reshape(2, 2)
    R = x[8:12].reshape(2, 2)
    if abs(np.linalg.det(P)) < 0.01: return 1e6
    if abs(np.linalg.det(Q)) < 0.01: return 1e6
    if abs(np.linalg.det(R)) < 0.01: return 1e6
    try:
        A_t, B_t, C_t = apply_gl2_action(*seed_i_ABC, P, Q, R)
        return hungarian_match_cost(A_t, B_t, C_t, *seed_j_ABC)
    except np.linalg.LinAlgError:
        return 1e6


def search(seed_i_ABC, seed_j_ABC, n_restarts=30, seed=0, verbose=False):
    rng = np.random.default_rng(seed)
    best = np.inf
    # Try identity first, then random
    trials = []
    for r in range(n_restarts):
        if r == 0:
            x0 = np.array([1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], dtype=float)
        else:
            x0 = np.array([1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], dtype=float)
            x0 = x0 + rng.standard_normal(12) * 0.8
        try:
            result = minimize(
                objective_hungarian, x0,
                args=(seed_i_ABC, seed_j_ABC),
                method="L-BFGS-B",
                options={"maxiter": 500, "ftol": 1e-14, "gtol": 1e-10},
            )
            trials.append(result.fun)
            if result.fun < best:
                best = result.fun
                if verbose: print(f"  r={r}: {result.fun:.4e}")
        except Exception:
            continue
    if verbose: print(f"  best of {n_restarts}: {best:.4e}")
    return best, trials


def main():
    T = make_matmul_tensor(n=2)
    US, VS, WS = known_strassen()
    strassen = (US, VS, WS)

    # Check 1: same input on both sides
    print("Sanity 1: optimization against self (should reach 0)")
    best, _ = search(strassen, strassen, n_restarts=5)
    print(f"  Strassen -> Strassen best: {best:.4e}")
    print(f"  {'PASS' if best < 1e-6 else 'FAIL'}\n")

    # Check 2: known GL(2)^3 action
    print("Sanity 2: recover known (P0, Q0, R0) action")
    rng = np.random.default_rng(123)
    for trial_seed in range(3):
        rng2 = np.random.default_rng(trial_seed * 17 + 1)
        P0 = np.eye(2) + rng2.standard_normal((2, 2)) * 0.3
        Q0 = np.eye(2) + rng2.standard_normal((2, 2)) * 0.3
        R0 = np.eye(2) + rng2.standard_normal((2, 2)) * 0.3
        while abs(np.linalg.det(P0)) < 0.1: P0 = np.eye(2) + rng2.standard_normal((2, 2)) * 0.3
        while abs(np.linalg.det(Q0)) < 0.1: Q0 = np.eye(2) + rng2.standard_normal((2, 2)) * 0.3
        while abs(np.linalg.det(R0)) < 0.1: R0 = np.eye(2) + rng2.standard_normal((2, 2)) * 0.3

        A1, B1, C1 = apply_gl2_action(US, VS, WS, P0, Q0, R0)
        res_check = residual(A1, B1, C1, T)
        print(f"  Trial {trial_seed}: action-applied residual = {res_check:.2e} (should be 0)")
        assert res_check < 1e-10, "Action didn't preserve T!"

        # Now optimize: can we recover?
        best, _ = search(strassen, (A1, B1, C1), n_restarts=30, seed=trial_seed)
        status = "PASS" if best < 1e-6 else ("CLOSE" if best < 1e-2 else "FAIL")
        print(f"  Strassen -> acted: best residual = {best:.4e}  [{status}]")
    print()

    # Check 3: seed-to-seed on the 4 machine-precision ALS seeds + Strassen
    print("Sanity 3: ALS seeds to Strassen and to each other (subset)")
    from tensor_pilot_2x2_matmul import run_als

    seeds = []
    for s in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=s)
        if res < 1e-10:
            seeds.append({"seed": s, "A": A, "B": B, "C": C})
        if len(seeds) >= 4:
            break

    for s in seeds[:2]:  # only test first 2 for speed
        label = f"seed{s['seed']}"
        # Strassen -> seed
        best, _ = search(strassen, (s["A"], s["B"], s["C"]), n_restarts=30, seed=s["seed"])
        print(f"  Strassen -> {label}: {best:.4e}  {'PASS' if best < 1e-4 else 'FAIL'}")
        # seed -> Strassen
        best2, _ = search((s["A"], s["B"], s["C"]), strassen, n_restarts=30, seed=s["seed"] + 100)
        print(f"  {label} -> Strassen: {best2:.4e}  {'PASS' if best2 < 1e-4 else 'FAIL'}")

    # Also seed 8 vs seed 13 (both at machine precision)
    if len(seeds) >= 2:
        best, _ = search((seeds[0]["A"], seeds[0]["B"], seeds[0]["C"]),
                        (seeds[1]["A"], seeds[1]["B"], seeds[1]["C"]),
                        n_restarts=30, seed=999)
        print(f"  seed{seeds[0]['seed']} -> seed{seeds[1]['seed']}: {best:.4e}  {'PASS' if best < 1e-4 else 'FAIL'}")


if __name__ == "__main__":
    main()
