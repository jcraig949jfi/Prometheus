"""Exact 4-input NPN canonicalization (all 222 equivalence classes over 65,536 functions)."""
from __future__ import annotations

import itertools
from typing import Dict, List, Tuple

import numpy as np

# Precompute the 384 (input-negation x input-permutation) row-index mappings for n=4.
# Output negation doubles that to 768 NPN symmetries.
_NPN4_ROW_MAPS: List[Tuple[int, ...]] = []
for _perm in itertools.permutations(range(4)):
    for _neg in range(16):
        _rmap = []
        for _r in range(16):
            _nr = 0
            for _j in range(4):
                _b = ((_r >> _perm[_j]) & 1) ^ ((_neg >> _j) & 1)
                _nr |= _b << _j
            _rmap.append(_nr)
        _NPN4_ROW_MAPS.append(tuple(_rmap))

_NPN4_TABLE: np.ndarray | None = None


def _build_npn4_table() -> np.ndarray:
    """Compute canonical NPN representative for every 4-input truth table 0..65535."""
    all_tt = np.arange(65536, dtype=np.uint16)
    best = np.minimum(all_tt, np.bitwise_xor(all_tt, np.uint16(0xFFFF)))
    # Vectorized over all 65,536 truth tables for each of the 384 input transforms.
    bits = [(all_tt >> r) & np.uint16(1) for r in range(16)]
    for rmap in _NPN4_ROW_MAPS:
        transformed = np.zeros(65536, dtype=np.uint16)
        for out_r, src_r in enumerate(rmap):
            if out_r == 0:
                transformed |= bits[src_r]
            else:
                transformed |= bits[src_r] << np.uint16(out_r)
        best = np.minimum(best, transformed)
        best = np.minimum(best, np.bitwise_xor(transformed, np.uint16(0xFFFF)))
    return best


def npn4_table() -> np.ndarray:
    global _NPN4_TABLE
    if _NPN4_TABLE is None:
        _NPN4_TABLE = _build_npn4_table()
    return _NPN4_TABLE


def npn4_canonical(tt: int) -> int:
    tt &= 0xFFFF
    return int(npn4_table()[tt])


def enumerate_npn4_classes() -> Dict[int, int]:
    """Return {canonical_tt: class_size} for all 222 4-input NPN classes."""
    tbl = npn4_table()
    vals, counts = np.unique(tbl, return_counts=True)
    return {int(v): int(c) for v, c in zip(vals, counts)}


# Precompute exact (perm, neg_mask) pairs matching _NPN4_ROW_MAPS order for fast inverse mapping.
_NPN4_TRANSFORMS: List[Tuple[Tuple[int, int, int, int], int]] = [
    (_perm, _neg)
    for _perm in itertools.permutations(range(4))
    for _neg in range(16)
]


def _apply_row_map(tt: int, rmap: Tuple[int, ...]) -> int:
    out = 0
    for out_r, src_r in enumerate(rmap):
        if (tt >> src_r) & 1:
            out |= 1 << out_r
    return out


def npn4_canonical_with_transform(
    tt: int,
) -> Tuple[int, Tuple[int, int, int, int], int, bool]:
    """Find (canon_tt, perm, in_neg, out_neg) such that:
        canon_tt(y0, y1, y2, y3) = tt(x0, x1, x2, x3) ^ out_neg
    where for input assignment y (row r), x_{perm[j]} = y_j ^ ((in_neg >> j) & 1).

    Equivalently, to realize `tt` on concrete wires `W = [w0, w1, w2, w3]` using a circuit
    for `canon_tt(y0, y1, y2, y3)`, feed wire `y_j = W[perm[j]] ^ ((in_neg >> j) & 1)`
    into `canon_tt`, and invert its output by `out_neg`!
    """
    tt &= 0xFFFF
    target_canon = int(npn4_table()[tt])
    for rmap, (perm, neg) in zip(_NPN4_ROW_MAPS, _NPN4_TRANSFORMS):
        tr = _apply_row_map(tt, rmap)
        if tr == target_canon:
            return (target_canon, perm, neg, False)
        if (tr ^ 0xFFFF) == target_canon:
            return (target_canon, perm, neg, True)
    raise RuntimeError(f"Failed to recover NPN4 transform for {tt:#06x}")


def compose_npn4_wire_map(
    target_tt: int,
    macro_tt: int,
) -> Tuple[Tuple[int, int, int, int], Tuple[bool, bool, bool, bool], bool] | None:
    """Given two 4-input truth tables in the same NPN class, return
    `(src_idx_for_macro_in, inv_for_macro_in, final_out_inv)` so that calling
    `macro(W[src[0]]^inv[0], ..., W[src[3]]^inv[3]) ^ final_out_inv` computes `target_tt(W)`!

    Returns None if `target_tt` and `macro_tt` are not NPN-equivalent.
    """
    c_t, p_t, n_t, o_t = npn4_canonical_with_transform(target_tt)
    c_m, p_m, n_m, o_m = npn4_canonical_with_transform(macro_tt)
    if c_t != c_m:
        return None
    # Exact row-map definition in _NPN4_ROW_MAPS:
    #   canon(y) = target(x_t) ^ o_t   where x_t[j] = y[p_t[j]] ^ n_t[j]
    #   canon(y) = macro(x_m)  ^ o_m   where x_m[i] = y[p_m[i]] ^ n_m[i]
    # Invert p_t: let inv_pt[p_t[j]] = j, so y[k] = x_t[inv_pt[k]] ^ n_t[inv_pt[k]].
    # Substitute k = p_m[i]:
    #   x_m[i] = x_t[inv_pt[p_m[i]]] ^ n_t[inv_pt[p_m[i]]] ^ n_m[i]
    # And target(x_t) = macro(x_m) ^ (o_m ^ o_t).
    inv_pt = [0, 0, 0, 0]
    for j in range(4):
        inv_pt[p_t[j]] = j
    src_idx = [0, 0, 0, 0]
    src_inv = [False, False, False, False]
    for i in range(4):
        j = inv_pt[p_m[i]]
        src_idx[i] = j
        src_inv[i] = bool(((n_t >> j) & 1) ^ ((n_m >> i) & 1))
    return (
        (src_idx[0], src_idx[1], src_idx[2], src_idx[3]),
        (src_inv[0], src_inv[1], src_inv[2], src_inv[3]),
        bool(o_m ^ o_t),
    )
