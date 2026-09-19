"""Crius Campaign 0 world: the fixed hidden operations on small integer vectors.

Objects are tuples of L integers modulo B. Operation labels 0..NUM_OPS-1 are
what a Player sees; the mapping from label to transform is fixed for the
campaign and never exposed through the Player-facing interface.

See crius/DESIGN_C0.md section 2 for the rationale of each operation.
"""

from __future__ import annotations

L = 4
B = 16
NUM_OPS = 6
RESET_ACTION = NUM_OPS  # the action value that returns the object to the task start

# (label, kind, parameters) -- kind is for receipts and reports only.
OP_TABLE = (
    (0, "translation", {"delta": (1, 0, 0, 0)}),
    (1, "translation", {"delta": (0, 3, 0, 0)}),
    (2, "translation", {"delta": (0, 0, 5, 0)}),
    (3, "conditional_translation", {"even": (2, 0, 0, 7), "odd": (0, 0, 0, 1)}),
    (4, "conditional_translation", {"even": (0, 4, 0, 0), "odd": (0, 0, 0, 4)}),
    (5, "rotation", {"shift": 1}),
)

WORLD_VERSION = "c0-ops-v1"


def context(x: tuple) -> int:
    """The visible property that conditional operations depend on: parity of x[0]."""
    return x[0] % 2


def add(x: tuple, d: tuple) -> tuple:
    return tuple((a + b) % B for a, b in zip(x, d))


def apply_op(op: int, x: tuple) -> tuple:
    """Apply hidden operation `op` to object `x`. Deterministic, total on 0..NUM_OPS-1."""
    if op == 0:
        return add(x, (1, 0, 0, 0))
    if op == 1:
        return add(x, (0, 3, 0, 0))
    if op == 2:
        return add(x, (0, 0, 5, 0))
    if op == 3:
        return add(x, (2, 0, 0, 7) if context(x) == 0 else (0, 0, 0, 1))
    if op == 4:
        return add(x, (0, 4, 0, 0) if context(x) == 0 else (0, 0, 0, 4))
    if op == 5:
        return x[1:] + x[:1]
    raise ValueError("unknown op %r" % (op,))


def apply_sequence(seq, x: tuple) -> tuple:
    for op in seq:
        x = apply_op(op, x)
    return x


def hamming(a: tuple, b: tuple) -> int:
    return sum(1 for p, q in zip(a, b) if p != q)


def performance(x: tuple, target: tuple) -> float:
    """1.0 at the target, 0.0 when every coordinate differs."""
    return 1.0 - hamming(x, target) / float(L)


def world_fingerprint() -> str:
    """A hash of the hidden operation table, recorded in every receipt."""
    import hashlib
    import json

    payload = json.dumps({"L": L, "B": B, "ops": OP_TABLE, "v": WORLD_VERSION}, sort_keys=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()[:16]
