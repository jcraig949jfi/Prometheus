"""Differential-evolution global search for orbit-membership.

Replaces L-BFGS-B with scipy.optimize.differential_evolution to test
interpretation (1): does the GL(2)^3 connection between Strassen and
ALS-converged seeds exist but lie far from identity, requiring global
optimization to find?

If DE finds residual ~0 on at least one pair: interpretation (1) confirmed,
near-identity init was the bottleneck, v1-insufficiency claim stands.

If DE also fails: interpretations (2) [multiple real orbits] or (3)
[(inv1, inv2) not orbit-complete] become the live hypotheses.

DE does not require differentiability of the objective, so the
v1-canonicalize discrete steps are not a problem here.
"""

import numpy as np
import sys
from pathlib import Path
from scipy.optimize import differential_evolution
import json
import time

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import make_matmul_tensor, run_als, residual
from canonicalize_test import canonicalize_v1, known_strassen
from tensor_gl2_action import apply_gl2_action
from orbit_membership_sanity import hungarian_match_cost


def objective(x, seed_i_ABC, seed_j_ABC):
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


def de_search(seed_i_ABC, seed_j_ABC, popsize=15, maxiter=200, seed=0,
              bounds_scale=3.0):
    """Differential evolution over GL(2)^3."""
    bounds = [(-bounds_scale, bounds_scale)] * 12
    t0 = time.time()
    result = differential_evolution(
        objective, bounds,
        args=(seed_i_ABC, seed_j_ABC),
        popsize=popsize, maxiter=maxiter,
        seed=seed, tol=1e-10, mutation=(0.5, 1.5), recombination=0.9,
        polish=True, init="sobol",
        workers=1,  # avoid Windows multiprocess overhead
    )
    return result.fun, result.x, time.time() - t0


def main():
    T = make_matmul_tensor(n=2)
    print("=== Orbit-membership via differential evolution ===\n")

    US, VS, WS = known_strassen()
    strassen = (US, VS, WS)

    # Sanity: known nearby action with DE
    print("Sanity: DE on Strassen -> apply_gl2(Strassen, small (P,Q,R))")
    rng = np.random.default_rng(7)
    P0 = np.eye(2) + rng.standard_normal((2, 2)) * 0.4
    Q0 = np.eye(2) + rng.standard_normal((2, 2)) * 0.4
    R0 = np.eye(2) + rng.standard_normal((2, 2)) * 0.4
    A1, B1, C1 = apply_gl2_action(US, VS, WS, P0, Q0, R0)
    res, x, dt = de_search(strassen, (A1, B1, C1), popsize=15, maxiter=100, seed=42)
    print(f"  best={res:.4e}  ({dt:.1f}s)  {'PASS' if res < 1e-6 else 'FAIL'}\n")

    # Collect ALS seeds
    seeds = []
    for s in range(20):
        A, B, C, ralz, _ = run_als(T, rank=7, max_iters=500, seed=s)
        if ralz < 1e-10:
            seeds.append({"seed": s, "A": A, "B": B, "C": C, "residual": ralz})

    # Run DE on Strassen vs each seed, and seed[0] vs seed[1..3]
    print("DE: Strassen -> ALS seed (4 seeds)")
    pairs_to_test = [
        ("Strassen", "seed" + str(seeds[i]["seed"]), strassen, (seeds[i]["A"], seeds[i]["B"], seeds[i]["C"]))
        for i in range(len(seeds))
    ]
    # Add a couple seed-pair tests
    pairs_to_test.append((
        "seed" + str(seeds[0]["seed"]), "seed" + str(seeds[1]["seed"]),
        (seeds[0]["A"], seeds[0]["B"], seeds[0]["C"]),
        (seeds[1]["A"], seeds[1]["B"], seeds[1]["C"]),
    ))

    results = []
    for label_i, label_j, si, sj in pairs_to_test:
        print(f"\n  {label_i} -> {label_j}:")
        # Use larger budget for these (likely far-from-identity solutions)
        res, x, dt = de_search(si, sj, popsize=20, maxiter=300, seed=0, bounds_scale=5.0)
        status = "PASS" if res < 1e-4 else ("CLOSE" if res < 1e-2 else "FAIL")
        print(f"    DE best: {res:.4e}  ({dt:.1f}s)  [{status}]")
        # If close-but-not-tight, try with wider bounds + more iters
        if 1e-4 <= res < 1e-1:
            print(f"    Borderline; retrying with wider bounds...")
            res2, _, dt2 = de_search(si, sj, popsize=30, maxiter=500, seed=999, bounds_scale=10.0)
            print(f"    Retry best: {res2:.4e}  ({dt2:.1f}s)")
            res = min(res, res2)
        results.append({
            "pair": f"{label_i} -> {label_j}",
            "de_residual": float(res),
            "status": status,
        })

    # Aggregate
    print("\n" + "=" * 60)
    print("AGGREGATE VERDICT")
    print("=" * 60)
    n_pass = sum(1 for r in results if r["de_residual"] < 1e-4)
    n_close = sum(1 for r in results if 1e-4 <= r["de_residual"] < 1e-2)
    n_fail = sum(1 for r in results if r["de_residual"] >= 1e-2)
    print(f"  PASS  (residual < 1e-4): {n_pass} / {len(results)}")
    print(f"  CLOSE (1e-4 to 1e-2):    {n_close} / {len(results)}")
    print(f"  FAIL  (>= 1e-2):         {n_fail} / {len(results)}")

    if n_pass == len(results):
        print("\n  Interpretation (1) CONFIRMED: GL(2)^3 connections exist but lie far from identity.")
        print("  Near-identity L-BFGS-B was the bottleneck. v1-insufficiency claim stands.")
    elif n_pass > 0:
        print("\n  PARTIAL: some pairs connect via DE, others don't. Mixed signal.")
        print("  Possibly: real orbits SPLIT into components, with some pairs in same component, others not.")
    else:
        print("\n  Interpretation (1) NOT confirmed: even DE doesn't find connections.")
        print("  Live hypotheses: (2) multiple disconnected real orbits, OR")
        print("                   (3) (inv1, inv2) not orbit-complete (false-positive collapse).")

    # Save
    out = Path(__file__).parent / "orbit_membership_de_results.json"
    with open(out, "w") as f:
        json.dump({
            "results": results,
            "n_pass": n_pass, "n_close": n_close, "n_fail": n_fail,
        }, f, indent=2)
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
