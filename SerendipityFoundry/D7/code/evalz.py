"""
Central z-evaluation.  For speed, z is evaluated ON DEMAND during the Gz BFS
(reachable states only) rather than materializing z over the whole state space.
Used by census, search (Z0/Z1), and controls so every arm shares identical
evaluation + verification machinery.

Gz = E0  union  { v -> z(v) }.  Reachability = closure of {S} under base ops
plus the single macro edge z, with unlimited invocations (z genuinely "exists").
"""

from __future__ import annotations
from collections import deque
from substrate import run_z, MicroFault, run_micro


def field_dist(a, b, p):
    d = 0
    for x, y in zip(a, b):
        e = abs(x - y) % p
        d += min(e, p - e)
    return d


def _zimg(ast, v, world, hoard, meter):
    try:
        ns, cost = run_z(ast, v, world, hoard)
    except MicroFault:
        ns, cost = v, 0
    if meter:
        meter.tick("transform_execution", cost + 1)
    return ns


def evaluate(ast, world, S, targets, hoard, meter=None, max_nodes_expand=100000):
    """
    BFS the effective graph Gz from S, computing z(v) lazily.
    Returns: reached{t:bool}, best_dist (min field dist to targets[0]),
             closure_size, writes_s(bool).
    """
    p = world.p
    seen = {S}
    dq = deque([S])
    writes_s = False
    tset = set(targets)
    reached = {t: (t == S) for t in targets}
    while dq:
        v = dq.popleft()
        nbs = world.base_neighbors(v)
        zv = _zimg(ast, v, world, hoard, meter)
        if zv[2] != v[2]:
            writes_s = True
        for nb in list(nbs) + [zv]:
            if nb not in seen:
                seen.add(nb)
                if nb in tset:
                    reached[nb] = True
                dq.append(nb)
                if len(seen) > max_nodes_expand:
                    dq.clear()
                    break
        if meter:
            meter.tick("graph_analysis", 1)
    if meter:
        meter.tick("exact_verification", len(targets))
    primary = targets[0]
    best = min(field_dist(v, primary, p) for v in seen)
    return {"reached": reached, "best_dist": best,
            "closure_size": len(seen), "writes_s": writes_s, "closure": seen}


def build_zfn(ast, world, hoard, meter=None):
    """Materialize z over the whole state space (only for degeneracy analysis)."""
    fn = {}
    for st in world.states():
        fn[st] = _zimg(ast, st, world, hoard, meter)
    return fn
