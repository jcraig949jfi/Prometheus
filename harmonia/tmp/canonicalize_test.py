"""
Empirical test of the orbit vs representative question.

From the 2x2 matmul pilot: 3 seeds converged at rank 7 to machine
precision (residual < 1e-12). Per theory (Strassen equivalence class
for 2x2 matmul is unique under GL(2)^3 action), all three are in the
same orbit. But under Steps 1+2 canonicalization (scale gauge +
permutation), do their canonical hashes agree?

If YES → the scaling-gauge + permutation quotient is enough for this case.
If NO  → Step 3 (basis alignment) is the load-bearing piece.

This is the falsification-first check on the "canonicalize first" claim.
"""

import numpy as np
import hashlib
from tensor_pilot_2x2_matmul import (
    make_matmul_tensor, run_als, reconstruct, residual
)


def canonicalize_v1(A, B, C, sign_tol=1e-8):
    """Steps 1 + 2 only: scale gauge + sign + permutation.
    Step 3 (basis alignment) deliberately omitted to test whether 1+2
    suffice.
    """
    A, B, C = A.copy(), B.copy(), C.copy()
    r = A.shape[1]

    # Step 1: normalize columns of A and B; push magnitude into C
    for i in range(r):
        a_n = np.linalg.norm(A[:, i])
        b_n = np.linalg.norm(B[:, i])
        if a_n > 1e-12 and b_n > 1e-12:
            A[:, i] /= a_n
            B[:, i] /= b_n
            C[:, i] *= a_n * b_n

    # Step 1b: sign gauge — make first entry-above-tol of A_i and B_i positive.
    # Flip sign of the partner factor to absorb.
    for i in range(r):
        # A sign
        mask = np.abs(A[:, i]) > sign_tol
        if mask.any():
            idx = np.argmax(mask)
            if A[idx, i] < 0:
                A[:, i] *= -1
                C[:, i] *= -1
        # B sign
        mask = np.abs(B[:, i]) > sign_tol
        if mask.any():
            idx = np.argmax(mask)
            if B[idx, i] < 0:
                B[:, i] *= -1
                C[:, i] *= -1

    # Step 2: permutation — lex sort by rounded concatenated triples
    keys = []
    for i in range(r):
        key = tuple(np.round(
            np.concatenate([A[:, i], B[:, i], C[:, i]]),
            decimals=4
        ))
        keys.append(key)
    order = sorted(range(r), key=lambda i: keys[i])
    A = A[:, order]
    B = B[:, order]
    C = C[:, order]

    return A, B, C


def canonical_hash(A, B, C, decimals=4):
    """Hash the canonicalized (A, B, C) by rounding to fixed decimals."""
    A, B, C = canonicalize_v1(A, B, C)
    flat = np.concatenate([A.flatten(), B.flatten(), C.flatten()])
    rounded = np.round(flat, decimals=decimals)
    return hashlib.sha256(rounded.tobytes()).hexdigest()[:16]


def get_converged_triples(T, n_seeds=20, rank=7, tol=1e-10):
    """Re-run ALS and keep only the seeds that reached machine precision."""
    results = []
    for seed in range(n_seeds):
        A, B, C, res, iters = run_als(T, rank=rank, max_iters=500, seed=seed)
        if res < tol:
            results.append({
                "seed": seed,
                "residual": res,
                "iters": iters,
                "A": A,
                "B": B,
                "C": C,
            })
    return results


def hash_distance(h1, h2):
    return "same" if h1 == h2 else "different"


def known_strassen():
    """Construct Strassen's decomposition of 2x2 matmul in the standard basis.

    Strassen computes 7 products M_1..M_7 of linear combinations of
    entries of A and B, then combines them for C. Encoded as three
    4x7 factor matrices where columns are the u, v, w for each product.
    """
    # a[i,j] flattened as row i*2 + j -> indices 0..3
    # A matrix (for u_i): coefficient of a[0,0], a[0,1], a[1,0], a[1,1]
    # B matrix (for v_i): coefficient of b[0,0], b[0,1], b[1,0], b[1,1]
    # C matrix (for w_i): coefficient of c[0,0], c[0,1], c[1,0], c[1,1]
    #
    # M_1 = (a00 + a11)(b00 + b11) -> contrib to c00 and c11
    # M_2 = (a10 + a11) b00         -> c10 += M_2, c11 -= M_2
    # M_3 = a00 (b01 - b11)         -> c01 += M_3, c11 += M_3
    # M_4 = a11 (b10 - b00)         -> c00 += M_4, c10 += M_4
    # M_5 = (a00 + a01) b11         -> c00 -= M_5, c01 += M_5
    # M_6 = (a10 - a00)(b00 + b01)  -> c11 += M_6
    # M_7 = (a01 - a11)(b10 + b11)  -> c00 += M_7
    #
    # c00 = M_1 + M_4 - M_5 + M_7
    # c01 = M_3 + M_5
    # c10 = M_2 + M_4
    # c11 = M_1 - M_2 + M_3 + M_6

    U = np.array([
        # M_1  M_2  M_3  M_4  M_5  M_6  M_7
        [ 1,   0,   1,   0,   1,  -1,   0],  # a00
        [ 0,   0,   0,   0,   1,   0,   1],  # a01
        [ 0,   1,   0,   0,   0,   1,   0],  # a10
        [ 1,   1,   0,   1,   0,   0,  -1],  # a11
    ], dtype=float)
    V = np.array([
        [ 1,   1,   0,  -1,   0,   1,   0],  # b00
        [ 0,   0,   1,   0,   0,   1,   0],  # b01
        [ 0,   0,   0,   1,   0,   0,   1],  # b10
        [ 1,   0,  -1,   0,   1,   0,   1],  # b11
    ], dtype=float)
    W = np.array([
        [ 1,   0,   0,   1,  -1,   0,   1],  # c00
        [ 0,   0,   1,   0,   1,   0,   0],  # c01
        [ 0,   1,   0,   1,   0,   0,   0],  # c10
        [ 1,  -1,   1,   0,   0,   1,   0],  # c11
    ], dtype=float)
    return U, V, W


