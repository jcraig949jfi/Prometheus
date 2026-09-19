"""Campaign 1 world RELAY: fixed primitive mechanics, per-stream relabeling, hidden procedure library.

Objects: tuples of L=4 integers in Z_8. Primitives (kind, pos): INC, DEC,
SWAP(pos, pos+1 mod L). A Player emits an action id in 0..11; a stream's
hidden permutation maps ids to primitives. Templates (hidden, per stream)
are lists of (kind, offset) steps applied relative to an argument
position. See crius/DESIGN_C1.md s1.
"""

from __future__ import annotations

import hashlib
import json
import random

from . import worlds

L = 4
B = 8
KINDS = ("INC", "DEC", "SWAP")
NUM_PRIMITIVES = len(KINDS) * L  # 12
NUM_ACTIONS = NUM_PRIMITIVES
RESET_ACTION = NUM_ACTIONS
WORLD_VERSION = "c1-relay-v1"


def primitive_of(index: int) -> tuple:
    """index in 0..11 -> (kind, pos)."""
    return KINDS[index // L], index % L


def index_of(kind: str, pos: int) -> int:
    return KINDS.index(kind) * L + (pos % L)


def apply_primitive(kind: str, pos: int, x: tuple) -> tuple:
    x = list(x)
    p = pos % L
    if kind == "INC":
        x[p] = (x[p] + 1) % B
    elif kind == "DEC":
        x[p] = (x[p] - 1) % B
    elif kind == "SWAP":
        q = (p + 1) % L
        x[p], x[q] = x[q], x[p]
    else:
        raise ValueError(kind)
    return tuple(x)


def apply_template(template, arg: int, x: tuple) -> tuple:
    for kind, offset in template:
        x = apply_primitive(kind, (arg + offset) % L, x)
    return x


def apply_chain(chain, x: tuple) -> tuple:
    """chain = [(template, arg), ...]"""
    for template, arg in chain:
        x = apply_template(template, arg, x)
    return x


def hamming(a: tuple, b: tuple) -> int:
    return sum(1 for p, q in zip(a, b) if p != q)


class _C1:
    B = B

    @staticmethod
    def num_actions(task) -> int:
        return NUM_ACTIONS

    @staticmethod
    def apply_action(task, action: int, x: tuple) -> tuple:
        kind, pos = primitive_of(task.perm[action])
        return apply_primitive(kind, pos, x)


worlds.register("c1", _C1)


def world_fingerprint() -> str:
    payload = json.dumps({"L": L, "B": B, "kinds": KINDS, "v": WORLD_VERSION}, sort_keys=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()[:16]


# ---------------------------------------------------------------- stream generator


def draw_library(rng: random.Random, k: int, min_steps: int = 2, max_steps: int = 3) -> list:
    """K distinct templates; no template is a single primitive and no two are equal."""
    lib = []
    seen = set()
    while len(lib) < k:
        m = rng.randint(min_steps, max_steps)
        t = tuple((rng.choice(KINDS), rng.randrange(L)) for _ in range(m))
        # normalise so the first step has offset 0 (argument = position of the first step)
        base = t[0][1]
        t = tuple((kind, (off - base) % L) for kind, off in t)
        if t in seen:
            continue
        # reject templates that are the identity on every object (e.g. INC then DEC at the same offset)
        probe = tuple(rng.randrange(B) for _ in range(L))
        if all(apply_template(t, a, probe) == probe for a in range(L)):
            continue
        seen.add(t)
        lib.append(t)
    return lib


def draw_perm(rng: random.Random) -> tuple:
    p = list(range(NUM_PRIMITIVES))
    rng.shuffle(p)
    return tuple(p)
