"""Gauge group for polymul tensor T over F_3 with n = 3.

Generators (verified to preserve T below):

  SUB_a  — substitution x -> x + a, for a in F_3 = {0, 1, 2}.
           x -> x + 0 = identity. x -> x + 1 has order 3 over F_3
           (since 1 + 1 + 1 = 0 mod 3). The non-trivial substitutions
           form a Z_3 subgroup (additive group of F_3).
           Action: M_in[r, c] = a^{c - r} * C(c, r) mod 3 for a in F_3*.
           More directly we build via repeated multiplication of SUB_1.

  SCAL_c — scaling x -> c x for c in F_3* = {1, 2}.
           c = 1 is identity; c = 2 maps x -> 2x.
           Action on input mode: diag(1, c, c^2) = diag(1, 2, 1).
           Action on output mode: diag(1, c, c^2, c^3, c^4) = diag(1, 2, 1, 2, 1).
           Order 2 subgroup.

  REV    — index reversal x^i -> x^{n-1-i}; M_in = J_3, M_out = J_5.
           Order 2 involution.

  SWAP   — commutativity p <-> q.
           Order 2.

The closure <SUB_1, SCAL_2, REV> determines the input-side gauge size
empirically. We BFS-close generators and verify each preserves T.

Plus:
  S_r            — column permutation, quotiented by sorting columns.
  per-column F_3* — quotiented by normalize_all_columns.
"""
from __future__ import annotations
import numpy as np
from math import comb

from .core import (
    POLYMUL_T, DIM_AB, DIM_C, N, P, is_polymul_decomp, sort_columns,
    decomp_to_bytes, column_keys, normalize_all_columns,
)


# -----------------------------------------------------------------------------
# F_3 linear-algebra primitives
# -----------------------------------------------------------------------------

