"""diagnostics.py — omniscient-side exact analysis machinery.

Everything in this module sees witnesses, world internals, and inverse primitives. It is
used by (a) the generation-time family filters in worlds.py and (b) the census/experiment
harnesses. NOTHING here may be imported by solver code; the observation boundary test in
tests/ asserts that statically.
"""
from __future__ import annotations

HALF = 6            # meet-in-the-middle half-depth (min_dist dmax = 12)


def bfs_side(world, root, half, backward):
    """state -> min depth from root, to depth `half`. Validity semantics:
    forward: every entered state must be valid; backward: only expand from valid states
    (an invalid state may sit at the meet layer but can never join a forward state)."""
    depth = {root: 0}
    frontier = [root]
    fns = world.invs if backward else world.prims
    for d in range(1, half + 1):
        nxt = []
        for s in frontier:
            if backward and not world.valid(s):
                continue
            for f in fns:
                ns = f(s)
                if not backward and not world.valid(ns):
                    continue
                if ns not in depth:
                    depth[ns] = d
                    nxt.append(ns)
        frontier = nxt
    return depth


def min_dist(world, s, t, half=HALF):
    fw = bfs_side(world, s, half, backward=False)
    bw = bfs_side(world, t, half, backward=True)
    best = None
    for u, df in fw.items():
        db = bw.get(u)
        if db is not None and (best is None or df + db < best):
            best = df + db
    return best        # None means > 2*half


def enum_words(world, root, length, backward):
    """ALL words of exactly `length` (validity-pruned): endpoint-state -> [words].
    Backward words are returned forward-oriented (they run endpoint -> root)."""
    out = {}
    fns = world.invs if backward else world.prims
    word = [0] * length

    def rec(state, i):
        if i == length:
            out.setdefault(state, []).append(tuple(word) if not backward
                                             else tuple(reversed(word)))
            return
        if backward and not world.valid(state):
            return
        for p in range(4):
            ns = fns[p](state)
            if not backward and not world.valid(ns):
                continue
            word[i] = p
            rec(ns, i + 1)

    if length == 0:
        return {root: [()]}
    rec(root, 0)
    return out


def solutions_at(world, s, t, d):
    a = d // 2
    fw = enum_words(world, s, a, backward=False)
    bw = enum_words(world, t, d - a, backward=True)
    sols = []
    for u, ws in fw.items():
        tail = bw.get(u)
        if tail:
            sols.extend(wf + wb for wf in ws for wb in tail)
    return sols


def contains_word(word, sub):
    n = len(sub)
    return any(word[i:i + n] == sub for i in range(len(word) - n + 1))
