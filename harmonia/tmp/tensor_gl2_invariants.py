"""
W2 Strategy 3 — Type A canonical hash via provably-GL(2)^3-invariant
quantities.

Derivation: the matmul-covariant action is
  U_r -> P U_r Q^{-1}
  V_r -> Q V_r R^{-1}
  W_r -> P^{-T} W_r R^T

For a single rank-1 term r, two GL(2)^3-invariant scalars:

  INV1_r = det(U_r) * det(V_r) * det(W_r)
    det(P U Q^{-1}) = det(P)/det(Q) * det(U)
    det(Q V R^{-1}) = det(Q)/det(R) * det(V)
    det(P^{-T} W R^T) = det(P)^{-1} * det(R) * det(W)
    Product: [det(P)/det(Q)] * [det(Q)/det(R)] * [det(R)/det(P)] * det(U)det(V)det(W)
          = 1 * det(U)det(V)det(W). INVARIANT.

  INV2_r = trace(U_r V_r W_r^T)
    Under the action: trace((P U Q^{-1})(Q V R^{-1})(P^{-T} W R^T)^T)
    = trace((P U Q^{-1})(Q V R^{-1})(R W^T P^{-1}))
    = trace(P U V W^T P^{-1})  (the Q's cancel, the R's cancel)
    = trace(U V W^T).  INVARIANT.

Cross-term invariants (mixing rank-1 terms r and s):
  INV3_{r,s} = trace(U_r V_s W_r^T) — under action: trace(P U_r V_s W_r^T P^{-1})
    = trace(U_r V_s W_r^T). INVARIANT (but Q_s terms go inside V_s and cancel
    with the Q from U_r's Q^{-1})
  Wait: trace((P U_r Q^{-1})(Q V_s R^{-1})(R W_r^T P^{-1}))
      = trace(P U_r V_s R^{-1} R W_r^T P^{-1})
      = trace(P U_r V_s W_r^T P^{-1})
      = trace(U_r V_s W_r^T). INVARIANT.

So we have two classes of per-term invariants (INV1, INV2) and one class of
mixed invariants (INV3). Computing a SORTED list of these over r
(and over pairs r,s for INV3) should form a basis-invariant fingerprint.

Hypothesis: if all ALS-converged seeds are in the same orbit, they should
have the same sorted invariant list as Strassen.
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


def per_term_invariants(A, B, C, decimals=4):
    """Compute INV1_r and INV2_r for each rank-1 term. Return sorted tuple."""
    Us = factor_to_matrices(A)
    Vs = factor_to_matrices(B)
    Ws = factor_to_matrices(C)
    r = Us.shape[0]

    inv1 = []  # det products
    inv2 = []  # tr(UVW^T)
    for i in range(r):
        U, V, W = Us[i], Vs[i], Ws[i]
        d = np.linalg.det(U) * np.linalg.det(V) * np.linalg.det(W)
        t = np.trace(U @ V @ W.T)
        inv1.append(d)
        inv2.append(t)

    inv1_sorted = tuple(np.round(sorted(inv1), decimals))
    inv2_sorted = tuple(np.round(sorted(inv2), decimals))
    return inv1_sorted, inv2_sorted


def cross_term_invariants(A, B, C, decimals=4, max_terms=None):
    """Compute INV3_{r,s} = tr(U_r V_s W_r^T) for all (r, s). Return sorted
    flat list.

    This is O(r^2). For r=7 we get 49 invariants.
    """
    Us = factor_to_matrices(A)
    Vs = factor_to_matrices(B)
    Ws = factor_to_matrices(C)
    r = Us.shape[0]
    if max_terms is not None:
        r = min(r, max_terms)

    inv3 = []
    for i in range(r):
        for j in range(r):
            t = np.trace(Us[i] @ Vs[j] @ Ws[i].T)
            inv3.append(t)

    # Sort for permutation-invariance
    # Note: a permutation of rank-1 terms relabels r -> perm(r). This affects
    # the cross-term matrix as INV3'[i, j] = INV3[perm(i), perm(j)]. The
    # MATRIX is conjugated by the permutation matrix. To get a permutation-
    # invariant fingerprint, we need a matrix invariant like eigenvalues,
    # or a sorted multi-set of entries.
    # For now: sorted flat list (loses structure, but permutation-invariant).
    inv3_sorted = tuple(np.round(sorted(inv3), decimals))
    return inv3_sorted


def canonical_hash_v2_invariants(A, B, C, decimals=4):
    """Type A canonical hash using provably GL(2)^3-invariant quantities."""
    i1, i2 = per_term_invariants(A, B, C, decimals=decimals)
    i3 = cross_term_invariants(A, B, C, decimals=decimals)
    payload = json.dumps({
        "inv1_det_prod": list(i1),
        "inv2_trace_uvw": list(i2),
        "inv3_cross_trace": list(i3),
    }, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def verify_invariance_under_random_gl(A, B, C, T, n_trials=5):
    """Sanity check: applying random (P,Q,R) should not change the invariants."""
    rng = np.random.default_rng(42)
    i1_orig, i2_orig = per_term_invariants(A, B, C)
    i3_orig = cross_term_invariants(A, B, C)
    print(f"  Original inv1 (det products): {i1_orig}")
    print(f"  Original inv2 (tr UVW^T):     {i2_orig}")
    print(f"  Original inv3 (cross traces, first 5): {i3_orig[:5]}...")

    all_pass = True
    for trial in range(n_trials):
        P = rng.standard_normal((2, 2))
        Q = rng.standard_normal((2, 2))
        R = rng.standard_normal((2, 2))
        while abs(np.linalg.det(P)) < 0.1: P = rng.standard_normal((2, 2))
        while abs(np.linalg.det(Q)) < 0.1: Q = rng.standard_normal((2, 2))
        while abs(np.linalg.det(R)) < 0.1: R = rng.standard_normal((2, 2))

        A_new, B_new, C_new = apply_gl2_action(A, B, C, P, Q, R)
        res = residual(A_new, B_new, C_new, T)
        if res > 1e-8:
            print(f"  Trial {trial} WARNING: action did not preserve T (res={res:.2e})")

        i1_new, i2_new = per_term_invariants(A_new, B_new, C_new)
        i3_new = cross_term_invariants(A_new, B_new, C_new)

        pass_1 = i1_orig == i1_new
        pass_2 = i2_orig == i2_new
        pass_3 = i3_orig == i3_new

        all_pass = all_pass and pass_1 and pass_2 and pass_3
        status = "OK" if (pass_1 and pass_2 and pass_3) else "MISMATCH"
        print(f"  Trial {trial} (det P={np.linalg.det(P):.2f}): inv1={pass_1}  inv2={pass_2}  inv3={pass_3}  {status}")
        if not (pass_1 and pass_2 and pass_3):
            print(f"    new inv1: {i1_new}")
            print(f"    new inv2: {i2_new}")
    return all_pass


def main():
    T = make_matmul_tensor(n=2)
    print("=== W2 Strategy 3 — GL(2)^3 polynomial invariants ===\n")

    # Phase 0: verify invariants are actually invariant
    print("Phase 0: verifying invariants on Strassen under random GL(2)^3 action...")
    US, VS, WS = known_strassen()
    invariance_ok = verify_invariance_under_random_gl(US, VS, WS, T)
    print(f"  invariance_ok: {invariance_ok}\n")

    # Phase 1: compute Strassen's v2 invariant-based hash
    h_strassen = canonical_hash_v2_invariants(US, VS, WS)
    print(f"Strassen invariant-hash: {h_strassen}\n")

    # Phase 2: compute hashes for ALS-converged seeds
    print("Collecting ALS-converged seeds at rank 7...")
    seeds = []
    for seed in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=seed)
        if res < 1e-10:
            seeds.append({"seed": seed, "A": A, "B": B, "C": C, "residual": res})
    print(f"  {len(seeds)} machine-precision seeds.\n")

    print("Per-seed invariant-hashes:")
    seed_hashes = []
    for s in seeds:
        h = canonical_hash_v2_invariants(s["A"], s["B"], s["C"])
        seed_hashes.append(h)
        match = "YES" if h == h_strassen else "NO"
        i1, i2 = per_term_invariants(s["A"], s["B"], s["C"])
        print(f"  seed {s['seed']}: hash={h}  matches_strassen={match}")
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

    print(f"\nPair-agreement: {n_pair_same}/{n_pairs}. Strassen matches: {n_match_strassen}/{len(seed_hashes)}.")

    if n_match_strassen == len(seed_hashes) and n_pair_same == n_pairs:
        print("\nW2 STRATEGY 3: PASS. All orbit elements collapse to same canonical hash under GL(2)^3 invariants.")
    elif n_pair_same > 0 or n_match_strassen > 0:
        print("\nW2 STRATEGY 3: PARTIAL. Some collapse; invariants insufficient.")
    else:
        print("\nW2 STRATEGY 3: FAIL. Invariants differ across orbit elements.")
        print("  Diagnosis: the chosen invariants are not complete for discriminating orbits,")
        print("  OR the ALS seeds are NOT actually in the same orbit as Strassen (would")
        print("  contradict the theoretical claim).")

    # Phase 3: compare Strassen vs seed 0 invariant-by-invariant
    print("\nDiagnostic — Strassen vs ALS seed invariant comparison:")
    i1_s, i2_s = per_term_invariants(US, VS, WS)
    i3_s = cross_term_invariants(US, VS, WS)
    if seeds:
        s0 = seeds[0]
        i1_0, i2_0 = per_term_invariants(s0["A"], s0["B"], s0["C"])
        i3_0 = cross_term_invariants(s0["A"], s0["B"], s0["C"])
        print(f"  inv1 (det products):")
        print(f"    Strassen: {i1_s}")
        print(f"    seed {s0['seed']}:  {i1_0}")
        print(f"    same: {i1_s == i1_0}")
        print(f"  inv2 (tr UVW^T):")
        print(f"    Strassen: {i2_s}")
        print(f"    seed {s0['seed']}:  {i2_0}")
        print(f"    same: {i2_s == i2_0}")
        print(f"  inv3 (cross traces) sum/min/max:")
        print(f"    Strassen: sum={sum(i3_s):.4f}  min={min(i3_s):.4f}  max={max(i3_s):.4f}")
        print(f"    seed {s0['seed']}:  sum={sum(i3_0):.4f}  min={min(i3_0):.4f}  max={max(i3_0):.4f}")
        print(f"    same: {i3_s == i3_0}")

    # Save
    out = Path(__file__).parent / "tensor_gl2_invariants_results.json"
    dump = {
        "strassen_hash": h_strassen,
        "seed_hashes": seed_hashes,
        "pair_same": n_pair_same,
        "n_pairs": n_pairs,
        "strassen_matches": n_match_strassen,
        "verdict": (
            "PASS" if (n_match_strassen == len(seed_hashes) and n_pair_same == n_pairs)
            else "PARTIAL" if (n_pair_same > 0 or n_match_strassen > 0)
            else "FAIL"
        ),
        "invariance_verified": invariance_ok,
    }
    with open(out, "w") as f:
        json.dump(dump, f, indent=2, default=str)
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
