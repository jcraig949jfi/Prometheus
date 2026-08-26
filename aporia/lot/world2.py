"""world2.py — tiny world v2. Cell-controlled construction, XOR target.

WHY THE TARGET CHANGED, and it was forced by the reviewer's own criterion rather than chosen.

v1 used a CONJUNCTIVE target, y = r00 AND NOT r01. Under the criterion
`P(r_i | y=0) ~= P(r_i | y=1)` for every primitive, a conjunction is UNSATISFIABLE:

    y = A AND NOT B  =>  every positive is the single cell (A=1, B=0)
                     =>  P(A | y=1) = 1 and P(B | y=1) = 0
                     =>  at least one conjunct always leaks totally.

No amount of resampling fixes that; it is algebra. The census caught the symptom (r08 gap
0.795) and tracing it revealed the target SHAPE was wrong, not just the generator.

    y = A XOR B  =>  positives are {(1,0),(0,1)}, negatives are {(0,0),(1,1)}
                 =>  P(A | y=1) = P(A | y=0) = 0.5, same for B
                 =>  NO primitive is marginally informative, and the signal exists ONLY in
                     the relation between two relations.

That is the composition-mandatory property in the strong sense the reviewer asked for, and
XOR is essentially the only shallow shape that has it.

CELL-CONTROLLED CONSTRUCTION, not rejection sampling on the target. v1 produced both classes
by rejecting until the target matched, which let every nuisance variable correlated with the
target's precondition ride free -- negatives were sparse graphs, so sparse-graph features
leaked. Here each of the four (A,B) cells is CONSTRUCTED to equal size, so label balance and
cell balance are exact rather than sampled.

THE TWO CHOSEN RELATIONS ARE LOGICALLY INDEPENDENT. v1's pair had r01 implying r00, which made
one occupancy cell impossible. A implies B kills a cell; independence is a design requirement,
not an accident.

    A = r00  some 2-step link exists
    B = r04  some mutual pair exists
    y = A XOR B

Both are directly controllable, which is what makes cell-controlled construction possible.
"""
from __future__ import annotations

import random
from itertools import permutations

N = 5
PAIRS = list(permutations(range(N), 2))


def _has_two_path(E):
    return any((a, b) in E and (b, c) in E for a, b, c in permutations(range(N), 3))


def _has_mutual(E):
    return any((a, b) in E and (b, a) in E for a, b in PAIRS)


def _strip_mutual(E):
    """Remove back-edges until no mutual pair remains. Touches as little as possible."""
    E = set(E)
    changed = True
    while changed:
        changed = False
        for a, b in list(PAIRS):
            if (a, b) in E and (b, a) in E:
                E.discard((b, a))
                changed = True
                break
    return E


def _strip_two_paths(E):
    """Remove edges until no 2-step link remains."""
    E = set(E)
    while _has_two_path(E):
        for a, b, c in permutations(range(N), 3):
            if (a, b) in E and (b, c) in E:
                E.discard((b, c))
                break
    return E


def make(rng, want_a, want_b):
    """Construct a graph in the requested (A, B) cell. Construction, not rejection."""
    for _ in range(500):
        E = {p for p in PAIRS if rng.random() < 0.30}
        if want_a and not _has_two_path(E):
            a, b, c = rng.sample(range(N), 3)
            E |= {(a, b), (b, c)}
        if not want_a:
            E = _strip_two_paths(E)
        if want_b and not _has_mutual(E):
            a, b = rng.sample(range(N), 2)
            E |= {(a, b), (b, a)}
            if not want_a:
                E = _strip_two_paths(E)
                if not _has_mutual(E):
                    continue
        if not want_b:
            E = _strip_mutual(E)
            if want_a and not _has_two_path(E):
                continue
        if _has_two_path(E) == want_a and _has_mutual(E) == want_b:
            return {"edges": sorted(E), "family": "G2",
                    "label": int(want_a != want_b)}      # XOR
    return None


# ── executable relations. Ugly names, family-agnostic dispatch. ─────────────

def _p(o):
    E = set(map(tuple, o["edges"]))
    return lambda a, b: (a, b) in E


def r00(o):
    p = _p(o)
    return any(p(a, b) and p(b, c) for a, b, c in permutations(range(N), 3))


def r04(o):
    p = _p(o)
    return any(p(a, b) and p(b, a) for a, b in PAIRS)


def r02(o):
    p = _p(o)
    return any(not any(p(a, b) for b in range(N) if b != a) for a in range(N))


def r03(o):
    p = _p(o)
    return any(not any(p(b, a) for b in range(N) if b != a) for a in range(N))


def r05(o):
    p = _p(o)
    return sum(1 for a, b in PAIRS if p(a, b)) > len(PAIRS) / 2


def r06(o):
    p = _p(o)
    return any(sum(1 for b in range(N) if b != a and p(a, b)) >= 2 for a in range(N))


def r07(o):
    p = _p(o)
    return any(sum(1 for b in range(N) if b != a and p(b, a)) >= 2 for a in range(N))


def r08(o):
    p = _p(o)
    return any(p(a, b) and p(b, c) and p(c, d)
               for a, b, c, d in permutations(range(N), 4))


def r09(o):
    return _p(o)(0, N - 1)


RELATIONS = {"r00": r00, "r02": r02, "r03": r03, "r04": r04,
             "r05": r05, "r06": r06, "r07": r07, "r08": r08, "r09": r09}

TARGET = ("r00", "r04")


def target_fn(o):
    return r00(o) != r04(o)          # XOR


def build(seed=20260826, per_cell=100):
    """Equal mass in all four (A,B) cells by construction."""
    rng = random.Random(seed)
    data, dropped = [], 0
    for a in (False, True):
        for b in (False, True):
            got = 0
            while got < per_cell:
                o = make(rng, a, b)
                if o is None:
                    dropped += 1
                    continue
                data.append(o)
                got += 1
    rng.shuffle(data)
    return data, dropped
