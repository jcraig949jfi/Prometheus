"""
GL(2)^3 matmul-covariant action on 2x2 matmul tensor decompositions.

For the matmul tensor T[ij, jk, ik] = [same middle j], a CP rank-r
decomposition (A, B, C) with shapes (4, r) decomposes via:

  T[ij, jk, ik] = sum_r A[ij, r] B[jk, r] C[ik, r]

Each rank-1 term (u_r, v_r, w_r) reshapes to 2x2 matrices (U_r, V_r, W_r)
where U_r[i,j] = u_r[2i+j], etc. The matmul-covariant GL(2)^3 action on
the three axes of matrix multiplication (input A rows, shared dimension,
output cols) acts as:

  U_r -> P U_r Q^{-1}
  V_r -> Q V_r R^{-1}
  W_r -> P W_r R^{-1}

for (P, Q, R) in GL(2)^3. This preserves T because matmul is basis-change
covariant.

This module provides:
  - reshape factor columns to/from 2x2 matrices
  - apply the GL(2)^3 action
  - verify preservation on Strassen
  - Type A canonical form via first-term QR reduction
  - Type B integer-fraction search via coordinate descent on (P, Q, R)
"""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tensor_pilot_2x2_matmul import (
    make_matmul_tensor, run_als, residual, reconstruct
)
from canonicalize_test import canonicalize_v1, known_strassen


def factor_to_matrices(X):
    """Reshape factor matrix X of shape (4, r) into array of r 2x2 matrices.
    Returns shape (r, 2, 2) where result[i] = X[:, i].reshape(2, 2)."""
    r = X.shape[1]
    return np.array([X[:, i].reshape(2, 2) for i in range(r)])


def matrices_to_factor(Ms):
    """Inverse of factor_to_matrices: (r, 2, 2) -> (4, r)."""
    r = Ms.shape[0]
    return np.stack([Ms[i].flatten() for i in range(r)], axis=1)


def apply_gl2_action(A, B, C, P, Q, R):
    """Apply (P, Q, R) in GL(2)^3 to factor matrices (A, B, C) of shape (4, r).

    Derivation: the matmul tensor encodes <AB, C> (Frobenius inner product).
    Under the change of basis on the three underlying 2D spaces,
      A -> P A Q^{-1}   (matrix A transforms covariantly)
      B -> Q B R^{-1}   (matrix B transforms covariantly)
      C -> P^{-T} C R^T (matrix C transforms by inverse-transpose to
                         preserve the Frobenius pairing <AB, C>)

    This preserves T as a covariant 3-tensor with T[a,b,c] = selector for
    the matmul identity.

    Returns (A_new, B_new, C_new) of same shape.
    """
    Q_inv = np.linalg.inv(Q)
    R_inv = np.linalg.inv(R)
    P_inv_T = np.linalg.inv(P).T
    R_T = R.T

    As = factor_to_matrices(A)  # (r, 2, 2)
    Bs = factor_to_matrices(B)
    Cs = factor_to_matrices(C)

    As_new = np.einsum("ab,rbc,cd->rad", P, As, Q_inv)
    Bs_new = np.einsum("ab,rbc,cd->rad", Q, Bs, R_inv)
    Cs_new = np.einsum("ab,rbc,cd->rad", P_inv_T, Cs, R_T)

    return (
        matrices_to_factor(As_new),
        matrices_to_factor(Bs_new),
        matrices_to_factor(Cs_new),
    )


