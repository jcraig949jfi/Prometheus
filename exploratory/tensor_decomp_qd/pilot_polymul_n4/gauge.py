"""Gauge group for polymul tensor T over F_2 at n = 4.

Generators (each verified to preserve T below):

  SUB    — substitution x -> x + 1.
           Action on input mode (degree n-1 = 3 polys): coordinate change so that
             tilde p(y) = p(y - 1) = p(y + 1) (mod 2)
           giving M_a[r, c] = C(c, r) mod 2 (Pascal lower-triangular in dim n).
           Action on output mode (degree 2n - 2 = 6 polys): same substitution
           in dim 2n - 1 = 7 (Pascal-(2n-1) mod 2).
           Verified: SUB is an involution and preserves T.

  REV    — index reversal. M_a = J_n (anti-diagonal), M_c = J_{2n-1}.
           Verified: involution, preserves T.

  SWAP   — commutativity p <-> q. Swaps modes 0 and 1 of T.

We BFS-close <SUB, REV> under multiplication and report |G_input| (the
non-swap subgroup). For polymul-3 (n=3) over F_2 this group was D_3 of
order 6 because of a hidden Z_3 (SUB and REV did not commute, with
composition of order 3). For n=4 we determine |G_input| empirically by
closure — the published F_2 polymul automorphism literature is sparse
on this. Documented carefully so the reader sees the closure result.

For each non-swap element, swap is paired in or out, doubling the group.
"""
from __future__ import annotations
import numpy as np
from math import comb

from .core import (
    POLYMUL_T, DIM_AB, DIM_C, N, is_polymul_decomp, sort_columns,
    decomp_to_bytes, column_keys,
)


# -----------------------------------------------------------------------------
# F_2 linear algebra primitives (Pascal, inverse mod 2)
# -----------------------------------------------------------------------------

def _pascal(d: int) -> np.ndarray:
    """Pascal matrix M[j, i] = C(i, j) mod 2."""
    M = np.zeros((d, d), dtype=np.int64)
    for i in range(d):
        for j in range(i + 1):
            M[j, i] = comb(i, j) & 1
    return M


def _inv_F2(M: np.ndarray) -> np.ndarray:
    """Inverse of an integer matrix mod 2."""
    n = M.shape[0]
    aug = np.hstack([M.copy().astype(np.int64) & 1,
                     np.eye(n, dtype=np.int64)])
    for c in range(n):
        piv = None
        for r in range(c, n):
            if aug[r, c] & 1:
                piv = r
                break
        if piv is None:
            raise ValueError("not invertible mod 2")
        aug[[c, piv]] = aug[[piv, c]]
        for r in range(n):
            if r != c and (aug[r, c] & 1):
                aug[r] = (aug[r] ^ aug[c]) & 1
    return aug[:, n:].astype(np.uint8)


# Substitution generator on input modes (dim n) and output mode (dim 2n - 1).
_M_in_pascal = _pascal(DIM_AB).astype(np.uint8)
_M_out_pascal = _pascal(DIM_C).astype(np.uint8)
_M_in_sub = _inv_F2(_M_in_pascal).T & 1
_M_out_sub = _M_out_pascal & 1

# Reversal generator (anti-diagonal).
_J_in = np.eye(DIM_AB, dtype=np.uint8)[::-1].copy()
_J_out = np.eye(DIM_C, dtype=np.uint8)[::-1].copy()


def _matmul_F2(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    return (X.astype(np.int64) @ Y.astype(np.int64) & 1).astype(np.uint8)


def _action_on_T(M_a: np.ndarray, M_b: np.ndarray, M_c: np.ndarray,
                 swap: bool) -> bool:
    T = POLYMUL_T.astype(np.int64)
    Tp = np.einsum('Ii,Jj,Kk,ijk->IJK',
                   M_a.astype(np.int64),
                   M_b.astype(np.int64),
                   M_c.astype(np.int64),
                   T) & 1
    if swap:
        Tp = Tp.transpose(1, 0, 2)
    return np.array_equal(Tp.astype(np.uint8), POLYMUL_T)


# -----------------------------------------------------------------------------
# Build full group via BFS-closure of generators
# -----------------------------------------------------------------------------

def build_gauge_actions():
    """Enumerate the gauge group by BFS-closing <SUB, REV> on the non-swap
    triples and crossing with SWAP. Each element is verified to preserve T.
    Returns: list of (M_a, M_b, M_c, swap, label).
    """
    I_in = np.eye(DIM_AB, dtype=np.uint8)
    I_out = np.eye(DIM_C, dtype=np.uint8)

    SUB = (_M_in_sub, _M_in_sub, _M_out_sub)
    REV = (_J_in, _J_in, _J_out)

    # Verify generators preserve T.
    assert _action_on_T(*SUB, swap=False), "SUB does not preserve polymul-n4 T"
    assert _action_on_T(*REV, swap=False), "REV does not preserve polymul-n4 T"

    def _compose(g1, g2):
        return (_matmul_F2(g1[0], g2[0]),
                _matmul_F2(g1[1], g2[1]),
                _matmul_F2(g1[2], g2[2]))

    def _key(g):
        return (g[0].tobytes(), g[1].tobytes(), g[2].tobytes())

    identity = (I_in, I_in, I_out)
    seen = {_key(identity): "I"}
    closed = [(identity, "I")]
    frontier = [(identity, "I")]
    gens = [(SUB, "S"), (REV, "R")]
    # BFS-closure.
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

# Validate every gauge element preserves T.
for (M_a, M_b, M_c, swap, label) in GAUGE_ACTIONS:
    assert _action_on_T(M_a, M_b, M_c, swap), (
        f"gauge element {label} fails to preserve polymul-n4 tensor"
    )


# -----------------------------------------------------------------------------
# Apply / canonicalize
# -----------------------------------------------------------------------------

def apply_gauge(U: np.ndarray, V: np.ndarray, W: np.ndarray, idx: int):
    M_a, M_b, M_c, swap, _ = GAUGE_ACTIONS[idx]
    U2 = _matmul_F2(M_a, U)
    V2 = _matmul_F2(M_b, V)
    W2 = _matmul_F2(M_c, W)
    if swap:
        U2, V2 = V2, U2
    return U2, V2, W2


def canonicalize(U: np.ndarray, V: np.ndarray, W: np.ndarray):
    """Compute canonical form under the gauge group x S_r."""
    best_bytes = None
    best_tuple = None
    for idx in range(GAUGE_SIZE):
        U2, V2, W2 = apply_gauge(U, V, W, idx)
        nz = ~((U2.sum(0) == 0) | (V2.sum(0) == 0) | (W2.sum(0) == 0))
        U2 = U2[:, nz]
        V2 = V2[:, nz]
        W2 = W2[:, nz]
        if U2.shape[1] == 0:
            continue
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
        U2, V2, W2 = sort_columns(U2, V2, W2)
        seen.add(decomp_to_bytes(U2, V2, W2))
    return len(seen)


def stabilizer_order(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    sz = orbit_size(U, V, W)
    if sz == 0:
        return 0
    return GAUGE_SIZE // sz
