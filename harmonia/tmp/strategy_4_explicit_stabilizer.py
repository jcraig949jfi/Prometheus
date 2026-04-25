"""Strategy 4: Type A canonicalizer for 2x2 matmul rank-r decompositions
via explicit parameterization of the GL(2)^3 matmul-covariant action.

Recipe (per James 2026-04-24 deep dive):
  1. Apply v1 canonicalization (quotients scale + sign + permutation).
  2. Pick anchor rank-1 term r* = argmax |det(U_r) det(V_r) det(W_r)|
     among the (typically unique) full-rank term.
  3. Use the GL(2)^3 freedom to pin U_{r*} = I and V_{r*} = I, leaving
     W_{r*} in a derived form. This consumes 8 of 12 dimensions of (P, Q, R).
  4. Use the residual 4-dim freedom (P' = Q' = R' diagonal, by the U_a = I
     and V_a = I constraints) to put W_{r*} into a canonical form via
     similarity (real Schur form). This consumes the remaining 4 dimensions.
  5. Apply v1 once more on the resulting triple (sign + permutation may have
     drifted); hash the final canonical (A, B, C).

Calibration target: 4 ALS-converged rank-7 seeds + Strassen ALL hash to
the same canonical form under this procedure. If they do, this is a TRUE
Type A `group_quotient` canonicalizer (orbit-level identity, not just
variety-level fingerprinting).

Outcome possibilities (per James's framing):
  - Success: gen_12 unlocks orbit-level dedup; v4 whitepaper gets
    a true `group_quotient` Type A tensor instance.
  - Failure: empirical evidence on stabilizer/orbit structure;
    no hash collapse means the GL-orbit components are genuinely
    distinct over R, confirming the v3 finding more strongly.

Either way: high information per ~60 min of work.
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


def strategy_4_canonicalize(A, B, C, eps=1e-8, verbose=False):
    """Type A canonical form via explicit GL(2)^3 stabilizer parameterization.

    Returns:
        (A_can, B_can, C_can) on success
        (None, reason) on failure (e.g., no good anchor term)
    """
    # Step 1: v1 quotient (scale, sign, permutation)
    A, B, C = canonicalize_v1(A, B, C)

    # Step 2: find anchor — term with max |det product|
    r = A.shape[1]
    Us = factor_to_matrices(A)
    Vs = factor_to_matrices(B)
    Ws = factor_to_matrices(C)

    detprods = np.array([
        np.linalg.det(Us[i]) * np.linalg.det(Vs[i]) * np.linalg.det(Ws[i])
        for i in range(r)
    ])

    if verbose:
        print(f"  detprods: {sorted(detprods)}")

    anchor = int(np.argmax(np.abs(detprods)))
    if abs(detprods[anchor]) < eps:
        return None, "no_full_rank_anchor_term"

    U_a = Us[anchor]
    V_a = Vs[anchor]
    W_a = Ws[anchor]

    # Step 3: pick (P, Q, R) so U_a -> I and V_a -> I
    # P U_a Q^{-1} = I and Q V_a R^{-1} = I
    # Solution: P = U_a^{-1}, Q = I, R = V_a (consumes 8 of 12 dims)
    if abs(np.linalg.det(U_a)) < eps:
        return None, "anchor_U_singular"
    if abs(np.linalg.det(V_a)) < eps:
        return None, "anchor_V_singular"

    P_init = np.linalg.inv(U_a)
    Q_init = np.eye(2)
    R_init = V_a.copy()

    A_t, B_t, C_t = apply_gl2_action(A, B, C, P_init, Q_init, R_init)

    # Verify U_a' = I and V_a' = I
    Us_t = factor_to_matrices(A_t)
    Vs_t = factor_to_matrices(B_t)
    Ws_t = factor_to_matrices(C_t)
    err1 = np.linalg.norm(Us_t[anchor] - np.eye(2))
    err2 = np.linalg.norm(Vs_t[anchor] - np.eye(2))
    if verbose:
        print(f"  After step 3: U_a-I norm = {err1:.2e}, V_a-I norm = {err2:.2e}")
    if err1 > 1e-6 or err2 > 1e-6:
        return None, f"step3_U_or_V_not_identity (err1={err1:.2e}, err2={err2:.2e})"

    # Step 4: residual GL freedom is (P' = Q' = R') for P' in GL(2).
    # Under this: W_a' = (P')^{-T} W_a^current (P')^T (similarity by P'^T from the right inverse).
    # Equivalently: W_a' = M^{-1} W_a^current M where M = (P')^T.
    # Pick M such that M^{-1} W_a^current M is in real-Schur form (canonical upper-quasi-triangular).
    W_a_curr = Ws_t[anchor]

    from scipy.linalg import schur
    # output='real' gives real upper quasi-triangular form
    T_schur, M = schur(W_a_curr, output='real')

    # Canonicalize Schur form: eigenvalue order is non-unique; fix it.
    # For real Schur on 2x2: T_schur is either diagonal (real eigs) or
    # has a single 2x2 block (complex conjugate pair).
    eigs = np.linalg.eigvals(W_a_curr)
    if np.all(np.abs(eigs.imag) < 1e-10):
        # Real eigenvalues — re-Schur with sort to put smaller eigenvalue first
        # scipy schur sort: callable(x) returning True puts that eigenvalue first
        eig_smaller = float(min(eigs.real))
        T_schur, M, _ = schur(W_a_curr, output='real',
                              sort=lambda x: x.real <= eig_smaller + 1e-10)

    # Sign canonicalization on M: make first non-negligible entry of each column positive
    M = M.copy()
    T_schur = T_schur.copy()
    for col in range(M.shape[1]):
        idx = np.argmax(np.abs(M[:, col]) > 1e-8)
        if M[idx, col] < 0:
            M[:, col] *= -1
            T_schur[:, col] *= -1
            T_schur[col, :] *= -1
    # T_schur = M^T W_a_curr M  (Schur returns Z such that A = Z T Z^T for orthogonal Z; M is orthogonal here)

    # We want W_a -> M^{-1} W_a M = T_schur. Action: (P')^{-T} W_a (P')^T.
    # So (P')^{-T} = M^{-1}, i.e., P' = M^{-T} = M (since M is orthogonal: M^{-T} = M).
    # Wait: scipy.linalg.schur returns A = Z T Z^* with Z unitary (orthogonal in real case).
    # So M = Z gives M^T A M = T. Equivalent: M^{-1} A M = T (since M orthogonal).
    # We want (P')^{-T} W_a (P')^T = T. So (P')^T = M means P' = M^T.
    # Verify: ((M^T))^{-T} W_a (M^T)^T = (M^T)^{-T} W_a M = M W_a M^T... wait that's not T.
    # Let me redo. M is orthogonal so M^T = M^{-1}. P'^T = M means P' = M^T = M^{-1}.
    # Then (P')^{-T} = (M^{-1})^{-T} = M^T = M^{-1}.
    # And (P')^T = (M^{-1})^T = M^T^{-T}... ugh confusing.
    # Let's just compute directly:

    # P' = M.T (so P'^T = M, P'^{-T} = (M.T)^{-T} = (M.T)^{-1}.T = M.T (orthogonal))
    # Wait if M is orthogonal then M.T = M^{-1}. And (M.T)^{-T} = (M^{-1})^{-T} = M^T = M^{-1}.
    # So (P')^{-T} = M^{-1} and (P')^T = M.

    # The action: W_a -> (P')^{-T} W_a (P')^T = M^{-1} W_a M.
    # And from Schur: M^{-1} W_a M = T_schur (since W_a = M T_schur M^{-1}, equivalently
    #                                        T_schur = M^{-1} W_a M = M.T W_a M).
    # YES — so this gives W_a' = T_schur. Good.

    P_resid = M.T  # this is what we apply
    Q_resid = P_resid.copy()
    R_resid = P_resid.copy()

    A_f, B_f, C_f = apply_gl2_action(A_t, B_t, C_t, P_resid, Q_resid, R_resid)

    # Sign canonicalization on T_schur diagonal: schur form can have negative diagonal.
    # The remaining freedom is sign-flips that preserve the action structure.
    # For now: apply v1 once more to handle sign + permutation drift.
    A_f, B_f, C_f = canonicalize_v1(A_f, B_f, C_f)

    return (A_f, B_f, C_f), None


def canonical_hash_strategy_4(A, B, C, decimals=4):
    """Hash via Strategy 4 explicit-stabilizer canonical form."""
    result, err = strategy_4_canonicalize(A, B, C)
    if result is None:
        return f"FAILURE:{err}"
    A_c, B_c, C_c = result
    flat = np.concatenate([A_c.flatten(), B_c.flatten(), C_c.flatten()])
    rounded = np.round(flat, decimals=decimals)
    return hashlib.sha256(rounded.tobytes()).hexdigest()[:16]


def main():
    T = make_matmul_tensor(n=2)
    print("=== Strategy 4 — explicit-stabilizer Type A canonicalizer ===\n")

    US, VS, WS = known_strassen()

    # Diagnostic: canonicalize Strassen
    print("Strassen:")
    h_strassen = canonical_hash_strategy_4(US, VS, WS)
    print(f"  hash: {h_strassen}\n")

    # Sanity: random GL(2)^3 action on Strassen, should hash same
    print("Sanity — 5 random GL(2)^3 actions on Strassen should preserve hash:")
    rng = np.random.default_rng(0)
    n_stable = 0
    n_total = 5
    for trial in range(n_total):
        P = rng.standard_normal((2, 2))
        Q = rng.standard_normal((2, 2))
        R = rng.standard_normal((2, 2))
        while abs(np.linalg.det(P)) < 0.1: P = rng.standard_normal((2, 2))
        while abs(np.linalg.det(Q)) < 0.1: Q = rng.standard_normal((2, 2))
        while abs(np.linalg.det(R)) < 0.1: R = rng.standard_normal((2, 2))
        A_act, B_act, C_act = apply_gl2_action(US, VS, WS, P, Q, R)
        h_act = canonical_hash_strategy_4(A_act, B_act, C_act)
        match = h_act == h_strassen
        n_stable += int(match)
        if not match:
            print(f"  trial {trial}: HASH DRIFT  {h_act}")
        else:
            print(f"  trial {trial}: stable")
    print(f"  {n_stable}/{n_total} preserve Strassen's hash under random action\n")

    # Calibration: do 4 ALS seeds + Strassen all hash to same value?
    print("Calibration — 4 ALS-converged rank-7 seeds vs Strassen:")
    seeds = []
    for s in range(20):
        A, B, C, res, _ = run_als(T, rank=7, max_iters=500, seed=s)
        if res < 1e-10:
            seeds.append({"seed": s, "A": A, "B": B, "C": C})
    print(f"  Found {len(seeds)} machine-precision seeds.\n")

    seed_hashes = []
    for s in seeds:
        h = canonical_hash_strategy_4(s["A"], s["B"], s["C"])
        match = "YES" if h == h_strassen else "NO"
        print(f"  seed {s['seed']}: hash={h}  matches_strassen={match}")
        seed_hashes.append(h)
    n_match_strassen = sum(1 for h in seed_hashes if h == h_strassen)
    n_pair_same = 0
    n_pairs = 0
    for i in range(len(seed_hashes)):
        for j in range(i + 1, len(seed_hashes)):
            n_pairs += 1
            if seed_hashes[i] == seed_hashes[j]:
                n_pair_same += 1
    print(f"\n  Pair-agreements: {n_pair_same}/{n_pairs}")
    print(f"  Strassen matches: {n_match_strassen}/{len(seed_hashes)}")

    # Different-class anchor: rank-8 should hash differently
    print("\nDifferent-class — rank-8 should hash differently:")
    A8, B8, C8, _, _ = run_als(T, rank=8, max_iters=500, seed=0)
    h8 = canonical_hash_strategy_4(A8, B8, C8)
    print(f"  rank-8 hash: {h8}")
    print(f"  differs from Strassen: {h8 != h_strassen}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT on Strategy 4")
    print("=" * 60)
    sanity_ok = n_stable == n_total
    same_class_ok = n_match_strassen == len(seed_hashes) and n_pair_same == n_pairs
    diff_class_ok = h8 != h_strassen

    if sanity_ok and same_class_ok and diff_class_ok:
        print("  ALL CALIBRATION ANCHORS PASS.")
        print("  Strategy 4 is a valid Type A `group_quotient` canonicalizer for 2x2 matmul.")
        print("  Ready to register as `tensor_decomp_identity_orbit@v1`.")
    elif sanity_ok and not same_class_ok:
        print("  PARTIAL. GL invariance OK; same-class collapse FAILED.")
        print(f"  {n_pair_same}/{n_pairs} pair-agreements.")
        print("  Indicates either: (a) anchor selection is unstable across seeds,")
        print("  (b) Schur form non-uniqueness across orbits, or")
        print("  (c) v3's hypothesis confirmed: V_T(7) over R has multiple")
        print("      disconnected GL(2,R)^3-orbit components.")
    elif not sanity_ok:
        print(f"  SANITY FAILED ({n_stable}/{n_total} stable).")
        print()
        print("  Diagnosis: anchor-only canonicalization is insufficient.")
        print("  After Step 3 fixes U_a = V_a = I for the anchor term, the OTHER")
        print("  6 rank-1 terms still carry the residual GL-freedom from the")
        print("  initial random action. Step 4's residual (P'=Q'=R') consumes")
        print("  4 dims by canonicalizing the anchor's W, but the (P_init, Q_init,")
        print("  R_init) chosen in Step 3 is itself dependent on which orbit point")
        print("  we started from. Hence other terms r != anchor end up at different")
        print("  locations between Strassen and acted_Strassen, producing different")
        print("  hashes after final v1 sort.")
        print()
        print("  Required: joint canonicalization across ALL rank-1 terms, not")
        print("  just the anchor. This needs either:")
        print("    - A second anchor term to consume residual P-freedom by")
        print("      pinning ITS U (or V or W) to canonical form simultaneously")
        print("      with the first anchor's. Constraint compatibility is non-trivial.")
        print("    - Polynomial invariants of the WHOLE decomposition (not just")
        print("      per-term) that distinguish ORBIT COMPONENTS within V_T(r)")
        print("      while remaining GL-invariant. Open mathematics.")
        print("    - Joint diagonalization respecting the matmul-coupling on")
        print("      multiple W_r's simultaneously. Computationally hard.")
        print()
        print("  Strategy 4 as initially scoped is insufficient. The instructive")
        print("  finding is that GL(2)^3 freedom is not absorbed by single-anchor")
        print("  canonicalization; orbit-level Type A for matmul tensors over R")
        print("  remains an open problem. The variety_fingerprint v2 instance")
        print("  stands as the shippable Type A canonicalization at this granularity.")
    else:
        print("  FAIL.")

    out = Path(__file__).parent / "strategy_4_results.json"
    dump = {
        "strassen_hash": h_strassen,
        "n_stable_under_random_GL": n_stable,
        "n_total_random_GL_trials": n_total,
        "n_seeds": len(seeds),
        "seed_hashes": seed_hashes,
        "n_pair_same": n_pair_same,
        "n_pairs": n_pairs,
        "n_match_strassen": n_match_strassen,
        "rank8_hash": h8,
        "rank8_differs_from_strassen": h8 != h_strassen,
        "verdict": "PASS" if (sanity_ok and same_class_ok and diff_class_ok) else "FAIL_OR_PARTIAL",
    }
    with open(out, "w") as f:
        json.dump(dump, f, indent=2, default=str)
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
