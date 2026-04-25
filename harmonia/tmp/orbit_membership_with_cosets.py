"""Extended orbit-membership test: include the discrete Aut(T) elements.

Hypothesis: seed_i and seed_j are in the same full Aut(T) orbit but
different GL(2)^3 cosets. Aut(T) for 2x2 matmul includes:
  - Connected: GL(2)^3 matmul-covariant
  - Z/3 cyclic mode-permutation: (A, B, C) -> (B, C, A) and (C, A, B)
  - Z/2 transpose: (A, B, C) -> reshape-transpose of each factor matrix
    (swap rows <-> cols in each 2x2)

Test: for each pair (seed_i, seed_j), try orbit-membership across
6 = 3 x 2 discrete coset representatives of seed_j. If at least ONE
coset version gives low residual via GL(2)^3 optimization, they're in
the same full Aut(T) orbit. This directly verifies that v2 hash
collapses the Aut(T) orbit (not just the connected subgroup).

Ambiguity note: the Z/3 mode-permutation takes "rank-1 term (u,v,w)"
to "rank-1 term (v,w,u)" — both still reconstruct a tensor T' that is
a permutation of T. The matmul tensor T itself satisfies
  T[ij, jk, ik] = T[jk, ik, ij] = T[ik, ij, jk] ... ??
Actually no — T is NOT cyclic-mode-symmetric as a tensor. What IS cyclic
is: if T is matmul, then mode-cyclic-permuted T is ALSO matmul in a
different variable-labeling. For matmul specifically, the tensor has the
symmetry that permuting (i, j, k) axes gives the "same" matmul under
index relabeling. This is the source of the Z/3 symmetry in Aut(T).

So: (A, B, C) -> (B, C, A) should still decompose the SAME T (up to
index relabeling of the tensor). But as decompositions of a FIXED
labeled T, this is a non-trivial symmetry.

For this test I try the 3 cyclic rotations of the decomposition factors
and the transpose (reshape A, B, C -> A^T, B^T, C^T per-term).

If ONE of these 6 coset representatives gives low residual via GL(2)^3
optimization, same orbit. If none do, (inv1, inv2) collapse is
coincidental and v2 hash may have false positives.
"""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import make_matmul_tensor, run_als, residual
from canonicalize_test import canonicalize_v1, known_strassen
from tensor_gl2_action import apply_gl2_action, factor_to_matrices, matrices_to_factor
from orbit_membership_sanity import search


def cyclic_rotate_factors(A, B, C, k):
    """Cyclic rotation k=0: (A, B, C), k=1: (B, C, A), k=2: (C, A, B).
    Each still reconstructs a matmul-like tensor under appropriate mode-
    relabeling.
    """
    if k == 0:
        return A, B, C
    elif k == 1:
        return B, C, A
    elif k == 2:
        return C, A, B


def transpose_factors(A, B, C):
    """Transpose each rank-1 term's 2x2 matrix form.
    For matmul, (U, V, W) transpose symmetry is from AB=C => (AB)^T = B^T A^T,
    so rank-1 term U⊗V⊗W under this symmetry becomes V^T⊗U^T⊗W^T or similar.
    Try the natural: transpose each 2x2 matrix.
    """
    def t(X):
        Ms = factor_to_matrices(X)  # (r, 2, 2)
        Ms_T = np.array([M.T for M in Ms])
        return matrices_to_factor(Ms_T)
    return t(A), t(B), t(C)


def discrete_coset_representatives(A, B, C):
    """Return all 6 = 3 * 2 coset reps: 3 cyclic rotations x 2 transpose states."""
    reps = []
    for k in range(3):
        rotA, rotB, rotC = cyclic_rotate_factors(A, B, C, k)
        reps.append(("cyclic" + str(k), rotA, rotB, rotC))
        tA, tB, tC = transpose_factors(rotA, rotB, rotC)
        reps.append(("cyclic" + str(k) + "_transposed", tA, tB, tC))
    return reps


def main():
    T = make_matmul_tensor(n=2)
    US, VS, WS = known_strassen()

    # Collect seeds
    seeds = []
    for s in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=s)
        if res < 1e-10:
            seeds.append({"seed": s, "A": A, "B": B, "C": C})

    print(f"Collected {len(seeds)} ALS seeds at machine precision.\n")

    # First check: does each coset rep of a seed still (approximately) reconstruct T?
    # This tells us whether cyclic rotations / transpose are actually T-preserving
    # under the FIXED tensor T (as opposed to a relabeled tensor).
    print("Coset-reconstruction check (do 6 coset reps of seed 0 still give T?):")
    s0 = seeds[0]
    reps = discrete_coset_representatives(s0["A"], s0["B"], s0["C"])
    for name, A, B, C in reps:
        res = residual(A, B, C, T)
        print(f"  {name}: residual = {res:.4e}  {'preserves_T' if res < 1e-6 else 'does_NOT_preserve_T'}")
    print()

    # Even if they don't preserve T, a coset-rep that reconstructs a PERMUTED
    # T might connect to Strassen via a permuted-input optimization. For now,
    # focus on finding cosets of seed_j that preserve T and then searching
    # GL(2)^3 optimization.

    print("Strassen coset-reconstructions (do Strassen's cosets give T?):")
    reps_s = discrete_coset_representatives(US, VS, WS)
    for name, A, B, C in reps_s:
        res = residual(A, B, C, T)
        print(f"  {name}: residual = {res:.4e}  {'preserves_T' if res < 1e-6 else 'does_NOT_preserve_T'}")
    print()

    # For pairs, test orbit-membership with coset rotations
    print("=" * 60)
    print("Orbit-membership test with discrete cosets (Strassen -> seed_j)")
    print("=" * 60)
    strassen = (US, VS, WS)
    for s_j in seeds[:2]:  # test first 2 seeds for speed
        sj = (s_j["A"], s_j["B"], s_j["C"])
        label = f"seed{s_j['seed']}"
        print(f"\nStrassen -> {label}:")

        # Try each coset rep of seed_j
        best_overall = np.inf
        best_coset = None
        for name, A_cj, B_cj, C_cj in discrete_coset_representatives(*sj):
            # Only try if it preserves T (otherwise GL(2)^3 optimization is ill-posed)
            res_check = residual(A_cj, B_cj, C_cj, T)
            if res_check > 1e-6:
                # Skip — coset rep not a T-preserving decomp
                continue
            best, _ = search(strassen, (A_cj, B_cj, C_cj), n_restarts=15, seed=s_j["seed"])
            print(f"  coset={name}: residual={best:.4e}  (coset_res={res_check:.2e})")
            if best < best_overall:
                best_overall = best
                best_coset = name

        if best_overall < 1e-4:
            print(f"  -> SAME ORBIT via coset '{best_coset}', residual {best_overall:.4e}")
        else:
            print(f"  -> no coset connects at <1e-4. Best: '{best_coset}' at {best_overall:.4e}")


if __name__ == "__main__":
    main()
