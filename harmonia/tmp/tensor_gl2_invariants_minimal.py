"""
W2 Strategy 3 REFINED — minimal invariant set.

Finding (2026-04-23): the 2x2 matmul tensor's full automorphism group
includes GL(2)^3 AND discrete symmetries (transpose, cyclic permutation
of factor roles). The connected GL(2)^3 subgroup alone is narrower than
the full Aut(T).

Two GL(2)^3-invariants (inv1 = det products per term; inv2 = tr(UVW^T)
per term) happen to ALSO be invariant under the discrete symmetries
(because det is preserved under transpose, and tr(UVW^T) under cyclic
permutation).

The cross-term invariants inv3_{r,s} = tr(U_r V_s W_r^T) are invariant
under GL(2)^3 but NOT under the discrete symmetries (they're not
symmetric in the factor-role swap).

Hypothesis: hash(sorted(inv1) + sorted(inv2)) collapses the full Aut
orbit, not just the GL(2)^3 coset. Test on the 4 ALS seeds + Strassen.

CRITICAL: normalize -0.0 -> 0.0 in the JSON payload so tuple equality
translates to hash equality.
"""

import numpy as np
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import make_matmul_tensor, run_als, residual
from canonicalize_test import canonicalize_v1, known_strassen
from tensor_gl2_action import apply_gl2_action, factor_to_matrices


def minimal_invariants(A, B, C, decimals=4):
    """Minimal provably-Aut(T)-invariant scalars for 2x2 matmul decompositions.

    Returns sorted (inv1, inv2) where:
      inv1_r = det(U_r) * det(V_r) * det(W_r)
      inv2_r = tr(U_r V_r W_r^T)
    Both sorted over rank-1 terms, rounded to `decimals`, -0.0 normalized to 0.0.
    """
    Us = factor_to_matrices(A)
    Vs = factor_to_matrices(B)
    Ws = factor_to_matrices(C)
    r = Us.shape[0]

    inv1 = []
    inv2 = []
    for i in range(r):
        d = float(np.linalg.det(Us[i]) * np.linalg.det(Vs[i]) * np.linalg.det(Ws[i]))
        t = float(np.trace(Us[i] @ Vs[i] @ Ws[i].T))
        # Normalize -0.0 -> 0.0
        if d == 0.0: d = 0.0
        if t == 0.0: t = 0.0
        inv1.append(round(d, decimals))
        inv2.append(round(t, decimals))

    # Normalize -0.0 -> 0.0 post-rounding
    inv1 = [0.0 if x == 0.0 else x for x in inv1]
    inv2 = [0.0 if x == 0.0 else x for x in inv2]

    return tuple(sorted(inv1)), tuple(sorted(inv2))


