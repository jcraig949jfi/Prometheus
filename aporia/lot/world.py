"""world.py — the tiny world. Solver-first, ugly primitives, composition-mandatory.

HARD INVARIANT (reviewer, 2026-08-26), pinned above this file:

    No primitive without a live consumer.
    primitive admitted  <=>  a current task exists on which its semantics can be
                             EXECUTED and ABLATED.

ANTI-PATTERN, also pinned:

    specification + citations + taxonomy + versioning + no causal consumer = 0 evidence.

The archaeology found a 956-line ontology that never ran. This file therefore contains no
taxonomy, no schema, no versioning protocol, and no English concept names. Primitives are
`r00..r09` on purpose -- if a name ever helps, we are measuring language-model priors rather
than symbolic computation.

MODEL, per the reviewer's reframing:

    executable relation -> useful composition -> ablation-worthy reification

not primitive -> motif -> macro, because "macro" risks becoming another noun we admire.

THE TARGET CONCEPT IS COMPOSITION-ONLY BY CONSTRUCTION. Its signal lives in
`(r_a AND NOT r_b)` -- a relation among relations -- and in no single r_i. That is what makes
the world capable of testing motif formation rather than feature detection.

TWO FAMILIES, SHARED STRUCTURE, ALIEN SURFACES:
    family G  labelled digraphs        -- "is there a 2-step link with no 1-step shortcut"
    family I  time intervals           -- same relation, no graph vocabulary anywhere

Nothing here is a concept library. It is a task population plus the executable relations a
solver may call, and it exists to be attacked by counterfeit solvers before it is believed.
"""
from __future__ import annotations

import random
from itertools import permutations

N_NODES = 5


# ── family G: labelled digraphs ─────────────────────────────────────────────

def g_make(rng, positive):
    """A digraph as a set of (i,j) edges. POSITIVE iff some 2-path a->b->c exists with
    NO direct a->c. Negatives are built to contain 2-paths that DO close, or no 2-path."""
    while True:
        edges = set()
        for i in range(N_NODES):
            for j in range(N_NODES):
                if i != j and rng.random() < 0.28:
                    edges.add((i, j))
        if _g_open_two_path(edges) == positive:
            return {"edges": sorted(edges), "label": int(positive), "family": "G"}


def _g_two_paths(edges):
    return [(a, b, c) for (a, b) in edges for (b2, c) in edges
            if b == b2 and a != c]


def _g_open_two_path(edges):
    return any((a, c) not in edges for (a, b, c) in _g_two_paths(edges))


# ── family I: time intervals. Same relation, deliberately alien surface. ────

def i_make(rng, positive):
    """Intervals on a line. 'a->b' means a ends before b starts (a precedes b).
    POSITIVE iff some a precedes b precedes c while a does NOT precede c -- which on
    intervals requires a and c to overlap. No graph words appear anywhere."""
    while True:
        iv = []
        for _ in range(N_NODES):
            s = rng.randint(0, 18)
            iv.append((s, s + rng.randint(1, 9)))
        if _i_open_two_path(iv) == positive:
            return {"intervals": iv, "label": int(positive), "family": "I"}


def _i_prec(iv, a, b):
    return iv[a][1] < iv[b][0]


def _i_open_two_path(iv):
    n = len(iv)
    return any(_i_prec(iv, a, b) and _i_prec(iv, b, c) and not _i_prec(iv, a, c)
               for a, b, c in permutations(range(n), 3))


# ── the executable relations a solver may call. Ugly names on purpose. ──────
# Each takes an object, returns a bool. Family-agnostic: they dispatch internally so a
# solver never sees which family it is in.

def _pairs(o):
    if o["family"] == "G":
        E = set(map(tuple, o["edges"]))
        return lambda a, b: (a, b) in E
    iv = o["intervals"]
    return lambda a, b: _i_prec(iv, a, b)


def r00(o):  # some 2-step link exists
    p = _pairs(o)
    return any(p(a, b) and p(b, c) for a, b, c in permutations(range(N_NODES), 3))


def r01(o):  # EVERY 2-step link has its 1-step shortcut
    p = _pairs(o)
    t = [(a, b, c) for a, b, c in permutations(range(N_NODES), 3) if p(a, b) and p(b, c)]
    return all(p(a, c) for a, b, c in t) if t else False


def r02(o):  # some element links to nothing
    p = _pairs(o)
    return any(not any(p(a, b) for b in range(N_NODES) if b != a) for a in range(N_NODES))


def r03(o):  # some element is linked from nothing
    p = _pairs(o)
    return any(not any(p(b, a) for b in range(N_NODES) if b != a) for a in range(N_NODES))


def r04(o):  # some mutual pair
    p = _pairs(o)
    return any(p(a, b) and p(b, a) for a, b in permutations(range(N_NODES), 2))


def r05(o):  # link count above half of max
    p = _pairs(o)
    n = sum(1 for a, b in permutations(range(N_NODES), 2) if p(a, b))
    return n > (N_NODES * (N_NODES - 1)) / 2


def r06(o):  # some element links to at least two others
    p = _pairs(o)
    return any(sum(1 for b in range(N_NODES) if b != a and p(a, b)) >= 2
               for a in range(N_NODES))


def r07(o):  # some element is linked from at least two others
    p = _pairs(o)
    return any(sum(1 for b in range(N_NODES) if b != a and p(b, a)) >= 2
               for a in range(N_NODES))


def r08(o):  # a 3-step chain exists
    p = _pairs(o)
    return any(p(a, b) and p(b, c) and p(c, d)
               for a, b, c, d in permutations(range(N_NODES), 4))


def r09(o):  # first element links to last
    p = _pairs(o)
    return p(0, N_NODES - 1)


RELATIONS = {"r00": r00, "r01": r01, "r02": r02, "r03": r03, "r04": r04,
             "r05": r05, "r06": r06, "r07": r07, "r08": r08, "r09": r09}

# The target, stated as a composition and NOT available as any single relation.
# This is the object a solver must discover; it is never handed to one.
TARGET = ("r00", "r01")           # r00 AND NOT r01


def target_fn(o):
    return r00(o) and not r01(o)


def build(seed=20260826, n=400):
    rng = random.Random(seed)
    G = [g_make(rng, i % 2 == 0) for i in range(n)]
    I = [i_make(rng, i % 2 == 0) for i in range(n)]
    return G, I