def verify_action_preserves_T():
    """Sanity check: apply a random (P, Q, R) to Strassen, residual stays 0."""
    T = make_matmul_tensor(n=2)
    US, VS, WS = known_strassen()
    res0 = residual(US, VS, WS, T)
    print(f"Strassen original residual: {res0:.2e}")

    rng = np.random.default_rng(42)
    for trial in range(5):
        P = rng.standard_normal((2, 2))
        Q = rng.standard_normal((2, 2))
        R = rng.standard_normal((2, 2))
        # Ensure invertible
        while abs(np.linalg.det(P)) < 0.1:
            P = rng.standard_normal((2, 2))
        while abs(np.linalg.det(Q)) < 0.1:
            Q = rng.standard_normal((2, 2))
        while abs(np.linalg.det(R)) < 0.1:
            R = rng.standard_normal((2, 2))

        A_new, B_new, C_new = apply_gl2_action(US, VS, WS, P, Q, R)
        res_new = residual(A_new, B_new, C_new, T)
        print(f"  Trial {trial} (det P={np.linalg.det(P):.2f}): res = {res_new:.2e}")
        assert res_new < 1e-10, f"Action does not preserve T! res={res_new:.2e}"

    print("GL(2)^3 action preserves T. Verified.\n")


def canonical_first_term_qr(A, B, C):
    """Type A canonical form via QR reduction of the first rank-1 term's
    U matrix plus first-term V matrix normalization.

    Strategy:
      1. Reshape first rank-1 term: U_1, V_1, W_1 as 2x2 matrices.
      2. QR-decompose U_1 = Q_U R_U. If R_U invertible, pick P = Q_U^T,
         Q = R_U^{-T} (so that U_1 becomes I under P U_1 Q^{-1}... wait,
         U_1 -> P U_1 Q^{-1} = Q_U^T Q_U R_U Q^{-1} = R_U Q^{-1}.
         Choose Q such that R_U Q^{-1} = I, i.e., Q = R_U.
         Then P = Q_U^T makes U_1 -> Q_U^T Q_U R_U R_U^{-1} = I.
      3. Now there's remaining freedom in R. Use V_1 -> Q V_1 R^{-1}.
         After step 2, V_1' = Q V_1 R^{-1} = R_U V_1 R^{-1}. Pick R
         such that first column of V_1' is canonical (e.g., unit vector).
      4. After step 3, remaining residual freedom should be near-zero
         modulo sign and permutation of rank-1 terms.

    Then apply v1 canonicalization (scale, sign, permutation) to finish.
    """
    # Step 1: reshape factor column 0 to 2x2
    As = factor_to_matrices(A)
    Bs = factor_to_matrices(B)
    Cs = factor_to_matrices(C)

    U1 = As[0]

    # Step 2: QR of U_1
    Q_U, R_U = np.linalg.qr(U1)
    # Want P U_1 Q^{-1} = I => P = Q_U^T, Q = R_U
    if abs(np.linalg.det(R_U)) < 1e-8:
        # Can't canonicalize; fall through with identity P, Q, R
        P = np.eye(2)
        Q = np.eye(2)
    else:
        P = Q_U.T
        Q = R_U.copy()  # so Q^{-1} = R_U^{-1}; P U_1 Q^{-1} = Q_U^T Q_U R_U R_U^{-1} = I

    # Apply (P, Q, I) — I on the third axis — then pick R
    A1, B1, C1 = apply_gl2_action(A, B, C, P, Q, np.eye(2))

    # Step 3: reshape first rank-1 term of B after transformation
    Bs1 = factor_to_matrices(B1)
    V1_new = Bs1[0]  # This is Q V_1 I^{-1} = Q V_1

    # Pick R such that first column of V_1_new @ R^{-1} is a canonical unit vector
    # V_1_new R^{-1} — pick R such that first column is e_1
    # That means R has first column = V_1_new[:, 0] normalized? Let's QR V_1_new too.
    Q_V, R_V = np.linalg.qr(V1_new)
    if abs(np.linalg.det(R_V)) < 1e-8:
        R = np.eye(2)
    else:
        # Want Q V_1 R^{-1} canonical. V_1_new = Q V_1 already applied.
        # Now V_1_new R^{-1} should be canonicalized. Use R = R_V so V_1_new R^{-1} = Q_V.
        # But we only have Q_V (orthogonal) — fix its sign so diagonal is positive
        R = R_V.copy()
        # Sign gauge: make diagonal of Q_V positive by flipping signs
        # (this affects both A and C via R_V, but that's fine per contract)

    A2, B2, C2 = apply_gl2_action(A1, B1, C1, np.eye(2), np.eye(2), R)

    # Step 4: apply v1 canonicalization (scale, sign, permutation)
    A_final, B_final, C_final = canonicalize_v1(A2, B2, C2)

    return A_final, B_final, C_final


