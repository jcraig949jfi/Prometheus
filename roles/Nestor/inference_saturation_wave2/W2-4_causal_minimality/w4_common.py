"""W2-4 causal minimality: shared assays. Read-only on campaign code; imports the S1 / FOR harnesses unchanged.

Every assay is a sequence of single calls of the world's own _pair_interact (map_common.Harness: dense VM, ATOMIC
run_ds runner, CF/C7 cell, slice 300, P-11 assay, post-interaction mutation). The runner is constructed, never .run().
The harness is built with the bare ATOMIC class ("CARRY" policy) and every entry state is passed explicitly, so ZERO
here is identical to run_rs ZERO (both organisms' registers None/0/0 before the call).

Readouts for a genome m (all against fresh uniform random partners):
  Z   zero-context conversion: share of interactions in which the partner half is converted (world birth with the
      donor as parent) AND ends >= 0.9 whole-genome identity to m. Sides alternate (balanced).
  R   retention: share of the same ZERO interactions in which the donor half is NOT converted (ATOMIC keeps it).
  K   children's conversion: up to NC converted partner halves from Z (the post-interaction genome the world stores)
      each run NI ZERO interactions; share converting a partner to >= 0.9 identity to the CHILD.
  C   carried-context conversion: one chain of N interactions starting from zero; the donor's registers carried
      across its own interactions; the partner's state drawn from map_offspring.partner_pool (S1's CARRY context);
      sides random 50/50. Rate over steps 2..N.
  P2  two-step establishment: map_children's two-type extinction formula on the Z joint law (a,b,c,e) and the K
      child law (p0c,p1c,p2c):  q = (c qC + e)/(1 - a qC - b), P2 = 1 - q.
"""
from __future__ import annotations

import hashlib
import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))

import map_common as M  # noqa: E402
import map_offspring as MO  # noqa: E402

ZS = (None, 0, 0)
_H = {}
_POOL = {}
VM_OVERRIDE = [None]      # physics test: set to the stock z8 module to run the same assay on the stock VM


def harness(cell, base=False):
    key = (cell, base)
    if key not in _H:
        if base:      # BASE write-back (world.Runner: both halves written back), for the write-back test only
            orig = M.run_rs.runner
            M.run_rs.runner = lambda world, policy, prng: world.Runner
            try:
                _H[key] = M.Harness("CARRY", 778, cell)
            finally:
                M.run_rs.runner = orig
        else:
            _H[key] = M.Harness("CARRY", 777, cell)
    M.world.z8 = VM_OVERRIDE[0] or M.DENSE
    return _H[key]


def pool(cell):
    if cell not in _POOL:
        _POOL[cell] = MO.partner_pool(cell)
    return _POOL[cell]


def ident(a, b):
    return M.ident(a, b)


def assay_zero(m, cell, n, tag, nc=5, d_st=None, p_st=None, sides=(0, 1), base=False):
    """ZERO (or fixed entry state) assay. Returns dict with conv, kept, joint law, children, side conv, delivered.
    With base=True the BASE write-back runner is used and 'intact' = donor kept with >= 0.9 identity to m."""
    h = harness(cell, base)
    rng = random.Random(repr(("W4Z", tag, m.hex(), cell)))
    conv = kept = 0
    joint = {"a": 0, "b": 0, "c": 0, "e": 0}
    kids = []
    side_c = {0: [0, 0], 1: [0, 0]}
    deliv = [0] * len(m)
    for k in range(n):
        side = sides[k % len(sides)]
        pg = M.rand_genome(rng, h.n)
        ds = ZS if d_st is None else (d_st(rng) if callable(d_st) else d_st)
        ps = ZS if p_st is None else (p_st(rng) if callable(p_st) else p_st)
        x = h.interact(m, pg, side, d_state=ds, p_state=ps)
        ch = x["p_conv"] and ident(x["gp"], m) >= 0.9
        kp = x["d_kept"] and (not base or ident(x["gd"], m) >= 0.9)
        conv += ch
        kept += kp
        joint["a" if kp and ch else "b" if kp else "c" if ch else "e"] += 1
        side_c[side][0] += 1
        side_c[side][1] += ch
        if ch:
            gp = x["gp"]
            for j in range(min(len(m), len(gp))):
                if gp[j] == m[j] and pg[j] != m[j]:
                    deliv[j] += 1
            if len(kids) < nc:
                kids.append(gp)
    return {"n": n, "conv": conv / n, "kept": kept / n, "nconv": conv,
            "joint": {k: v / n for k, v in joint.items()}, "kids": kids,
            "side_conv": {s: (v[1] / v[0] if v[0] else None) for s, v in side_c.items()}, "deliv": deliv}


def assay_children(kids, cell, ni, tag):
    h = harness(cell)
    rng = random.Random(repr(("W4K", tag, cell)))
    cnt = [0, 0, 0]
    cconv = 0
    for kg in kids:
        for k in range(ni):
            side = k % 2
            pg = M.rand_genome(rng, h.n)
            x = h.interact(kg, pg, side, d_state=ZS, p_state=ZS)
            ch = x["p_conv"] and ident(x["gp"], kg) >= 0.9
            cconv += ch
            cnt[(1 if x["d_kept"] else 0) + (1 if ch else 0)] += 1
    tot = sum(cnt)
    if not tot:
        return {"n": 0, "conv": None, "law": None}
    return {"n": tot, "conv": cconv / tot, "law": [c / tot for c in cnt]}


def assay_carry(m, cell, n, tag):
    h = harness(cell)
    P = pool(cell)
    rng = random.Random(repr(("W4C", tag, m.hex(), cell)))
    st = ZS
    conv = 0
    kept = 0
    for k in range(n):
        side = rng.randrange(2)
        pg = M.rand_genome(rng, h.n)
        x = h.interact(m, pg, side, d_state=st, p_state=P[rng.randrange(len(P))])
        st = x["d_state"]
        if k >= 1:
            conv += x["p_conv"] and ident(x["gp"], m) >= 0.9
            kept += x["d_kept"]
    return {"n": n - 1, "conv": conv / (n - 1), "kept": kept / (n - 1)}


def p_est2(joint, child_law):
    a, b, c, e = joint["a"], joint["b"], joint["c"], joint["e"]
    if child_law is None:
        qc = 1.0
    else:
        p0c, p1c, p2c = child_law
        qc = 1.0 if p2c <= p0c else p0c / p2c
    den = 1 - a * qc - b
    q = 1.0 if den <= 1e-12 else min(1.0, (c * qc + e) / den)
    return 1 - q


def full(m, cell, tag, nz=40, nc_kids=5, ni=8, ncarry=40):
    z = assay_zero(m, cell, nz, tag, nc=nc_kids)
    k = assay_children(z["kids"], cell, ni, tag)
    c = assay_carry(m, cell, ncarry, tag)
    return {"Z": z["conv"], "R": z["kept"], "K": k["conv"], "C": c["conv"], "Ckept": c["kept"],
            "P2": p_est2(z["joint"], k["law"]), "nkids": len(z["kids"]), "Kn": k["n"],
            "joint": z["joint"], "side_conv": z["side_conv"], "deliv": z["deliv"], "nconv": z["nconv"]}


def ko_value(g, p, which=0):
    rng = random.Random(int(hashlib.sha256(g + bytes([p])).hexdigest()[:16], 16) ^ 20260930)
    vals = rng.sample([v for v in range(256) if v != g[p]], 3)
    return vals[which]


def knock(g, p, which=0):
    m = bytearray(g)
    m[p] = ko_value(g, p, which)
    return bytes(m)
