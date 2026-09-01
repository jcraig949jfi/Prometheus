"""
Certification lane (ORACLE / never learner-visible).

Two independent proofs of a barrier, per D7 section 3:
  (1) EXHAUSTIVE: full transitive closure of base physics from S; check T not in it.
      Because V is finite this is an exact, path-length-infinite fact (R_inf).
  (2) ALGEBRAIC INVARIANT: a linear functional f(v)=w.v (mod p) conserved by every
      base op on every state, with f(S) != f(T). This *explains* the cut.

Also provides reachability of the effective graph Gz = E0 union {v->z(v)}.
"""

from __future__ import annotations
from collections import deque
from itertools import product

from substrate import World, run_micro


def base_closure(world: World, S):
    """Full transitive closure (R_inf) of base physics from S. Returns a set."""
    seen = {S}
    dq = deque([S])
    while dq:
        v = dq.popleft()
        for nb in world.base_neighbors(v):
            if nb not in seen:
                seen.add(nb)
                dq.append(nb)
    return seen


def gz_closure(world: World, S, zfn, extra_budget_nodes=None):
    """Closure of {S} under base ops PLUS the macro edge v -> zfn[v]."""
    seen = {S}
    dq = deque([S])
    while dq:
        v = dq.popleft()
        nbs = list(world.base_neighbors(v))
        if v in zfn:
            nbs.append(zfn[v])
        for nb in nbs:
            if nb not in seen:
                seen.add(nb)
                dq.append(nb)
    return seen


def _linear_invariants(world: World):
    """
    Find all linear functionals w (mod p) conserved by every base op on every
    state: f(v)=sum_i w_i v_i, requiring f(op(v)) == f(v) for all v, all base ops.
    Returned as a list of weight-tuples (a spanning set is enough for our use).
    We solve by brute force over small weight space when p**nreg is small; for the
    proof world this is trivial and exact.
    """
    p, n = world.p, world.nreg
    states = list(world.states())
    invs = []
    # brute-force candidate weights in Z_p^n (skip all-zero)
    for w in product(range(p), repeat=n):
        if all(x == 0 for x in w):
            continue
        ok = True
        for v in states:
            fv = sum(wi * vi for wi, vi in zip(w, v)) % p
            for _, prog in world.base_ops:
                nv, _ = run_micro(prog, v, p)
                fnv = sum(wi * xi for wi, xi in zip(w, nv)) % p
                if fnv != fv:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            invs.append(w)
    return invs


def certify_cut(world: World, S, T, want_invariant=True):
    """
    Returns a certificate dict. barrier=True iff T is unreachable under base physics.
    """
    closure = base_closure(world, S)
    t_reach = T in closure
    cert = {
        "world": world.name,
        "world_fingerprint": world.fingerprint(),
        "S": list(S),
        "T": list(T),
        "reachable_count": len(closure),
        "state_space": world.p ** world.nreg,
        "T_reachable_base": t_reach,
        "barrier": (not t_reach),
        "proof": "exhaustive_closure(R_inf)",
    }
    if want_invariant:
        invs = _linear_invariants(world)
        witness = None
        for w in invs:
            fS = sum(wi * si for wi, si in zip(w, S)) % world.p
            fT = sum(wi * ti for wi, ti in zip(w, T)) % world.p
            if fS != fT:
                witness = {"weights": list(w), "fS": fS, "fT": fT}
                break
        cert["invariant_witness"] = witness
        cert["invariant_count"] = len(invs)
        if witness is not None:
            cert["proof"] = "exhaustive_closure(R_inf) + conserved_linear_invariant"
    return cert


def target_reachable_with_z(world: World, S, T, zfn):
    """Does z open a path S -> T?  (crossing test for admission criterion D)."""
    closure = gz_closure(world, S, zfn)
    return (T in closure), len(closure)
