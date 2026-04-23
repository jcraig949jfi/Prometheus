"""
CANONICALIZER:tensor_decomp_identity@v2 — multi-invariant canonical form.

Strategy: after v1 canonicalization (scale + sign + permutation), compute
basis-independent numerical invariants of the (A, B, C) triple. Hash
the sorted invariants.

Invariants attempted (all should be basis-invariant under orthogonal change;
partially basis-invariant under general GL):
  1. Singular value spectra of A, B, C (sorted descending).
  2. Eigenvalue spectra of Gramians A^T A, B^T B, C^T C (= squared SVs).
  3. Frobenius norms per rank-1 term: ||u_i|| * ||v_i|| * ||w_i|| (sorted).
  4. Trace of A^T B, A^T C, B^T C (basis-DEP, used only as sanity check).
  5. Multi-trace of tensor mode unfoldings: T_(0) T_(0)^T eigenvalues, etc.

Calibration: the 4 ALS-converged rank-7 seeds from the 2x2 pilot + Strassen's
integer representative should all hash identically under v2.

EXPERIMENT: this may fail. If invariants coincide across the orbit, pass.
If they differ, v2 strategy is insufficient and needs a different approach
(candidates in orbit_vs_representative.md: SVD/Schur basis alignment,
orbit-internal integer search which is Type B, or full group enumeration).
"""

import numpy as np
import hashlib
import json
from pathlib import Path

# Import pilot code
import sys
sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import (
    make_matmul_tensor, run_als, reconstruct, residual
)
from canonicalize_test import canonicalize_v1, known_strassen


def multi_invariants(A, B, C, decimals=4):
    """Compute a vector of basis-invariant numerical features.

    Each invariant is a sorted tuple of numbers rounded to `decimals`
    decimal places, for hash stability.
    """
    A, B, C = np.array(A, dtype=float), np.array(B, dtype=float), np.array(C, dtype=float)
    invariants = {}

    # 1. Singular values of each factor (sorted descending)
    invariants["sv_A"] = tuple(np.round(sorted(np.linalg.svd(A, compute_uv=False), reverse=True), decimals))
    invariants["sv_B"] = tuple(np.round(sorted(np.linalg.svd(B, compute_uv=False), reverse=True), decimals))
    invariants["sv_C"] = tuple(np.round(sorted(np.linalg.svd(C, compute_uv=False), reverse=True), decimals))

    # 2. Frobenius norms of full factor matrices (invariant under orthogonal)
    invariants["fro_A"] = float(np.round(np.linalg.norm(A, 'fro'), decimals))
    invariants["fro_B"] = float(np.round(np.linalg.norm(B, 'fro'), decimals))
    invariants["fro_C"] = float(np.round(np.linalg.norm(C, 'fro'), decimals))

    # 3. Per-rank-1 term magnitudes (sorted) — invariant under scale+sign+permutation
    r = A.shape[1]
    magnitudes = []
    for i in range(r):
        m = np.linalg.norm(A[:, i]) * np.linalg.norm(B[:, i]) * np.linalg.norm(C[:, i])
        magnitudes.append(m)
    invariants["term_magnitudes"] = tuple(np.round(sorted(magnitudes, reverse=True), decimals))

    # 4. Mode unfolding singular values (basis-invariant for the tensor T itself)
    # T is the reconstructed tensor; mode-k unfolding SVs
    T_hat = np.einsum("ir,jr,kr->ijk", A, B, C)
    n = T_hat.shape[0]
    for mode in range(3):
        unfolding = np.moveaxis(T_hat, mode, 0).reshape(n, -1)
        svs = np.linalg.svd(unfolding, compute_uv=False)
        invariants[f"unfold_mode{mode}_sv"] = tuple(np.round(sorted(svs, reverse=True), decimals))

    # 5. Gramian eigenvalue spectra (redundant with SVs but included as cross-check)
    for name, M in [("A", A), ("B", B), ("C", C)]:
        G = M.T @ M  # (r, r) Gramian
        evs = np.sort(np.linalg.eigvalsh(G))[::-1]
        invariants[f"gram_{name}_ev"] = tuple(np.round(evs, decimals))

    return invariants


