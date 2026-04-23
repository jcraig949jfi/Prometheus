"""
CANONICALIZER:tensor_decomp_identity@v2 — Type A canonical hash for
2x2 matrix-multiplication tensor CP decompositions.

Type:    A (canonical identity — deterministic quotient + hash)
Group:   scale_gauge × sign_gauge × permutation(S_r) × GL(2)^3 matmul-covariant
         × discrete Aut(T) symmetries (transpose, factor-role permutation)
Target:  CP rank-r decompositions of T[ij, jk, ik] for 2x2 matmul (n=2)

Derivation: the matmul-covariant GL(2)^3 action on CP decompositions is
  U_r -> P U_r Q^{-1}
  V_r -> Q V_r R^{-1}
  W_r -> P^{-T} W_r R^T

Two per-term scalars are invariant under this action (verified algebraically
+ empirically):
  inv1_r = det(U_r) * det(V_r) * det(W_r)
  inv2_r = trace(U_r V_r W_r^T)

Both also happen to be invariant under the discrete Aut(T) symmetries
(transpose preserves det; trace is cyclic). The sorted-multiset pair
(sorted(inv1_1..r), sorted(inv2_1..r)) is an orbit-invariant fingerprint
on the tested inputs (4 independent ALS-converged rank-7 decompositions +
Strassen's integer decomposition).

Calibration (2026-04-23):
  - 4 ALS-converged rank-7 seeds + Strassen -> 5/5 identical hashes.
  - 10/10 random GL(2)^3 actions on Strassen preserve hash.
  - rank-8 naive decomposition hashes differently (separation OK).

Declared limitations:
  - Not proven orbit-complete in general. The minimal (inv1, inv2) pair
    passes the 2x2 calibration but has not been shown to separate all
    distinct rank-7 orbits on other tensors. For a future consumer that
    needs cross-target identity (e.g., different matmul sizes, different
    tensor targets), additional invariants may be needed.
  - Specific to 2x2 matmul shape. Factors must reshape cleanly into
    2x2 matrices.
  - Possible hash collisions with non-orbit-equivalent inputs not
    exhaustively tested. Separation is probabilistic.
"""

from __future__ import annotations
import numpy as np
import hashlib
import json


def factor_to_matrices(X: np.ndarray) -> np.ndarray:
    """Reshape factor matrix X of shape (4, r) into (r, 2, 2)."""
    r = X.shape[1]
    return np.array([X[:, i].reshape(2, 2) for i in range(r)])


def minimal_invariants(A: np.ndarray, B: np.ndarray, C: np.ndarray, decimals: int = 4):
    """Compute the Aut(T)-invariant (inv1, inv2) pair for a 2x2-matmul CP decomp.

    Args:
        A, B, C: factor matrices of shape (4, r).
        decimals: rounding precision for the returned tuples.

    Returns:
        (sorted_inv1, sorted_inv2) as tuples of floats.
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
        inv1.append(round(d, decimals))
        inv2.append(round(t, decimals))

    # Normalize -0.0 to 0.0 so hash is stable under sign-of-zero variation
    inv1 = [0.0 if x == 0.0 else x for x in inv1]
    inv2 = [0.0 if x == 0.0 else x for x in inv2]

    return tuple(sorted(inv1)), tuple(sorted(inv2))


def canonical_hash(A: np.ndarray, B: np.ndarray, C: np.ndarray, decimals: int = 4) -> str:
    """Type A canonical hash for a 2x2-matmul CP decomposition.

    Returns a 16-char hex digest (first 16 chars of SHA-256 over a
    deterministic JSON serialization of the invariant tuples).
    """
    inv1, inv2 = minimal_invariants(A, B, C, decimals=decimals)
    payload = json.dumps({
        "canonicalizer": "tensor_decomp_identity@v2",
        "inv1_det_prod": list(inv1),
        "inv2_trace_uvw": list(inv2),
    }).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


# ---------- instance metadata ----------

INSTANCE_METADATA = {
    "name": "tensor_decomp_identity",
    "version": 2,
    "type": "A",
    "equivalence_group": [
        "scale_gauge",
        "sign_gauge",
        "permutation(S_r)",
        "GL(2)^3 matmul-covariant action",
        "discrete Aut(T): transpose, factor-role permutation",
    ],
    "declared_limitations": [
        {
            "name": "orbit_completeness_not_proven",
            "severity": "partial",
            "workaround": (
                "Invariants pass the 2x2 calibration but are not proven "
                "orbit-complete in general. Consumers needing separation "
                "on other tensors should add calibration anchors per tensor "
                "target before relying on identity claims."
            ),
        },
        {
            "name": "fixed_to_2x2_matmul_shape",
            "severity": "total",
            "workaround": (
                "Factors must reshape into 2x2 matrices. For n x n matmul "
                "with n > 2, a separate instance (tensor_decomp_identity_nxn@v1) "
                "is required with the appropriate GL(n)^3 action."
            ),
        },
        {
            "name": "probabilistic_separation",
            "severity": "partial",
            "workaround": (
                "Distinct orbits producing identical (inv1, inv2) tuples "
                "would collide. Not exhaustively tested; treat as standard "
                "hash collision risk with the added risk that 2 invariants "
                "is a low-dimensional fingerprint."
            ),
        },
    ],
    "calibration_anchors": {
        "same_class": {
            "description": "4 ALS-converged rank-7 decomps + Strassen all hash identically",
            "passed": True,
            "evidence": "harmonia/tmp/tensor_gl2_invariants_minimal_results.json",
        },
        "different_class": {
            "description": "rank-8 naive decomp hashes differently from rank-7 Strassen",
            "passed": True,
        },
        "gl_invariance": {
            "description": "10/10 random GL(2)^3 actions on Strassen preserve hash",
            "passed": True,
        },
    },
    "implementation_path": "agora/canonicalizer/tensor_decomp_identity_v2.py::canonical_hash",
    "first_shipped": "2026-04-23",
}


def describe() -> dict:
    """Return instance metadata for registry introspection."""
    return INSTANCE_METADATA.copy()


if __name__ == "__main__":
    import pprint
    pprint.pp(INSTANCE_METADATA)
