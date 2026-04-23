"""
Gauge group for the 2x2 matmul tensor over F_2 and canonicalization.

Gauge group
-----------
1. S_r: permutation of the r rank-1 summands.
2. Matmul-isotropy subgroup of GL_2(F_2)^3: the triples (A, B, C) that leave
   the matmul tensor invariant.

Action on a decomposition (U, V, W), columns (u_i, v_i, w_i) representing
vec(X_i), vec(Y_i), vec(Z_i) respectively:

    X_i -> A X_i B^{-1}
    Y_i -> B Y_i C^{-1}
    Z_i -> A Z_i C^{-1}

which in row-major vec is a linear map on each factor matrix. Because
Z_i = X_i Y_i is preserved:
    A X_i B^{-1} * B Y_i C^{-1} = A X_i Y_i C^{-1} = A Z_i C^{-1}
so the matmul relation (and therefore the matmul tensor) is preserved.

Over F_2 the scaling gauge (lambda a_i, mu b_i, (lambda mu)^-1 c_i) is
trivial (lambda = mu = 1). So the gauge group is S_r x {(A,B,C) in GL_2(F_2)^3}
and canonicalization is combinatorial: O(|S_r| * |GL_2|^3) per decomposition,
but we quotient by S_r on the fly via column sorting, bringing it to O(|GL_2|^3).

Over F_2, |GL_2(F_2)| = 6, so |GL_2|^3 = 216 basis transforms to try.
"""
from __future__ import annotations
import itertools
import numpy as np
from .core import (
    reconstruct, MATMUL_T, is_matmul_decomp, sort_columns, decomp_to_bytes,
    column_keys,
)


# -----------------------------------------------------------------------------
# GL_2(F_2)
# -----------------------------------------------------------------------------

def enumerate_GL2_F2() -> list[np.ndarray]:
    """Return the 6 elements of GL_2(F_2) as (2,2) uint8 arrays."""
    out = []
    for bits in range(16):
        m = np.array([(bits >> 3) & 1, (bits >> 2) & 1,
                      (bits >> 1) & 1, bits & 1], dtype=np.uint8).reshape(2, 2)
        # det mod 2
        det = (int(m[0, 0]) * int(m[1, 1]) - int(m[0, 1]) * int(m[1, 0])) & 1
        if det == 1:
            out.append(m)
    return out


GL2 = enumerate_GL2_F2()
assert len(GL2) == 6, f"GL_2(F_2) should have 6 elements, got {len(GL2)}"


def _gf2_inv2(m: np.ndarray) -> np.ndarray:
    """2x2 inverse over F_2 (uses det=1, adjugate)."""
    # Over F_2, inverse of [[a,b],[c,d]] with ad+bc=1 is [[d,b],[c,a]].
    return np.array([[m[1, 1], m[0, 1]], [m[1, 0], m[0, 0]]], dtype=np.uint8) & 1


GL2_INV = [_gf2_inv2(g) for g in GL2]

# Row-major vec: vec(X)[2*i + j] = X[i, j].
# Linear map on vec(X) sending X -> A X B^{-1}:
#     vec(A X B^{-1})[2*i + j] = sum_{a,b} A[i,a] X[a,b] B^{-1}[b,j]
# which is (A (x) B^{-T}) acting on vec(X) in row-major (because we go row-first).
# Here B^{-T} = (B^{-1})^T. So build a 4x4 matrix M(A, B) for each basis pair.

def _action_on_mode(A: np.ndarray, Binv: np.ndarray) -> np.ndarray:
    """Build the 4x4 matrix over F_2 that sends vec(X) to vec(A X B^{-1}).

    In row-major, M = A (x) (B^{-1})^T.
    """
    Binv_T = Binv.T
    return np.kron(A, Binv_T).astype(np.uint8) & 1


def _preserves_matmul(M_U, M_V, M_W) -> bool:
    """Test whether pushforward (M_U (x) M_V (x) M_W) T = T for the matmul tensor.

    Over F_2 with 2x2 matmul, the action (M_U, M_V, M_W) =
        (A (x) B^{-T}, B (x) C^{-T}, A (x) C^{-T})
    preserves matmul iff A A^T = I AND C C^T = I (orthogonality over F_2).
    Rather than hard-code this, we test empirically.
    """
    from .core import MATMUL_T
    # Pushforward: T'[i,j,k] = sum M_U[i,i'] M_V[j,j'] M_W[k,k'] T[i',j',k']
    T = MATMUL_T.astype(np.int32)
    # Use einsum over F_2 then reduce mod 2.
    Tp = np.einsum('ia,jb,kc,abc->ijk',
                   M_U.astype(np.int32),
                   M_V.astype(np.int32),
                   M_W.astype(np.int32),
                   T) & 1
    return np.array_equal(Tp.astype(np.uint8), MATMUL_T)


