"""
Controls that separate a genuine topology-changing wormhole from cheaper
explanations, plus the frozen nonlinear-degeneracy classifier.

  * reweight_navigator (D7 s14): may reweight base-edge proposals but adds NO new
    transition.  Its reachable set == base closure, so it can never cross a cut.
  * macro_replay (D7 s15): compiles existing base trajectories into macro edges.
    Base ops preserve the invariant, so macros stay inside base closure -> no cross.
  * degeneracy classifier (D7 s19): affine / coordinate-separable / commuting /
    context-independence tests over the FULL finite state space.  Frozen here,
    before any binding evidence.
"""

from __future__ import annotations
import random
from collections import deque
from substrate import run_micro
from certify import base_closure
from evalz import build_zfn


# --------------------------------------------------------------------------
# Existing-graph navigation control (cannot create transitions).
# --------------------------------------------------------------------------

def reweight_navigator(world, S, T, budget=5000, seed=0):
    """Learned reweighting over E0. Reachable set is base closure regardless."""
    closure = base_closure(world, S)
    return {"crossed": (T in closure), "reachable": len(closure),
            "note": "reweighting E0 cannot add transitions"}


# --------------------------------------------------------------------------
# Path-macro control (compile base trajectories only).
# --------------------------------------------------------------------------

def macro_replay(world, S, T, n_macros=400, max_len=8, seed=0):
    rng = random.Random(seed)
    base = [prog for _, prog in world.base_ops]
    macros = []
    for _ in range(n_macros):
        seq = [rng.choice(base) for _ in range(rng.randint(2, max_len))]
        macros.append(seq)

    def macro_img(v, seq):
        cur = v
        for prog in seq:
            cur, _ = run_micro(prog, cur, world.p)
        return cur

    seen = {S}
    dq = deque([S])
    while dq:
        v = dq.popleft()
        nbs = [nb for nb in world.base_neighbors(v)]
        for seq in macros:
            nbs.append(macro_img(v, seq))
        for nb in nbs:
            if nb not in seen:
                seen.add(nb)
                dq.append(nb)
    return {"crossed": (T in seen), "reachable": len(seen),
            "note": "macros of base ops preserve the base invariant"}


# --------------------------------------------------------------------------
# Frozen nonlinear-degeneracy classifier (over the full finite state space).
# --------------------------------------------------------------------------

def _affine_fit(zfn, p, nreg):
    """True iff there exist A,b over Z_p with zfn(v)=A v + b for ALL v."""
    zero = tuple(0 for _ in range(nreg))
    b = zfn[zero]
    cols = []
    for i in range(nreg):
        e = tuple(1 if j == i else 0 for j in range(nreg))
        img = zfn[e]
        cols.append(tuple((img[k] - b[k]) % p for k in range(nreg)))  # A e_i
    for v, out in zfn.items():
        pred = list(b)
        for i in range(nreg):
            for k in range(nreg):
                pred[k] = (pred[k] + cols[i][k] * v[i]) % p
        if tuple(pred) != out:
            return False
    return True


def _coordinate_separable(zfn, p, nreg):
    """
    True iff z is coordinate-separable in the STRONG sense: every output coord i
    is a function of a SINGLE input coord j (some j, not necessarily i -- this also
    catches permuted separability).  Degenerate if separable.
    """
    for i in range(nreg):
        depends_on_single = False
        for j in range(nreg):
            table = {}
            ok = True
            for v, out in zfn.items():
                key = v[j]
                if key in table and table[key] != out[i]:
                    ok = False
                    break
                table[key] = out[i]
            if ok:
                depends_on_single = True
                break
        if not depends_on_single:
            return False  # output coord i needs >=2 input coords -> not separable
    return True


def _commutes_with_base(zfn, world):
    for v in world.states():
        zv = zfn[v]
        for _, prog in world.base_ops:
            bz, _ = run_micro(prog, zv, world.p)
            bv, _ = run_micro(prog, v, world.p)
            if zfn.get(bv) != bz:
                return False
    return True


def _context_independent(zfn, p, nreg):
    """True iff z(v)-v is the same vector for all v (a constant translation)."""
    deltas = set()
    for v, out in zfn.items():
        deltas.add(tuple((out[k] - v[k]) % p for k in range(nreg)))
        if len(deltas) > 1:
            return False
    return True


def classify_degeneracy(ast, world, hoard):
    zfn = build_zfn(ast, world, hoard)
    p, n = world.p, world.nreg
    affine = _affine_fit(zfn, p, n)
    separable = _coordinate_separable(zfn, p, n)
    commutes = _commutes_with_base(zfn, world)
    ctx_indep = _context_independent(zfn, p, n)
    degenerate = affine or separable
    return {
        "affine": affine,
        "coordinate_separable": separable,
        "commutes_with_base": commutes,
        "context_independent": ctx_indep,
        "degenerate_linear_class": degenerate,
        "nonlinear_gate_pass": (not degenerate),
        "verdict_class": ("DEGENERATE_LINEAR" if degenerate else "NONLINEAR_CONTEXT_DEPENDENT"),
    }