def _matmul_Fp(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    return ((X.astype(np.int64) @ Y.astype(np.int64)) % P).astype(np.int8)


def _inv_Fp(M: np.ndarray) -> np.ndarray:
    n = M.shape[0]
    aug = np.hstack([M.copy().astype(np.int64) % P,
                     np.eye(n, dtype=np.int64)])
    for c in range(n):
        piv = None
        for r in range(c, n):
            if aug[r, c] % P != 0:
                piv = r
                break
        if piv is None:
            raise ValueError("not invertible mod p")
        aug[[c, piv]] = aug[[piv, c]]
        inv = pow(int(aug[c, c]) % P, -1, P)
        aug[c] = (aug[c] * inv) % P
        for r in range(n):
            if r != c and (aug[r, c] % P) != 0:
                factor = aug[r, c] % P
                aug[r] = (aug[r] - factor * aug[c]) % P
    return (aug[:, n:] % P).astype(np.int8)


# -----------------------------------------------------------------------------
# Generator construction
# -----------------------------------------------------------------------------

def _pascal_a(a: int, d: int) -> np.ndarray:
    """Pascal-style matrix for substitution x -> x + a, dim d.

    P_a[j, i] = a^{i - j} * C(i, j) mod p for i >= j (else 0).

    For a=1 this is the standard Pascal matrix (binomial coefficients
    mod p) which is upper-triangular with ones on the diagonal.

    Convention: this matrix represents p_old (in old basis) -> p_new (in
    new basis), where new basis is shifted. We use it on the OUTPUT mode
    of T directly. For the INPUT modes the matrix-tensor convention
    requires (P_a^{-1})^T (matching the F_2 polymul-n3 pilot convention).
    """
    M = np.zeros((d, d), dtype=np.int64)
    for i in range(d):
        for j in range(i + 1):
            M[j, i] = (pow(a, i - j, P) * (comb(i, j) % P)) % P
    return (M % P).astype(np.int8)


def _scaling_matrix(c: int, d: int) -> np.ndarray:
    """Diagonal matrix diag(1, c, c^2, ..., c^{d-1}) mod p, representing
    the action on coefficients when x -> c x:
      p(x) -> p(c x); coefficient of x^i in p(c x) is p_i * c^i.
    For the input-mode action under our einsum convention we use the
    inverse-transpose just like for the substitution, but a diagonal
    matrix is its own transpose and inverse-of-diag is just diag of
    inverses, so input-mode is diag(1, c^{-1}, c^{-2}, ...).
    """
    return np.diag([pow(c, i, P) for i in range(d)]).astype(np.int8) % P


def _action_on_T(M_a, M_b, M_c, swap: bool) -> bool:
    T = POLYMUL_T.astype(np.int64)
    Tp = np.einsum('Ii,Jj,Kk,ijk->IJK',
                   M_a.astype(np.int64),
                   M_b.astype(np.int64),
                   M_c.astype(np.int64),
                   T) % P
    if swap:
        Tp = Tp.transpose(1, 0, 2)
    return np.array_equal(Tp.astype(np.int8), POLYMUL_T)


# Build the three non-swap generators.
# Convention (matching the F_2 polymul-3 pilot): for the substitution
# generator we use M_in = (Pascal_a^{-1})^T and M_out = Pascal_a, both
# acting under einsum 'Ii,Jj,Kk,ijk->IJK'.
_PA1_in = _pascal_a(1, DIM_AB)
_PA1_out = _pascal_a(1, DIM_C)
SUB1_in = _inv_Fp(_PA1_in).T.astype(np.int8) % P
SUB1_out = _PA1_out

# Scaling x -> 2x: M_in = M_out = diag(c^i) preserves T directly.
SCAL2_in = _scaling_matrix(2, DIM_AB)
SCAL2_out = _scaling_matrix(2, DIM_C)
J_in = np.eye(DIM_AB, dtype=np.int8)[::-1].copy()
J_out = np.eye(DIM_C, dtype=np.int8)[::-1].copy()


# Verify each preserves T.
assert _action_on_T(SUB1_in, SUB1_in, SUB1_out, swap=False), \
    "SUB1 (x -> x+1) does not preserve polymul-3 over F_3"
assert _action_on_T(SCAL2_in, SCAL2_in, SCAL2_out, swap=False), \
    "SCAL2 (x -> 2x) does not preserve polymul-3 over F_3"
assert _action_on_T(J_in, J_in, J_out, swap=False), \
    "REV does not preserve polymul-3 over F_3"


# -----------------------------------------------------------------------------
# BFS-closure of <SUB1, SCAL2, REV>
# -----------------------------------------------------------------------------

def build_gauge_actions():
    I_in = np.eye(DIM_AB, dtype=np.int8)
    I_out = np.eye(DIM_C, dtype=np.int8)

    SUB = (SUB1_in, SUB1_in, SUB1_out)
    SCAL = (SCAL2_in, SCAL2_in, SCAL2_out)
    REV = (J_in, J_in, J_out)

    def _compose(g1, g2):
        return (_matmul_Fp(g1[0], g2[0]),
                _matmul_Fp(g1[1], g2[1]),
                _matmul_Fp(g1[2], g2[2]))

    def _key(g):
        return (g[0].tobytes(), g[1].tobytes(), g[2].tobytes())

    identity = (I_in, I_in, I_out)
    seen = {_key(identity): "I"}
    closed = [(identity, "I")]
    frontier = [(identity, "I")]
    gens = [(SUB, "S"), (SCAL, "C"), (REV, "R")]

    while frontier:
        new_frontier = []
        for g, lab in frontier:
            for gen, glab in gens:
                ng = _compose(gen, g)
                nk = _key(ng)
                if nk not in seen:
                    seen[nk] = lab + glab
                    closed.append((ng, lab + glab))
                    new_frontier.append((ng, lab + glab))
        frontier = new_frontier

    # Cross with SWAP.
    actions = []
    for (g, lab) in closed:
        for swap_bit in (0, 1):
            M_a, M_b, M_c = g
            actions.append((M_a, M_b, M_c, bool(swap_bit), (lab, swap_bit)))
    return actions


GAUGE_ACTIONS = build_gauge_actions()
GAUGE_SIZE = len(GAUGE_ACTIONS)
NONSWAP_SIZE = GAUGE_SIZE // 2

# Verify: every gauge element preserves T.
for (M_a, M_b, M_c, swap, label) in GAUGE_ACTIONS:
    assert _action_on_T(M_a, M_b, M_c, swap), \
        f"gauge element {label} fails to preserve polymul-3 over F_3"


# -----------------------------------------------------------------------------
# Apply / canonicalize
# -----------------------------------------------------------------------------

def apply_gauge(U: np.ndarray, V: np.ndarray, W: np.ndarray, idx: int):
    M_a, M_b, M_c, swap, _ = GAUGE_ACTIONS[idx]
    U2 = _matmul_Fp(M_a, U)
    V2 = _matmul_Fp(M_b, V)
    W2 = _matmul_Fp(M_c, W)
    if swap:
        U2, V2 = V2, U2
    return U2, V2, W2


def canonicalize(U: np.ndarray, V: np.ndarray, W: np.ndarray):
    """Canonicalize under (input gauge x SWAP) x S_r x per-column F_3* scaling."""
    best_bytes = None
    best_tuple = None
    for idx in range(GAUGE_SIZE):
        U2, V2, W2 = apply_gauge(U, V, W, idx)
        nz = ~((U2.sum(0) == 0) | (V2.sum(0) == 0) | (W2.sum(0) == 0))
        U2 = U2[:, nz]; V2 = V2[:, nz]; W2 = W2[:, nz]
        if U2.shape[1] == 0:
            continue
        U2, V2, W2 = normalize_all_columns(U2, V2, W2)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        b = decomp_to_bytes(U2, V2, W2)
        if best_bytes is None or b < best_bytes:
            best_bytes = b
            best_tuple = (U2.copy(), V2.copy(), W2.copy())
    return best_tuple, best_bytes


def effective_rank(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    nz = ~((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    return int(nz.sum())


def orbit_size(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    seen = set()
    for idx in range(GAUGE_SIZE):
        U2, V2, W2 = apply_gauge(U, V, W, idx)
        nz = ~((U2.sum(0) == 0) | (V2.sum(0) == 0) | (W2.sum(0) == 0))
        U2 = U2[:, nz]; V2 = V2[:, nz]; W2 = W2[:, nz]
        if U2.shape[1] == 0:
            continue
        U2, V2, W2 = normalize_all_columns(U2, V2, W2)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        seen.add(decomp_to_bytes(U2, V2, W2))
    return len(seen)


def stabilizer_order(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    sz = orbit_size(U, V, W)
    if sz == 0:
        return 0
    return GAUGE_SIZE // sz