def canonical_hash_v2_qr(A, B, C, decimals=4):
    """Hash after QR-canonical basis reduction + v1 canonicalization."""
    import hashlib
    A_c, B_c, C_c = canonical_first_term_qr(A, B, C)
    flat = np.concatenate([A_c.flatten(), B_c.flatten(), C_c.flatten()])
    rounded = np.round(flat, decimals=decimals)
    return hashlib.sha256(rounded.tobytes()).hexdigest()[:16]


# ---------------- Type B integer search via GL(2)^3 optimization ----------------

def integer_fraction(A, B, C, atol=0.01):
    e = np.concatenate([A.flatten(), B.flatten(), C.flatten()])
    return float(np.mean(np.abs(e - np.round(e)) < atol))


def search_integer_via_gl2(A0, B0, C0, T, n_trials=500, step_scale=0.3, seed=0):
    """Type B: search (P, Q, R) in GL(2)^3 to maximize integer_fraction of
    the transformed factors. Uses random perturbation + acceptance on improve.
    Because the action preserves T exactly, reconstruction residual stays 0.
    """
    rng = np.random.default_rng(seed)
    P = np.eye(2)
    Q = np.eye(2)
    R = np.eye(2)

    A_best, B_best, C_best = apply_gl2_action(A0, B0, C0, P, Q, R)
    A_c, B_c, C_c = canonicalize_v1(A_best, B_best, C_best)
    best_if = integer_fraction(A_c, B_c, C_c)
    history = [{"trial": -1, "integer_fraction": best_if}]

    for trial in range(n_trials):
        # Perturb (P, Q, R) multiplicatively: new = I + eps * N
        scale = step_scale * (1.0 - trial / n_trials) + 0.01
        P_new = P + rng.standard_normal((2, 2)) * scale
        Q_new = Q + rng.standard_normal((2, 2)) * scale
        R_new = R + rng.standard_normal((2, 2)) * scale

        # Keep invertible
        if abs(np.linalg.det(P_new)) < 0.1: continue
        if abs(np.linalg.det(Q_new)) < 0.1: continue
        if abs(np.linalg.det(R_new)) < 0.1: continue

        A_new, B_new, C_new = apply_gl2_action(A0, B0, C0, P_new, Q_new, R_new)
        A_c, B_c, C_c = canonicalize_v1(A_new, B_new, C_new)
        if_new = integer_fraction(A_c, B_c, C_c)

        if if_new > best_if:
            best_if = if_new
            P, Q, R = P_new, Q_new, R_new
            A_best, B_best, C_best = A_c, B_c, C_c
            history.append({"trial": trial, "integer_fraction": best_if})

    res = residual(A_best, B_best, C_best, T)
    return A_best, B_best, C_best, res, best_if, history


# ---------------- main: run W2 Strategy 2 + W3 Strategy D ----------------

