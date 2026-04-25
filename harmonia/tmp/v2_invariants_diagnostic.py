"""Diagnostic: are v2's (inv1, inv2) invariants class-functions of T and r,
or do they actually discriminate within rank-r decompositions of fixed T?

Tests:
  T1: same tensor T, different rank-7 decompositions (4 ALS seeds + Strassen)
      -> Already verified: all hash same (5/5).
  T2: same tensor T, rank-8 (over-parameterized)
      -> Already verified: hashes differently from rank-7.
  T3: different tensor T' (a perturbed matmul), rank-7
      -> If (inv1, inv2) are T-fingerprints, these should hash differently.
  T4: different tensor T'' (random tensor of same shape, rank-7 if possible)
      -> Should hash differently.
  T5: 3x3 matmul tensor, rank-23 Laderman-like
      -> Different shape, different rank, different (inv1, inv2).

If T3, T4, T5 all hash distinctly from T1's hash, then (inv1, inv2) IS a
discriminator across (T, r) but constant within fixed (T, r). That makes v2
a "tensor-fingerprint canonicalizer" not an "orbit canonicalizer."

If T3 or T4 happens to hash THE SAME as T1, then (inv1, inv2) is even
weaker than expected.
"""

import numpy as np
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tensor_pilot_2x2_matmul import make_matmul_tensor, run_als, residual
from canonicalize_test import known_strassen
from agora.canonicalizer.tensor_decomp_identity_v2 import canonical_hash, minimal_invariants


def main():
    print("=== v2 invariants diagnostic — are these class-functions of T? ===\n")

    T = make_matmul_tensor(n=2)
    rng = np.random.default_rng(0)

    # Baseline: Strassen's hash
    US, VS, WS = known_strassen()
    h_strassen = canonical_hash(US, VS, WS)
    inv_strassen = minimal_invariants(US, VS, WS)
    print(f"T1 (matmul, rank-7 Strassen):")
    print(f"  hash = {h_strassen}")
    print(f"  inv1 = {inv_strassen[0]}")
    print(f"  inv2 = {inv_strassen[1]}\n")

    # T2: rank-8 of same matmul (already known different)
    A8, B8, C8, _, _ = run_als(T, rank=8, max_iters=500, seed=0)
    h_r8 = canonical_hash(A8, B8, C8)
    print(f"T2 (matmul, rank-8 ALS):")
    print(f"  hash = {h_r8}")
    print(f"  matches T1: {h_r8 == h_strassen}\n")

    # T3: perturbed matmul T' = T + small noise; find rank-7 decomp
    print("T3 (perturbed matmul T + 0.01*noise, rank-7):")
    T_perturbed = T + rng.standard_normal(T.shape) * 0.01
    Ap, Bp, Cp, resp, _ = run_als(T_perturbed, rank=7, max_iters=500, seed=0)
    print(f"  ALS residual on perturbed T: {resp:.4e}")
    if resp < 1e-3:
        h_pert = canonical_hash(Ap, Bp, Cp)
        inv_pert = minimal_invariants(Ap, Bp, Cp)
        print(f"  hash = {h_pert}")
        print(f"  inv1 = {inv_pert[0]}")
        print(f"  inv2 = {inv_pert[1]}")
        print(f"  matches T1: {h_pert == h_strassen}")
    else:
        print(f"  ALS did not converge cleanly on perturbed T; skipping hash comparison.")
    print()

    # T4: random (non-matmul) tensor of same shape, find rank-7 approx
    print("T4 (random 4x4x4 tensor, rank-7 approx):")
    T_rand = rng.standard_normal(T.shape)
    T_rand = T_rand / np.linalg.norm(T_rand) * np.linalg.norm(T)  # match Frobenius norm
    Ar, Br, Cr, resr, _ = run_als(T_rand, rank=7, max_iters=500, seed=0)
    print(f"  ALS residual: {resr:.4e}")
    h_rand = canonical_hash(Ar, Br, Cr)
    inv_rand = minimal_invariants(Ar, Br, Cr)
    print(f"  hash = {h_rand}")
    print(f"  inv1 = {inv_rand[0]}")
    print(f"  inv2 = {inv_rand[1]}")
    print(f"  matches T1: {h_rand == h_strassen}\n")

    # T5: 3x3 matmul tensor, rank-9 (under-rank, will fail to converge but invariants computable)
    # Skip this — different shape requires different code path

    # T6: SAME matmul T at rank 7, but a deliberately constructed bad decomp
    # E.g., scaled Strassen by random orthogonal matrices on each factor
    # (this just stays in the orbit but tests that random orbit elements don't
    # accidentally lose the invariant pattern)
    print("T6 (Strassen rotated by random orthogonal matrix, rank-7, same T):")
    O_A = np.linalg.qr(rng.standard_normal((4, 4)))[0]  # 4x4 orthogonal
    O_B = np.linalg.qr(rng.standard_normal((4, 4)))[0]
    # Just permute term ORDER + sign-flip per term
    perm = rng.permutation(7)
    A_rot = US[:, perm].copy()
    B_rot = VS[:, perm].copy()
    C_rot = WS[:, perm].copy()
    for i in range(7):
        if rng.random() > 0.5:
            A_rot[:, i] *= -1
            C_rot[:, i] *= -1
        if rng.random() > 0.5:
            B_rot[:, i] *= -1
            C_rot[:, i] *= -1
    res6 = residual(A_rot, B_rot, C_rot, T)
    print(f"  residual on T: {res6:.4e}")
    h6 = canonical_hash(A_rot, B_rot, C_rot)
    print(f"  hash = {h6}")
    print(f"  matches T1: {h6 == h_strassen}\n")

    # T7: matmul tensor at rank 9 (also rank-decomposable, just over-parameterized)
    print("T7 (matmul T, rank-9 over-parameterized):")
    A9, B9, C9, res9, _ = run_als(T, rank=9, max_iters=500, seed=0)
    print(f"  ALS residual: {res9:.4e}")
    h9 = canonical_hash(A9, B9, C9)
    print(f"  hash = {h9}")
    print(f"  matches T1: {h9 == h_strassen}\n")

    # Summary
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print(f"  T1 (matmul,  rank 7, Strassen): {h_strassen}")
    print(f"  T2 (matmul,  rank 8):           {h_r8}     same as T1: {h_r8 == h_strassen}")
    if resp < 1e-3:
        print(f"  T3 (PERT_T,  rank 7):           {h_pert}     same as T1: {h_pert == h_strassen}")
    print(f"  T4 (random,  rank 7):           {h_rand}     same as T1: {h_rand == h_strassen}")
    print(f"  T6 (matmul,  rank 7, sgn perm): {h6}     same as T1: {h6 == h_strassen}")
    print(f"  T7 (matmul,  rank 9):           {h9}     same as T1: {h9 == h_strassen}")

    out = Path(__file__).parent / "v2_invariants_diagnostic_results.json"
    with open(out, "w") as f:
        json.dump({
            "T1_matmul_rank7_strassen": h_strassen,
            "T2_matmul_rank8": h_r8,
            "T3_perturbed_rank7": h_pert if resp < 1e-3 else None,
            "T4_random_rank7": h_rand,
            "T6_matmul_rank7_perm": h6,
            "T7_matmul_rank9": h9,
        }, f, indent=2)


if __name__ == "__main__":
    main()