def minimal_canonical_hash(A, B, C, decimals=4):
    """Hash based only on GL(2)^3 × Aut-discrete-invariant scalars."""
    inv1, inv2 = minimal_invariants(A, B, C, decimals=decimals)
    payload = json.dumps({
        "inv1_det_prod": list(inv1),
        "inv2_trace_uvw": list(inv2),
    }).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def main():
    T = make_matmul_tensor(n=2)
    print("=== W2 Strategy 3 refined — minimal invariants (inv1 + inv2 only) ===\n")

    US, VS, WS = known_strassen()
    h_strassen = minimal_canonical_hash(US, VS, WS)
    i1_s, i2_s = minimal_invariants(US, VS, WS)
    print(f"Strassen hash: {h_strassen}")
    print(f"  inv1: {i1_s}")
    print(f"  inv2: {i2_s}\n")

    # Collect all ALS-converged seeds
    print("Collecting ALS-converged seeds...")
    seeds = []
    for seed in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=seed)
        if res < 1e-10:
            seeds.append({"seed": seed, "A": A, "B": B, "C": C, "residual": res})
    print(f"  {len(seeds)} machine-precision seeds.\n")

    print("Per-seed minimal-invariant hashes:")
    seed_hashes = []
    for s in seeds:
        h = minimal_canonical_hash(s["A"], s["B"], s["C"])
        i1, i2 = minimal_invariants(s["A"], s["B"], s["C"])
        seed_hashes.append(h)
        match = "YES" if h == h_strassen else "NO"
        print(f"  seed {s['seed']}: hash={h}  strassen={match}")
        print(f"    inv1: {i1}")
        print(f"    inv2: {i2}")

    n_match_strassen = sum(1 for h in seed_hashes if h == h_strassen)
    n_pair_same = 0
    n_pairs = 0
    for i in range(len(seed_hashes)):
        for j in range(i + 1, len(seed_hashes)):
            n_pairs += 1
            if seed_hashes[i] == seed_hashes[j]:
                n_pair_same += 1

    print(f"\nPair-agreement: {n_pair_same}/{n_pairs}")
    print(f"Strassen matches: {n_match_strassen}/{len(seed_hashes)}")

    if n_match_strassen == len(seed_hashes) and n_pair_same == n_pairs and len(seed_hashes) > 0:
        print("\n  *** W2 STRATEGY 3 REFINED: PASS ***")
        print("  All orbit elements (ALS seeds + Strassen) collapse to one canonical hash.")
        print("  The minimal (inv1, inv2) pair is Aut(T)-invariant AND orbit-complete on")
        print("  the tested inputs. Ready to register as CANONICALIZER:tensor_decomp_identity@v2.")
    elif n_pair_same > 0 or n_match_strassen > 0:
        print("\n  W2 STRATEGY 3 REFINED: PARTIAL.")
    else:
        print("\n  W2 STRATEGY 3 REFINED: FAIL.")

    # Stress test: apply random GL(2)^3 action to Strassen, check hash stays same
    print("\nStress test — apply 10 random GL(2)^3 actions to Strassen, check hash invariance:")
    rng = np.random.default_rng(0)
    n_stable = 0
    for trial in range(10):
        P = rng.standard_normal((2, 2))
        Q = rng.standard_normal((2, 2))
        R = rng.standard_normal((2, 2))
        while abs(np.linalg.det(P)) < 0.1: P = rng.standard_normal((2, 2))
        while abs(np.linalg.det(Q)) < 0.1: Q = rng.standard_normal((2, 2))
        while abs(np.linalg.det(R)) < 0.1: R = rng.standard_normal((2, 2))
        A_new, B_new, C_new = apply_gl2_action(US, VS, WS, P, Q, R)
        h_new = minimal_canonical_hash(A_new, B_new, C_new)
        if h_new == h_strassen:
            n_stable += 1
        else:
            print(f"  Trial {trial} HASH DRIFT: {h_new} (expected {h_strassen})")
    print(f"  {n_stable}/10 random GL actions preserve Strassen hash.")

    # Stress test 2: different-rank inputs should NOT hash same as Strassen
    print("\nStress test — rank-8 (naive) decomposition should NOT match rank-7 Strassen:")
    A8, B8, C8, _, _ = run_als(T, rank=8, max_iters=500, seed=0)
    h8 = minimal_canonical_hash(A8, B8, C8)
    print(f"  rank-8 hash: {h8}")
    print(f"  Differs from Strassen: {h8 != h_strassen}")

    # Save
    out = Path(__file__).parent / "tensor_gl2_invariants_minimal_results.json"
    dump = {
        "strassen_hash": h_strassen,
        "strassen_inv1": list(i1_s),
        "strassen_inv2": list(i2_s),
        "n_seeds": len(seeds),
        "seed_hashes": seed_hashes,
        "pair_same": n_pair_same,
        "n_pairs": n_pairs,
        "strassen_matches": n_match_strassen,
        "verdict": (
            "PASS" if (n_match_strassen == len(seed_hashes) and n_pair_same == n_pairs and len(seed_hashes) > 0)
            else "PARTIAL" if (n_pair_same > 0 or n_match_strassen > 0)
            else "FAIL"
        ),
        "gl_stress_test_stable": n_stable,
        "rank8_different": h8 != h_strassen,
    }
    with open(out, "w") as f:
        json.dump(dump, f, indent=2)
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