def main():
    T = make_matmul_tensor(n=2)
    print(f"Tensor T: shape={T.shape}, ||T||_F={np.linalg.norm(T):.4f}")

    # Verify Strassen's decomposition reconstructs T exactly
    US, VS, WS = known_strassen()
    res_strassen = residual(US, VS, WS, T)
    print(f"\nStrassen decomposition residual: {res_strassen:.2e}")
    assert res_strassen < 1e-10, "Strassen decomposition failed to reconstruct T"
    print("  Strassen verified.")
    h_strassen = canonical_hash(US, VS, WS)
    int_frac_strassen = np.mean(
        np.abs(np.concatenate([US.flatten(), VS.flatten(), WS.flatten()])
               - np.round(np.concatenate([US.flatten(), VS.flatten(), WS.flatten()]))) < 0.01
    )
    print(f"  Strassen canonical_hash (v1): {h_strassen}")
    print(f"  Strassen integer_fraction:    {int_frac_strassen:.3f}")

    # Run ALS and collect converged seeds at rank 7
    print(f"\nCollecting ALS-converged rank-7 seeds (residual < 1e-10)...")
    triples = get_converged_triples(T, n_seeds=20, rank=7, tol=1e-10)
    print(f"  Found {len(triples)} converged seeds.")

    print("\nPer-converged-seed canonical hashes (v1 = scale + sign + permutation):")
    hashes = []
    for t in triples:
        h = canonical_hash(t["A"], t["B"], t["C"])
        int_frac = np.mean(
            np.abs(np.concatenate([t["A"].flatten(), t["B"].flatten(), t["C"].flatten()])
                   - np.round(np.concatenate([t["A"].flatten(), t["B"].flatten(), t["C"].flatten()]))) < 0.01
        )
        hashes.append(h)
        print(f"  seed={t['seed']}  res={t['residual']:.2e}  hash={h}  int_frac={int_frac:.3f}")

    # Pairwise hash agreement
    print("\nPairwise hash comparison (same orbit by theory; same hash iff v1 suffices):")
    n_same = 0
    n_pairs = 0
    for i in range(len(hashes)):
        for j in range(i + 1, len(hashes)):
            n_pairs += 1
            if hashes[i] == hashes[j]:
                n_same += 1
    if n_pairs > 0:
        print(f"  {n_same}/{n_pairs} pairs hash-equivalent under v1 canonicalizer")

    # Compare against Strassen's canonical hash
    print("\nAny ALS-converged seed hash matches Strassen's canonical hash?")
    matches = sum(1 for h in hashes if h == h_strassen)
    print(f"  {matches}/{len(hashes)} match Strassen.")
    if matches == 0:
        print("  (expected under theory: steps 1+2 alone do NOT quotient out the GL^3 basis;")
        print("   ALS lands on random-basis orbit elements; Strassen is one specific element.)")

    # Report representative integer fractions
    print("\nInteger-fraction summary:")
    print(f"  Strassen:              {int_frac_strassen:.3f}")
    if triples:
        als_ifs = [
            np.mean(
                np.abs(np.concatenate([t["A"].flatten(), t["B"].flatten(), t["C"].flatten()])
                       - np.round(np.concatenate([t["A"].flatten(), t["B"].flatten(), t["C"].flatten()]))) < 0.01
            )
            for t in triples
        ]
        print(f"  ALS converged mean:    {np.mean(als_ifs):.3f}")
        print(f"  ALS converged max:     {np.max(als_ifs):.3f}")

    print("\n=== VERDICT ON CANONICALIZER v1 ===")
    if n_pairs > 0 and n_same == n_pairs:
        print("  All converged seeds hash to same canonical rep under v1.")
        print("  -> Scale + permutation quotient suffices for 2x2 matmul.")
        print("  -> But NONE match Strassen integer rep; v1 collapses the orbit to SOME rep, not the Strassen one.")
    elif n_pairs > 0:
        print("  Converged seeds hash to DIFFERENT canonical reps under v1.")
        print("  -> Scale + permutation alone does NOT quotient out the full orbit.")
        print("  -> Step 3 (basis alignment) is the load-bearing piece for canonicalization.")
        print("  -> This is the empirical evidence for the orbit-vs-representative architecture note.")
    else:
        print("  No converged seeds to compare. Rerun pilot with larger budget.")


if __name__ == "__main__":
    main()
