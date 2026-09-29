"""CVT-R adapter: drives Artemis's CVT-1/2/R certificate (certs.cvt + certs.score, unchanged copy of
roles/Artemis/challenge/p11/certs.py @2af325f7b) through NPE's own VM and cell parameters.

VM / cell environment is built exactly as Nestor's corpus delegate does it (corpus_analysis.env @origin/main):
  world.z8 = run_dc.dense_z8()  if vm == "DENSE"  else the stock z8 (z80atlas-verify)
  r = world.Runner(dict(run_ds.cells()[run_dd.CELLS[cell]]["cell"], atlas_axis="NONE"), 1, tier=<arm tier>)
  n = r.L, tape = world._pow2(2n), budget = r.t["slice"], mask = r._ops_mask(), cmr = r.copy_mut
All foreign code runs from git-archive copies under ./foreign (origin/main SHA in foreign/ORIGIN_MAIN_SHA).
"""
from __future__ import annotations

import hashlib
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE / "foreign" / "roles" / "Nestor" / "campaigns"
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
PATHS = [HERE / "artemis_p11",
         CAMP / "z80atlas-verify-2026-09-22", CAMP / "c9x-explore-2026-09-24" / "x_donor_swap",
         W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", W1 / "x_dd_establish"]
for _p in PATHS:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

FRESH = (None, 0, 0)
_W = {}


def vm_module(vm):
    import z8 as z8_plain
    import run_dc
    if vm == "DENSE":
        if "dense" not in _W:
            _W["dense"] = run_dc.dense_z8()
        return _W["dense"]
    if vm == "PLAIN":
        return z8_plain
    raise ValueError("unknown vm %r" % (vm,))


def env(vm, cell):
    """(world, runner, vm module) with world.z8 set explicitly, as Nestor's scripts do."""
    import world
    import run_dd
    import run_ds
    z = vm_module(vm)
    world.z8 = z
    key = ("r", cell)
    if key not in _W:
        a = run_ds.cells()[run_dd.CELLS[cell]]
        _W[key] = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    r = _W[key]
    r.__dict__.pop("_ops_mask", None)
    return world, r, z


def params(vm, cell):
    world, r, z = env(vm, cell)
    n = r.L
    return {"n": n, "tape_len": world._pow2(2 * n), "budget": r.t["slice"], "mask": r._ops_mask(),
            "cmr": r.copy_mut, "vm_name": z.__name__}


# ------------------------------------------------------------------ P-11 (NPE's fresh-start assay, unchanged)
def p11_rates(vm, cell, g, tag, k):
    """run_dd.assay_one logic, but also per-side counts. Seeds ("X-DONOR-DISCOVERY", tag, i, side) as run_dd.
    Returns (either-side rate, side-0 rate, side-1 rate)."""
    world, r, z = env(vm, cell)
    import p11
    P = params(vm, cell)
    n = P["n"]
    hits, sides = 0, [0, 0]
    for i in range(k):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            res = p11.assay(z, n=n, tape_len=P["tape_len"], ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                            budget=P["budget"], ops_mask=P["mask"], cmr=P["cmr"], victim_side=1 - side,
                            seed=("X-DONOR-DISCOVERY", tag, i, side))
            sides[side] += res["pass"]
            ok = ok or res["pass"]
        hits += ok
    return hits / k, sides[0] / k, sides[1] / k


def q1_reproduce(g, vm, cell):
    """Exactly corpus_analysis.q1_chunk's full-mask arm: run_dd.assay_one(world, r, g, ("CORPUS-Q1", hex), 20)."""
    import run_dd
    world, r, z = env(vm, cell)
    h, _ = run_dd.assay_one(world, r, g, ("CORPUS-Q1", g.hex()), 20)
    return h / 20


# ------------------------------------------------------------------ CVT (Artemis certs.py, unchanged)
def make_step(z, n, tape_len, budget, mask, side, sid):
    """harness.step, kind == "pair", copy mutation 0: the descendant is the victim half after one interaction
    against common-random victim bytes sha256("VICTIM", sid, g, k); re-placed at the donor side next generation."""
    import p11
    from common import shabytes

    def step(G, g, k):
        vb = shabytes("VICTIM", sid, g, k, n=n)
        ga, gb = (G, vb) if side == 0 else (vb, G)
        tape, _, _, _ = p11.interact(z, n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                     budget=budget, ops_mask=mask, cmr=0.0, rng=random.Random(0))
        v0 = n if side == 0 else 0
        return bytes(tape[v0:v0 + n])
    return step


def cvt_side(z, G, n, tape_len, budget, mask, side, sid):
    import certs
    rows, _ = certs.cvt(make_step(z, n, tape_len, budget, mask, side, sid), G, sid, False)
    return certs.score(rows, n)


def cvt_genome(vm, cell, G, sid):
    P = params(vm, cell)
    _, _, z = env(vm, cell)
    if len(G) != P["n"]:
        raise ValueError("genome length %d != cell L %d" % (len(G), P["n"]))
    return {side: cvt_side(z, G, P["n"], P["tape_len"], P["budget"], P["mask"], side, sid) for side in (0, 1)}


def file_hashes():
    fs = [HERE / "artemis_p11" / "certs.py", HERE / "artemis_p11" / "common.py", HERE / "adapter.py"]
    V = CAMP / "z80atlas-verify-2026-09-22"
    fs += [V / f for f in ("p11.py", "z8.py", "world.py", "constants.py", "grammar.py", "MANIFEST_FROZEN.json")]
    fs += [CAMP / "c9x-explore-2026-09-24/x_donor_swap/run_ds.py", W1 / "x_dd_dense_copy/run_dc.py",
           W1 / "x_donor_discovery/run_dd.py"]
    return {str(f.relative_to(HERE)): hashlib.sha256(f.read_bytes()).hexdigest() for f in fs}