def canonical_hash_v2(A, B, C, decimals=4):
    """Type A canonical hash: apply v1 canonicalization, compute invariants, hash.

    Note: v1 canonicalization is a no-op on invariants (invariants are already
    basis-independent), but we apply it anyway so the pipeline is composable.
    """
    A1, B1, C1 = canonicalize_v1(A, B, C)
    inv = multi_invariants(A1, B1, C1, decimals=decimals)
    # Serialize invariants deterministically
    payload = json.dumps(inv, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def get_machine_precision_seeds(T, n_seeds=20, rank=7, tol=1e-10):
    """Re-run ALS and keep only seeds at machine precision."""
    results = []
    for seed in range(n_seeds):
        A, B, C, res, iters = run_als(T, rank=rank, max_iters=500, seed=seed)
        if res < tol:
            results.append({
                "seed": seed,
                "residual": res,
                "A": A, "B": B, "C": C,
            })
    return results


def main():
    T = make_matmul_tensor(n=2)
    print("=== CANONICALIZER:tensor_decomp_identity@v2 — multi-invariant test ===\n")
    print(f"Tensor T: shape={T.shape}, ||T||_F={np.linalg.norm(T):.4f}\n")

    # 1. Compute Strassen's v2 hash
    US, VS, WS = known_strassen()
    assert residual(US, VS, WS, T) < 1e-10, "Strassen reconstruction broken"
    h_strassen = canonical_hash_v2(US, VS, WS)
    inv_strassen = multi_invariants(*canonicalize_v1(US, VS, WS))
    print(f"Strassen v2 hash: {h_strassen}")
    print(f"  term_magnitudes: {inv_strassen['term_magnitudes']}")
    print(f"  sv_A: {inv_strassen['sv_A']}")
    print(f"  fro_A = {inv_strassen['fro_A']}, fro_B = {inv_strassen['fro_B']}, fro_C = {inv_strassen['fro_C']}")
    print()

    # 2. Collect ALS-converged seeds at rank 7
    print("Collecting machine-precision ALS seeds (residual < 1e-10)...")
    seeds = get_machine_precision_seeds(T, n_seeds=20, rank=7, tol=1e-10)
    print(f"  Found {len(seeds)} machine-precision seeds.\n")

    # 3. Compute v2 hashes for each seed
    print("Per-seed v2 hashes:")
    print(f"  {'seed':>5} {'residual':>12} {'hash':>18}  same_as_strassen")
    seed_hashes = []
    for s in seeds:
        h = canonical_hash_v2(s["A"], s["B"], s["C"])
        seed_hashes.append(h)
        mark = "YES" if h == h_strassen else "NO"
        print(f"  {s['seed']:>5} {s['residual']:>12.2e} {h:>18}  {mark}")
    print()

    # 4. Pairwise collision check (same-orbit anchor)
    print("Pairwise hash agreement among ALS seeds:")
    n_same, n_pairs = 0, 0
    for i in range(len(seed_hashes)):
        for j in range(i + 1, len(seed_hashes)):
            n_pairs += 1
            if seed_hashes[i] == seed_hashes[j]:
                n_same += 1
    print(f"  {n_same} / {n_pairs} ALS-seed pairs hash identically under v2")
    print()

    # 5. Match with Strassen
    strassen_matches = sum(1 for h in seed_hashes if h == h_strassen)
    print(f"Strassen matches: {strassen_matches} / {len(seed_hashes)} ALS seeds hash same as Strassen")
    print()

    # 6. Verdict
    print("=== VERDICT on tensor_decomp_identity@v2 ===")
    pairs_ok = (n_pairs == 0 or n_same == n_pairs)
    strassen_ok = (len(seed_hashes) == 0 or strassen_matches == len(seed_hashes))
    if pairs_ok and strassen_ok:
        print("  PASS. All same-orbit inputs hash identically under v2.")
        print("  Multi-invariant strategy validated on 2x2 matmul.")
    elif strassen_matches > 0 or n_same > 0:
        print(f"  PARTIAL. Some pairs match ({n_same}/{n_pairs}), some Strassen ({strassen_matches}/{len(seed_hashes)}).")
        print("  Multi-invariant strategy partially collapses orbit; still insufficient.")
    else:
        print("  FAIL. Multi-invariant strategy does NOT collapse the orbit.")
        print("  Failure is data: the basis-invariants computed here do not uniquely identify")
        print("  the T-stabilizer orbit. Next candidate: SVD/Schur basis alignment, or a richer")
        print("  invariant family including GL-covariant tensor-network contractions.")
    print()

    # 7. Diagnostic: dump Strassen vs one ALS seed invariants side-by-side
    if seeds:
        print("Diagnostic — Strassen vs seed 8 invariants:")
        inv_seed = multi_invariants(*canonicalize_v1(seeds[0]["A"], seeds[0]["B"], seeds[0]["C"]))
        for key in sorted(inv_strassen.keys()):
            s_val = inv_strassen[key]
            a_val = inv_seed.get(key)
            same = "==" if s_val == a_val else "!="
            print(f"  {key}: strassen {s_val} {same} seed{seeds[0]['seed']} {a_val}")

    # Save results
    out = Path(__file__).parent / "tensor_decomp_identity_v2_results.json"
    dump = {
        "strassen_hash": h_strassen,
        "strassen_invariants": {k: list(v) if isinstance(v, tuple) else v for k, v in inv_strassen.items()},
        "n_seeds": len(seeds),
        "seed_hashes": seed_hashes,
        "pair_same_pct": (n_same / max(1, n_pairs)),
        "strassen_matches": strassen_matches,
        "verdict": "PASS" if (pairs_ok and strassen_ok) else ("PARTIAL" if (n_same > 0 or strassen_matches > 0) else "FAIL"),
    }
    with open(out, "w") as f:
        json.dump(dump, f, indent=2, default=str)
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
