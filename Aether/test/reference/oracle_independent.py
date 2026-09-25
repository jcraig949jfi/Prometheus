"""
Aether AETH-00 (semantics_id aeth00.v1) -- SECOND, independent CPU oracle.

AETHER_TEST_PLAN.md test 22 ("Independent transition oracle") requires a
second reference implementation, written independently from the primary
one (oracle.py), for differential testing. To make that comparison have
genuine value this file:

- operates on a flat `bytes`/`bytearray` buffer with manual index
  arithmetic, never the nested (row, col) -> tuple grid oracle.py uses;
- computes the arbitration key inline, in a different expression shape,
  rather than calling oracle.py's splitmix64_mix/pack_coords/
  arbitration_priority helpers;
- groups contests with a single dict keyed by a packed integer rather
  than a (tuple, int) Python tuple key;
- is a single function rather than oracle.py's five-stage pipeline.

Both files necessarily implement the SAME frozen formulas (the spec
leaves no freedom there); what is independent is the code path, data
representation, and control flow, so a bug in one is unlikely to be
mechanically reproduced in the other. Read only against
Aether/AETHER_SPEC.md -- never against oracle.py -- when maintaining
this file.
"""

from typing import Dict, Tuple

_MASK64 = 0xFFFFFFFFFFFFFFFF
_SEED_XOR = 0x9E3779B97F4A7C15
_MUL_A = 0xBF58476D1CE4E5B9
_MUL_B = 0x94D049BB133111EB

WRITE_OPCODE = 0x01


def _mix(x: int) -> int:
    x &= _MASK64
    x = x ^ (x >> 30)
    x = (x * _MUL_A) & _MASK64
    x = x ^ (x >> 27)
    x = (x * _MUL_B) & _MASK64
    x = x ^ (x >> 31)
    return x & _MASK64


def _key64(hi: int, lo: int) -> int:
    return ((hi & 0xFFFFFFFF) << 32) | (lo & 0xFFFFFFFF)


def priority_of(
    seed: int, tick: int, trow: int, tcol: int, tfield: int, srow: int, scol: int
) -> int:
    """Independent expression of the same chained SplitMix64 priority as
    oracle.arbitration_priority; must never be refactored to call it."""
    a = _mix((seed & _MASK64) ^ _SEED_XOR)
    b = _mix(a ^ (tick & _MASK64))
    c = _mix(b ^ _key64(trow, tcol))
    d = _mix(c ^ (tfield & _MASK64))
    return _mix(d ^ _key64(srow, scol))


def step_bytes(H: int, W: int, seed: int, tick: int, data: bytes) -> bytes:
    """S[t] (flat bytes) -> S[t+1] (flat bytes). Raises OverflowError from
    tick == 2**64-1, ValueError on a duplicate physical source within one
    contest (defect detector, mirrors oracle.assert_no_duplicate_sources
    by an independent route: a plain seen-set scan during the single
    proposal-decoding pass, not a post-hoc grouped-dict check)."""
    if len(data) != H * W * 4:
        raise ValueError("buffer length mismatch")
    if tick == _MASK64:
        raise OverflowError("tick overflow")

    def cell_index(row: int, col: int) -> int:
        return (row * W + col) * 4

    # contests: packed (target_row, target_col, field) -> list[(srow, scol, value)]
    contests: Dict[Tuple[int, int, int], list] = {}
    seen_targets_per_source: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    for row in range(H):
        for col in range(W):
            base = cell_index(row, col)
            opcode = data[base + 0]
            if opcode != WRITE_OPCODE:
                continue
            arg0 = data[base + 1]
            arg1 = data[base + 2]
            payload = data[base + 3]
            direction = arg0 % 4
            field = arg1 % 4
            if direction == 0:
                trow, tcol = (row - 1) % H, col
            elif direction == 1:
                trow, tcol = row, (col + 1) % W
            elif direction == 2:
                trow, tcol = (row + 1) % H, col
            else:
                trow, tcol = row, (col - 1) % W
            source = (row, col)
            if source in seen_targets_per_source:
                raise ValueError(f"duplicate physical source proposal: {source}")
            seen_targets_per_source[source] = (trow, tcol, field)
            key = (trow, tcol, field)
            contests.setdefault(key, []).append((row, col, payload))

    out = bytearray(data)
    for (trow, tcol, field), entries in contests.items():
        best_prio = -1
        best_value = None
        for srow, scol, value in entries:
            prio = priority_of(seed, tick, trow, tcol, field, srow, scol)
            if prio > best_prio:
                best_prio = prio
                best_value = value
        out[cell_index(trow, tcol) + field] = best_value
    return bytes(out)