def main():
    T = make_matmul_tensor(n=2)
    print("=== GL(2)^3 matmul-covariant action ===\n")

    # Phase 0: verify action preserves T
    verify_action_preserves_T()

    # ===== Phase 1: W2 Strategy 2 — Type A canonical via QR-reduction =====
    print("=" * 60)
    print("W2 Strategy 2 — Type A canonical form via QR-reduction of first rank-1 term")
    print("=" * 60)

    US, VS, WS = known_strassen()
    h_strassen = canonical_hash_v2_qr(US, VS, WS)
    print(f"Strassen QR-canonical hash: {h_strassen}")

    print("\nCollecting ALS-converged seeds at rank 7...")
    seeds = []
    for seed in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=seed)
        if res < 1e-10:
            seeds.append({"seed": seed, "A": A, "B": B, "C": C, "residual": res})
    print(f"  {len(seeds)} machine-precision seeds.\n")

    print("Per-seed QR-canonical hashes:")
    strat2_hashes = []
    for s in seeds:
        h = canonical_hash_v2_qr(s["A"], s["B"], s["C"])
        strat2_hashes.append(h)
        match = "YES" if h == h_strassen else "NO"
        print(f"  seed {s['seed']}: hash={h}  matches_strassen={match}")
    n_match_strassen = sum(1 for h in strat2_hashes if h == h_strassen)
    n_pair_same = 0
    n_pairs = 0
    for i in range(len(strat2_hashes)):
        for j in range(i + 1, len(strat2_hashes)):
            n_pairs += 1
            if strat2_hashes[i] == strat2_hashes[j]:
                n_pair_same += 1
    print(f"\nPair-agreement: {n_pair_same}/{n_pairs}. Strassen matches: {n_match_strassen}/{len(strat2_hashes)}.")
    if n_match_strassen == len(strat2_hashes) and n_pair_same == n_pairs:
        print("W2 STRATEGY 2: PASS (all orbit elements collapse to one hash)")
    elif n_pair_same > 0 or n_match_strassen > 0:
        print("W2 STRATEGY 2: PARTIAL (some collapse; strategy needs refinement)")
    else:
        print("W2 STRATEGY 2: FAIL (QR reduction alone insufficient)")

    # ===== Phase 2: W3 Strategy D — Type B integer search via GL(2)^3 =====
    print()
    print("=" * 60)
    print("W3 Strategy D — Type B integer search via GL(2)^3 action")
    print("=" * 60)

    results = []
    for s in seeds:
        A0, B0, C0 = canonicalize_v1(s["A"], s["B"], s["C"])
        if_start = integer_fraction(A0, B0, C0)
        A_out, B_out, C_out, res_out, if_out, history = search_integer_via_gl2(
            s["A"], s["B"], s["C"], T, n_trials=500, step_scale=0.5, seed=s["seed"]
        )
        results.append({
            "seed": s["seed"],
            "start_if": if_start,
            "end_if": if_out,
            "delta": if_out - if_start,
            "final_residual": res_out,
            "history_len": len(history),
        })
        print(f"  seed {s['seed']}: start_if={if_start:.3f} -> end_if={if_out:.3f}  (delta={if_out-if_start:+.3f}, res={res_out:.2e}, {len(history)} improvements)")

    best_if = max(r["end_if"] for r in results) if results else 0
    n_near_strassen = sum(1 for r in results if r["end_if"] >= 0.9)
    print(f"\n  Best end_if across seeds: {best_if:.3f} (Strassen: 1.000)")
    print(f"  Seeds reaching >= 0.9: {n_near_strassen} / {len(results)}")
    if n_near_strassen > 0:
        print("W3 STRATEGY D: PASS (GL(2)^3 search recovers near-integer representative)")
    elif best_if > max((r["start_if"] for r in results), default=0) + 0.2:
        print("W3 STRATEGY D: PARTIAL (improves integer_fraction meaningfully, does not reach Strassen)")
    else:
        print("W3 STRATEGY D: FAIL (no meaningful improvement over v1 starting point)")

    # Save
    import json
    out = Path(__file__).parent / "tensor_gl2_action_results.json"
    dump = {
        "w2_strategy_2_qr_reduction": {
            "strassen_hash": h_strassen,
            "seed_hashes": strat2_hashes,
            "pair_same": n_pair_same,
            "n_pairs": n_pairs,
            "strassen_matches": n_match_strassen,
            "verdict": (
                "PASS" if (n_match_strassen == len(strat2_hashes) and n_pair_same == n_pairs)
                else "PARTIAL" if (n_pair_same > 0 or n_match_strassen > 0)
                else "FAIL"
            ),
        },
        "w3_strategy_d_gl2_integer_search": {
            "results": results,
            "best_end_if": best_if,
            "n_near_strassen": n_near_strassen,
            "verdict": (
                "PASS" if n_near_strassen > 0
                else "PARTIAL" if best_if > max((r["start_if"] for r in results), default=0) + 0.2
                else "FAIL"
            ),
        },
    }
    with open(out, "w") as f:
        json.dump(dump, f, indent=2, default=str)
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