def build_iso_actions():
    """Build matmul-preserving actions under the GL_2(F_2)^3 parameterization.

    The parameterization (A, B, C) -> (A (x) B^{-T}, B (x) C^{-T}, A (x) C^{-T})
    is derived from the matmul relation X Y = Z under basis change
    (X, Y, Z) -> (A X B^{-1}, B Y C^{-1}, A Z C^{-1}).

    Over F_2 with n=2, tensor-preservation requires A and C orthogonal
    (A A^T = I, C C^T = I), because over char-2 the summation
    (A A^T)[i, i'] does NOT collapse to delta unless A is orthogonal.

    We enumerate all 216 triples and keep only the ~24 that empirically
    satisfy (M_U (x) M_V (x) M_W) T_matmul = T_matmul. This is a valid
    subgroup of the full matmul isotropy; cyclic (mode-transpose) and
    other isotropy-broadening actions are not included in the pilot.

    Returns a list of (M_U, M_V, M_W, (iA, iB, iC)) tuples.
    """
    all_actions = []
    for iA, A in enumerate(GL2):
        for iB, B in enumerate(GL2):
            Binv = GL2_INV[iB]
            for iC, C in enumerate(GL2):
                Cinv = GL2_INV[iC]
                M_U = _action_on_mode(A, Binv)
                M_V = _action_on_mode(B, Cinv)
                M_W = _action_on_mode(A, Cinv)
                all_actions.append((M_U, M_V, M_W, (iA, iB, iC)))

    # Filter to matmul-preserving subgroup.
    preserving = [t for t in all_actions if _preserves_matmul(t[0], t[1], t[2])]
    return preserving


ISO_ACTIONS = build_iso_actions()
# Size depends on F_2 orthogonality constraint; expected 24 for 2x2 matmul.
ISO_SIZE = len(ISO_ACTIONS)
assert ISO_SIZE >= 1, "matmul isotropy subgroup unexpectedly empty"


def apply_iso(U: np.ndarray, V: np.ndarray, W: np.ndarray,
              action_idx: int):
    """Apply the action_idx-th matmul isotropy element to a decomposition."""
    M_U, M_V, M_W, _ = ISO_ACTIONS[action_idx]
    U2 = (M_U @ U) & 1
    V2 = (M_V @ V) & 1
    W2 = (M_W @ W) & 1
    return U2, V2, W2


# -----------------------------------------------------------------------------
# Canonicalization
# -----------------------------------------------------------------------------

def canonicalize(U: np.ndarray, V: np.ndarray, W: np.ndarray):
    """Compute the canonical form of (U, V, W) under S_r x matmul-isotropy.

    Strategy: for each of the 216 isotropy transforms, apply it, sort columns
    (quotients by S_r), and take the lex-smallest serialization.

    Returns:
        best_tuple: (U_c, V_c, W_c) canonical representative
        best_bytes: serialized canonical form (for hashing/equality)
    """
    best_bytes = None
    best_tuple = None
    for idx in range(len(ISO_ACTIONS)):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        # Drop all-zero columns (they add nothing to the tensor).
        nz = ~((U2.sum(0) == 0) & (V2.sum(0) == 0) & (W2.sum(0) == 0))
        U2 = U2[:, nz]
        V2 = V2[:, nz]
        W2 = W2[:, nz]
        if U2.shape[1] == 0:
            continue
        # Re-sort after dropping zero columns.
        U2, V2, W2 = sort_columns(U2, V2, W2)
        b = decomp_to_bytes(U2, V2, W2)
        if best_bytes is None or b < best_bytes:
            best_bytes = b
            best_tuple = (U2.copy(), V2.copy(), W2.copy())
    return best_tuple, best_bytes


def effective_rank(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    """Number of nonzero columns after sorting (drops all-zero-column summands)."""
    nz = ~((U.sum(0) == 0) & (V.sum(0) == 0) & (W.sum(0) == 0))
    return int(nz.sum())


def orbit_size(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    """Count distinct decompositions in the gauge orbit of (U, V, W).

    Applies all 216 isotropy transforms composed with column sorting.
    Returns the size of the orbit (= |S_r x Iso| / |stabilizer|).
    Note: S_r is quotiented out by the sort; we count distinct
    sorted-serialized representatives under the 216 isotropy actions.
    """
    seen = set()
    for idx in range(len(ISO_ACTIONS)):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        nz = ~((U2.sum(0) == 0) & (V2.sum(0) == 0) & (W2.sum(0) == 0))
        U2 = U2[:, nz]
        V2 = V2[:, nz]
        W2 = W2[:, nz]
        if U2.shape[1] == 0:
            continue
        U2, V2, W2 = sort_columns(U2, V2, W2)
        seen.add(decomp_to_bytes(U2, V2, W2))
    return len(seen)


def stabilizer_order(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    """Order of the stabilizer subgroup in the matmul isotropy.

    Among the 216 isotropy elements, count those whose action yields
    a decomposition equal (after column sort) to the input (itself sorted).
    """
    Ub, Vb, Wb = sort_columns(U, V, W)
    nz = ~((Ub.sum(0) == 0) & (Vb.sum(0) == 0) & (Wb.sum(0) == 0))
    Ub = Ub[:, nz]
    Vb = Vb[:, nz]
    Wb = Wb[:, nz]
    Ub, Vb, Wb = sort_columns(Ub, Vb, Wb)
    key0 = decomp_to_bytes(Ub, Vb, Wb)
    count = 0
    for idx in range(len(ISO_ACTIONS)):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        nz2 = ~((U2.sum(0) == 0) & (V2.sum(0) == 0) & (W2.sum(0) == 0))
        U2 = U2[:, nz2]
        V2 = V2[:, nz2]
        W2 = W2[:, nz2]
        if U2.shape[1] != Ub.shape[1]:
            continue
        U2, V2, W2 = sort_columns(U2, V2, W2)
        if decomp_to_bytes(U2, V2, W2) == key0:
            count += 1
    return count
